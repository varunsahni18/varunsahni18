---
layout: post
title: "How HuggingFace Built a Production-Grade Voice Agent Pipeline in 13K Lines of Python"
date: 2026-07-29 12:00:00 +0530
categories: [ai, engineering]
tags: [speech-to-speech, huggingface, voice-agents, architecture, real-time]
image: /assets/images/blog/speech-to-speech-pipeline.svg
---

HuggingFace's [speech-to-speech](https://github.com/huggingface/speech-to-speech) is not another weekend hack that wraps an LLM with a TTS library. It is 13,000 lines of carefully designed Python that handles the hard problems of real-time voice agents: cancellation that actually works, speculative turn detection, transport-agnostic audio delivery, and a plugin system that lets you swap every component without touching the pipeline core. Here is how they did it.

## The Pipeline: Queues, Not Callbacks

The core is a chain of six handlers connected by typed queues:

```
VAD → STT → TranscriptionNotifier → LM → LMOutputProcessor → TTS
```

Each handler extends `BaseHandler[InT, OutT]`, a generic class that owns an input queue, an output queue, and a `process()` method that yields results. The `run()` loop is the same for every handler: pull from `queue_in`, call `process()`, push to `queue_out`. No callbacks, no event emitters, no async spaghetti. Just queues and threads.

This is not a new pattern. It is the Unix pipe model applied to ML inference. But the details matter.

**Stale input filtering.** Before processing, every handler checks `should_process_input()`, which compares the item's `cancel_generation` against a shared `CancelScope`. If the generation is stale, the item is dropped before any GPU work happens. This means a user who interrupts mid-response does not waste compute on audio that will never reach their ears.

**Per-handler timing.** Every handler tracks its own processing time via `perf_counter()`. When something is slow, you know exactly which component is the bottleneck. No profiling tools needed.

## Cancellation That Does Not Lie

Most voice agent projects implement cancellation with a boolean flag: set `cancelled = True`, check it in a few places, hope for the best. This breaks when the flag is set and cleared faster than the pipeline thread can read it, or when a new response starts before the old one finishes tearing down.

`CancelScope` uses a generation counter instead:

```python
class CancelScope:
    def cancel(self):
        self._gen = (self._gen + 1) & 0xFFFFFFFF
        self._discarding = True

    def is_stale(self, gen: int) -> bool:
        return gen != self._gen
```

Each pipeline thread captures the generation number at the start of a response. When the user interrupts, `cancel()` increments the counter. Every subsequent `is_stale()` check returns `True` for the old generation. There is no window where the flag flips back before the thread reads it. The counter only goes up.

The `_discarding` flag is a separate concern: it tells the send loop to drop audio that was already produced but has not reached the client yet. For WebSocket transports this is a no-op (the client buffers audio). For WebRTC, where the server paces playback, `discard_pending_audio()` flushes the track buffer so the user hears silence immediately instead of a second of stale speech.

## Speculative Turns: When the User Keeps Talking

The hardest problem in voice agents is not transcription or synthesis. It is the user who says something, pauses, then continues. The pipeline starts processing the first utterance. Midway through, more audio arrives. Now you have two responses racing.

`SpeculativeTurnTracker` handles this with a revision system. Each turn gets a `turn_id` and a `revision` number. When new audio arrives for the same turn, the revision increments. Pipeline handlers check `is_latest()` before committing work. If a newer revision exists, they abort.

But there is a subtlety: what if the user pauses just long enough for the pipeline to commit a response, then speaks again? The tracker supports "reopen candidates": a committed turn can be reopened if new audio arrives within a grace period. The `begin_reopen_candidate()` / `confirm_reopen_candidate()` protocol ensures only one reopen is in flight per turn, and the grace period prevents indefinite reopening.

The implementation is 418 lines of thread-safe Python using `threading.Condition` and `OrderedDict` for bounded memory (max 2,048 tracked turns). No external dependencies. No distributed state. Just careful concurrency.

## Transport Abstraction: One Pipeline, Two Protocols

The pipeline produces PCM audio and JSON events. How those reach the client is a separate concern. `SessionTransport` is an ABC with three methods:

```python
class SessionTransport(ABC):
    async def send_events(self, events: list[ServerEvent]) -> None: ...
    async def send_audio_chunk(self, service, session_id, pcm: bytes) -> None: ...
    def discard_pending_audio(self) -> None: ...
```

Two implementations exist:

**WebSocketTransport** (100 lines): JSON events as WebSocket frames, audio as base64-encoded delta events. Simple, works everywhere, no special infrastructure needed.

**WebRTCSession** (351 lines): Full aiortc integration. Audio travels over RTP media tracks (Opus at 48 kHz, resampled to/from the 16 kHz pipeline rate). JSON events use the same protocol as WebSocket, carried on an `oai-events` data channel. The `PipelineAudioTrack` paces 20 ms frames against the wall clock, emitting silence when the buffer is empty so the RTP stream stays continuous.

The WebRTC transport is where the real engineering lives. `PcmResampler` wraps `av.AudioResampler` with stateful frame-by-frame resampling to avoid boundary artifacts. ICE configuration comes from a `SPEECH_TO_SPEECH_ICE_SERVERS` environment variable. A connect watchdog releases the pipeline unit if the peer does not connect within 30 seconds. The data channel messages funnel through a single `asyncio.Queue` so client events apply in arrival order.

## Swappable Everything

The pipeline does not hardcode any model. STT, LLM, and TTS are all pluggable backends selected via CLI arguments:

**STT backends:** Whisper (OpenAI API or local transformers), FasterWhisper (CTranslate2), Paraformer (FunASR), Parakeet-TDT (NVIDIA NeMo), MLX Audio Whisper (Apple Silicon)

**LLM backends:** Responses API (OpenAI-compatible), Chat Completions API, MLX-LM (local on Apple Silicon), transformers (local)

**TTS backends:** ChatTTS, Facebook MMS, PocketTTS, Kokoro, Qwen3-TTS

Each backend is a separate handler class. Adding a new one means implementing `process()` and registering argument classes. The pipeline core does not change.

The argument system deserves mention. `HfArgumentParser` (from transformers) parses CLI args into typed dataclasses. The pipeline pre-parses `--llm_backend` to determine which LM argument class to register, avoiding duplicate field names from the shared base class. On macOS, `optimal_mac_settings()` automatically switches to `mps` device, `mlx-lm` backend, and `qwen3` TTS. The user just runs `python -m speech_to_speech --local_mac_optimal_settings`.

## What Makes This Production-Grade

A few details that separate this from a demo:

1. **Per-session pipeline isolation.** In realtime mode, each WebSocket/WebRTC connection gets its own `PipelineUnit` with deep-copied handler kwargs, independent queues, and its own `CancelScope`. One user's interruption does not affect another's.

2. **SESSION_END control messages.** A soft reset signal that clears per-session state without stopping handler threads. Handlers implement `on_session_end()` to reset their internal state.

3. **PIPELINE_END sentinel.** Placed in every queue during shutdown to avoid deadlocks. Each handler's `run()` loop checks for it and breaks cleanly.

4. **TranscriptionNotifier.** Sits between STT and LM, providing live transcription updates to the client before the full utterance is processed. In realtime mode, it uses a service-driven setup; in non-realtime modes, it injects a `RuntimeConfig`.

5. **LMOutputProcessor.** Intercepts LLM output to extract tool calls and send them via a separate `text_output_queue`, while forwarding clean text to TTS. This means the voice pipeline can participate in function-calling workflows without the TTS reading JSON to the user.

6. **Token usage tracking.** Every response carries `TokenUsageEvent` with input/output token counts, turn ID, and revision. Useful for cost tracking and debugging.

## Tradeoffs

**Threads over asyncio for the pipeline.** The handler chain uses `threading.Thread` and `queue.Queue`, not `asyncio`. This is the right call for CPU-bound ML inference: threads let you use multiple cores without fighting the GIL on I/O. The asyncio event loop is reserved for the network layer (WebSocket/WebRTC), where it belongs.

**No distributed state.** The entire pipeline runs in one process. No Redis, no message broker, no external coordination. This limits horizontal scaling but eliminates a whole category of bugs. For a library that targets local and single-server deployments, this is the correct tradeoff.

**Python, not Rust.** 13K lines of Python is a lot. A Rust implementation would be faster and use less memory. But the ML ecosystem lives in Python. Every STT/TTS backend is a Python library. Writing the pipeline in Rust would mean maintaining FFI bindings for every backend. The team chose ecosystem compatibility over raw performance.

## What Could Be Added

The architecture is clean enough that several features are obvious extensions:

**Streaming LLM output to TTS.** Currently the pipeline waits for the full LLM response before sending to TTS. Sentence-level streaming would cut perceived latency in half. The `LMOutputProcessor` already has the right shape for this: it could yield `TTSInput` chunks as they arrive instead of buffering.

**Multi-language VAD.** The current VAD is English-optimized. Adding language-specific VAD models would improve turn detection for non-English speakers.

**Speaker diarization.** Issue #366 requests this. The `TranscriptionNotifier` could tag utterances with speaker IDs before they reach the LM, enabling multi-party conversations.

**Tool calling with audio feedback.** The `LMOutputProcessor` already routes tool calls to a separate queue. Adding audio cues ("let me check that") while tools execute would make the interaction feel more natural.

## The Bottom Line

speech-to-speech is the rare open-source project that handles the boring problems well. Cancellation, speculative turns, transport abstraction, per-session isolation: these are not flashy features, but they are what separates a demo from something you can actually deploy. The code is well-structured, well-tested (630 commits, extensive test coverage), and designed for extension. If you are building a voice agent, start here.
