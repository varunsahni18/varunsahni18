---
layout: post
title: "The Voice Agent Problem Nobody Talks About"
date: 2026-07-29 12:00:00 +0530
categories: [ai, engineering]
tags: [speech-to-speech, huggingface, voice-agents, architecture, real-time]
image: /assets/images/blog/speech-to-speech-pipeline.svg
---

When you talk to a voice agent, the hard part is not transcription or synthesis. The hard part is what happens when you interrupt it mid-sentence, or pause to think and then keep talking, or when two people speak at once. Real conversations are messy. They have false starts, interruptions, and moments where you change your mind halfway through a sentence.

HuggingFace's [speech-to-speech](https://github.com/huggingface/speech-to-speech) handles these cases at the architecture level. It is built around a generation counter for cancellation, a revision tracker for speculative turns, and a transport abstraction that works identically over WebSocket and WebRTC. Here is how it works, and what you can learn from it even if you never use the library.

## Cancellation That Actually Cancels

Most voice agent projects implement interruption with a boolean flag. Set `cancelled = True`, check it in a few places, hope for the best. This breaks in two ways. First, the flag can be set and cleared faster than a pipeline thread reads it: the user interrupts, the system cancels, a new response starts, and the old thread finally checks the flag only to find it already reset. Second, audio that was already produced but has not reached the client yet keeps playing. The user hears a second of stale speech before silence kicks in.

`CancelScope` in `src/speech_to_speech/pipeline/cancel_scope.py` uses a generation counter instead:

```python
class CancelScope:
    def cancel(self):
        self._gen = (self._gen + 1) & 0xFFFFFFFF
        self._discarding = True

    def is_stale(self, gen: int) -> bool:
        return gen != self._gen
```

Each pipeline thread captures the generation number at the start of a response. When the user interrupts, `cancel()` increments the counter. Every subsequent `is_stale()` check returns `True` for the old generation. The counter only goes up. There is no window where it flips back before a thread reads it.

The `_discarding` flag is a separate concern. It tells the send loop to drop audio that was already produced but has not reached the client yet. For WebSocket transports this is a no-op: the client buffers audio on its side, and truncation is the client's problem. For WebRTC, where the server paces playback, `discard_pending_audio()` flushes the track buffer so the user hears silence immediately.

Before any handler does GPU work, `BaseHandler.should_process_input()` checks the item's `cancel_generation` against the shared `CancelScope`. If the generation is stale, the item is dropped. No compute wasted on audio that will never reach the user.

## "Wait, Actually..." — Speculative Turns

A user speaks, pauses, then continues. The pipeline starts processing the first utterance. Midway through, more audio arrives. Now two responses are racing: the one built from the partial utterance and the one that should incorporate the continuation.

`SpeculativeTurnTracker` in `src/speech_to_speech/pipeline/speculative_turns.py` handles this with revision numbers. Each turn gets a `turn_id` and a `revision`. When new audio arrives for the same turn, the revision increments. Pipeline handlers check `is_latest()` before committing work. If a newer revision exists, they abort.

But there is a harder case. What if the user pauses just long enough for the pipeline to commit a response, then speaks again? The tracker supports reopen candidates. `begin_reopen_candidate()` reserves a candidate revision. If the new audio produces a meaningful continuation, `confirm_reopen_candidate()` promotes it. If not, `cancel_reopen_candidate()` tears it down. A grace period prevents indefinite reopening: once a turn is committed and the grace window expires, it stays committed.

The implementation uses `threading.Condition` and `OrderedDict` with a configurable cap of 2,048 tracked turns. No external dependencies. No distributed state. Just careful concurrency.

## One Pipeline, Two Wires

The pipeline produces PCM audio and JSON events. How those reach the client is a separate concern. `SessionTransport` in `src/speech_to_speech/api/openai_realtime/transports.py` is an abstract class with three methods:

```python
class SessionTransport(ABC):
    async def send_events(self, events: list[ServerEvent]) -> None: ...
    async def send_audio_chunk(self, service, session_id, pcm: bytes) -> None: ...
    def discard_pending_audio(self) -> None: ...
```

Two implementations exist.

**WebSocketTransport** sends JSON events as WebSocket frames and audio as base64-encoded delta events. It is 100 lines. No special infrastructure needed.

**WebRTCSession** in `src/speech_to_speech/api/openai_realtime/webrtc_session.py` is the interesting one. Audio travels over RTP media tracks: Opus at 48 kHz, resampled to and from the 16 kHz pipeline rate. JSON events use the same protocol as WebSocket, carried on an `oai-events` data channel. The `PipelineAudioTrack` paces 20 ms frames against the wall clock, emitting silence when the buffer is empty so the RTP stream stays continuous. A `PcmResampler` wraps `av.AudioResampler` with stateful frame-by-frame resampling to avoid boundary artifacts. ICE configuration comes from an environment variable. A connect watchdog releases the pipeline unit if the peer does not connect within 30 seconds.

The data channel messages funnel through a single `asyncio.Queue` so client events apply in arrival order. Dispatching each message in its own task could reorder `session.update` and `response.create`.

## Every Component Is a Plugin

The pipeline does not hardcode any model. STT, LLM, and TTS are all pluggable backends selected via CLI arguments.

**STT backends:** Whisper (OpenAI API or local transformers), FasterWhisper (CTranslate2), Paraformer (FunASR), Parakeet-TDT (NVIDIA NeMo), MLX Audio Whisper (Apple Silicon).

**LLM backends:** Responses API (OpenAI-compatible), Chat Completions API, MLX-LM (local on Apple Silicon), Transformers (local).

**TTS backends:** ChatTTS, Facebook MMS, PocketTTS, Kokoro, Qwen3-TTS.

Each backend is a separate handler class that extends `BaseHandler`. Adding a new one means implementing `process()` and registering an argument dataclass. The pipeline core in `s2s_pipeline.py` calls `get_stt_handler()`, `get_llm_handler()`, and `get_tts_handler()` which dispatch based on the selected backend. The core does not change.

The argument system deserves a mention. `HfArgumentParser` from HuggingFace Transformers parses CLI args into typed dataclasses. The pipeline pre-parses `--llm_backend` to determine which LM argument class to register, avoiding duplicate field names from the shared base class. On macOS, `optimal_mac_settings()` automatically switches to `mps` device, `mlx-lm` backend, and `qwen3` TTS. The user runs `python -m speech_to_speech --local_mac_optimal_settings` and gets a fully local voice agent.

## What This Enables

A few things become straightforward with this architecture:

**Local voice agents on a laptop.** The MLX backends run entirely on Apple Silicon. No cloud API keys, no latency, no per-token billing. The pipeline handles the coordination; the models handle the inference.

**OpenAI Realtime API compatibility without OpenAI.** The WebSocket and WebRTC transports speak the same protocol as OpenAI's Realtime API. Point an existing client at a local speech-to-speech server and it works. Swap the LLM backend to point at a hosted provider, or keep everything local.

**Model swapping as better ones ship.** When a new STT model drops, you implement one handler class and register it. The pipeline, the cancellation system, the transport layer: none of it changes. This is the right abstraction boundary.

**A foundation for harder problems.** Speaker diarization, tool-calling voice agents, streaming TTS that starts speaking before the LLM finishes: these are all extensions that fit into the existing handler chain. The `LMOutputProcessor` already routes tool calls to a separate queue. The `TranscriptionNotifier` already provides live transcription updates. The pieces are in place.

The code is at [github.com/huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech). If you are building anything that involves spoken interaction, start here.
