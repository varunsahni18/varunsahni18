---
layout: post
title: "How Alibaba's OpenCodeReview Achieves 9x Token Savings: A Deep Dive into the Hybrid Architecture"
date: 2026-07-26
tags: [Architecture, Code Review, LLM, Go, Open Source, Alibaba]
---

When Alibaba open-sourced their internal code review tool last month, the numbers caught my attention. 12,000+ stars in weeks. Claims of "higher precision and F1 than general-purpose agents" at "~1/9 the token cost." Battle-tested across tens of thousands of developers.

Most open source releases with claims like these fall apart when you read the source code. The architecture turns out to be a thin wrapper around an LLM API with some regex sprinkled on top. So I cloned the repo and spent a weekend tracing through ~182 Go files to understand what they actually built.

The short answer: they built something genuinely interesting. The long answer is the rest of this post.

## The Problem: Why General-Purpose Agents Fail at Code Review

If you point Claude Code or Codex at a pull request and ask it to review the code, three things go wrong.

First, **token costs explode with file count**. A PR touching 20 files needs context from all 20 files for the agent to reason about them. That is O(n²) context growth. A 20-file PR at 2,000 tokens per file is 40,000 tokens just for the code, before any tool calls or conversation history. At Anthropic's pricing, that adds up fast.

Second, **agents hallucinate line numbers**. LLMs are bad at counting. Ask one to point to "line 47 of auth.go" and it will confidently tell you the bug is on line 47 when the actual code is on line 52. The diff format makes this worse: the line numbers in a unified diff are the old file's line numbers, not the new file's. Even humans get confused by this.

Third, **false positives erode trust**. A general-purpose agent flags 20 issues. 15 are real, 5 are noise. After the third false positive, the developer stops reading. The tool becomes background noise.

Alibaba's team faced all three problems at scale. Their solution was a hybrid architecture: deterministic Go code for everything an LLM gets wrong, and an LLM agent for everything deterministic code cannot do.

## The Core Insight: Per-File Isolation

The single most important architectural decision in OpenCodeReview is that **each file gets its own LLM conversation with zero shared state**.

```
PR with 20 changed files
  → 20 independent LLM conversations
  → Each conversation sees: system prompt + that file's diff + list of other changed files
  → No cross-file context sharing
```

This is the decision that makes the ~1/9 token cost possible. Linear cost scaling instead of quadratic. The tradeoff is real: the agent cannot catch bugs that span multiple files. A function call in `auth.go` that passes arguments in the wrong order to a function defined in `db.go` will slip through. The agent reviewing `auth.go` sees the call site but has no visibility into the function signature.

The architecture document is honest about this: "No cross-file reasoning. Every file is reviewed in its own LLM conversation."

For Alibaba's scale, the tradeoff was worth it. Most bugs in large codebases are local to individual files. The 9x cost reduction from isolation outweighs the missed cross-file issues. But it is a real limitation, and one you should understand before adopting the tool.

## The Three-Zone Memory Compressor

Per-file isolation solves the cross-file cost problem. But what about long conversations within a single file? A complex file might need 15 rounds of tool calls. Each round adds a user message, an assistant message, and tool results. The context window fills up.

OpenCodeReview's answer is a three-zone memory compression system in `internal/llmloop/compression.go`:

```
messages = [frozen(2)] + [compress zone] + [active zone (K most recent rounds)]
```

**Frozen zone**: The first 2 messages. These are the system prompt (instructions, rules, tool definitions) and the initial user message (the diff being reviewed). These never get compressed. They contain the core context the agent needs to do its job.

**Compress zone**: Older conversation rounds. When triggered, the LLM summarizes these into `<previous_review_summary>` tags that get appended to the user message. The original messages are dropped. The agent still knows what it found earlier, just not the exact back-and-forth.

**Active zone**: The K most recent complete rounds that fit within `(0.80 × MAX_TOKENS) - reservedTokens`. A "round" is one assistant message plus its tool result messages. These stay in full.

The compression has two triggers:

- **60% of MAX_TOKENS (58,888)**: Kicks off async background compression. The main loop keeps running. The compression result gets swapped in when ready.
- **80%**: Runs compression synchronously. The loop pauses until it finishes. This is the emergency brake.

The practical effect: a single file review can theoretically run forever, bounded only by the LLM's ability to summarize its own work. In practice, the tool-call budget (30 rounds for diff mode, 60 for scan mode) provides a hard cap.

## The Six-Layer False Positive Defense

This is where the "higher precision than general-purpose agents" claim lives. OpenCodeReview has six distinct layers that filter out bad findings before they reach the developer.

### Layer 1: REVIEW_FILTER_TASK

After the main review loop finishes for a file, all collected comments are sent back to the LLM with the original diff. The prompt asks: "Which of these comments are provably incorrect based solely on the diff?" The LLM returns a JSON array of comment IDs to remove.

This is an LLM critiquing its own work. It catches things like: the agent flagged a "missing null check" on a variable that was already null-checked three lines above (visible in the diff context), or suggested a fix that would break the build because it misunderstood the type system.

The filter is best-effort. Errors are logged and silently ignored. If the filter crashes, all comments pass through unfiltered rather than losing real findings.

### Layer 2: Line Number Resolution (Two-Pass)

The LLM calls `code_comment` with `existing_code`, a string snippet of the problematic code. The deterministic resolver in `internal/diff/resolver.go` does a sliding-window consecutive match of normalized lines against the diff hunks.

It tries the new side first (context + added lines with absolute line numbers), then the old side (context + deleted lines), then falls back to scanning the full new file content. Normalization strips leading `+`/`-`, trims whitespace, and skips blank lines.

A second pass runs over all comments after the agent loop finishes, catching any comments that were missed or re-located.

### Layer 3: RE_LOCATION_TASK

When text-based matching fails, the system asks the LLM to regenerate a more precise `existing_code` snippet from the diff. It retries the line resolution with the new snippet. If it still fails, `start_line` stays 0, marking the comment as unanchored.

### Layer 4: Path Override

The model sometimes hallucinates a file path. The tool execution layer in `internal/llmloop/loop.go` always overrides the path with the current file being reviewed. The agent cannot accidentally comment on the wrong file.

### Layer 5: DEDUP_TASK (Scan Mode)

In scan mode, where the same pattern might appear across multiple files, a dedup pass groups near-duplicate comments. The implementation has safety guarantees: every input ID must appear exactly once in the output groups. Unknown IDs, duplicate assignments, or missing IDs cause the entire dedup result to be rejected and the originals kept.

### Layer 6: Tool-Call Discipline

The system prompt instructs the model to limit context-gathering to 2-3 tool calls per finding, batch multiple comments in a single `code_comment` call, and call `task_done` immediately when finished. This is not a technical filter, but it reduces the noise that comes from an agent over-investigating and generating speculative findings.

## Where the LLM Wins and Where It Does Not

The "hybrid" in "hybrid architecture" is not marketing. There is a clean split between what runs in Go and what runs through the LLM.

**Deterministic (Go code, no LLM):**

| Stage | File | What It Does |
|-------|------|-------------|
| Diff parsing | `internal/diff/parser.go` | Regex-based unified diff to structured objects |
| File filtering | `internal/agent/preview.go` | 5-gate check: binary, exclude, include, extension, default path |
| Rule resolution | `internal/config/rules/system_rules.go` | 4-layer priority: custom, project, global, system |
| Line number matching | `internal/diff/resolver.go` | Sliding-window match against diff hunks |
| Token counting | `internal/llm/client.go` | Embedded tiktoken BPE data, no network calls |
| Path override | `internal/llmloop/loop.go` | Prevents hallucinated file paths |

**LLM-driven:**

| Stage | When | Tools |
|-------|------|-------|
| PLAN_TASK | Per file, skipped if < 50 changed lines | None (read-only tool list as text) |
| MAIN_TASK | Per file, tool-use loop | 6 tools: task_done, code_comment, file_read, file_find, file_read_diff, code_search |
| REVIEW_FILTER_TASK | After main loop per file | None |
| RE_LOCATION_TASK | When line resolution fails | None |
| DEDUP_TASK | Per batch after all files (scan only) | None |
| PROJECT_SUMMARY_TASK | After all batches (scan only) | None |

The pattern is consistent: anything involving counting, matching, filtering, or path resolution runs in Go. Anything involving semantic understanding runs through the LLM. The Go code handles what LLMs are bad at. The LLM handles what Go code cannot do.

![OpenCodeReview Architecture: Hybrid Pipeline](/assets/images/blog/open-code-review-architecture.svg)

## The 12 Cost Optimizations, Ranked by Impact

The ~1/9 token cost claim is not from one technique. It is the compound effect of twelve optimizations. Here they are, roughly in order of impact:

1. **Per-file isolation**: Linear O(n) cost scaling instead of O(n²). This is the biggest single factor.

2. **Three-zone memory compression**: Older conversation rounds summarized instead of sent in full. Keeps per-file conversations bounded.

3. **Anthropic prompt caching**: System prompt and tool definitions cached server-side via `CacheControl` ephemeral parameters. These are the largest static parts of every request.

4. **OpenAI Responses API prompt caching**: Per-file UUID session IDs enable cache bucket sharing across turns within one file's agent loop.

5. **Plan phase skip**: Files with fewer than 50 changed lines skip PLAN_TASK entirely. One fewer LLM call per small file.

6. **Pre-flight token guards**: Files exceeding 80% of MAX_TOKENS are skipped before any LLM call. No wasted API requests on files that would overflow the context window anyway.

7. **Batch strategy (scan mode)**: `by-language` grouping keeps same-language files adjacent in time, improving prompt-cache hit rates.

8. **Pre-run cost estimation**: `internal/scan/estimate.go` projects token usage before scan starts. Warns if estimate exceeds budget.

9. **Embedded BPE tokenizer**: tiktoken BPE data embedded in the binary. No network calls for token counting.

10. **Tool-call budget**: Hard cap at 30 rounds (diff) or 60 rounds (scan) per file. `code_search` capped at 100 results with 10-second timeout.

11. **Dedup reduces downstream cost**: DEDUP_TASK reduces comment count, which reduces PROJECT_SUMMARY_TASK input size.

12. **Compact comment rendering**: Summary comments truncated to ~280 characters.

## What Is Missing: No Fix Verification

This is the most honest part of the architecture. OpenCodeReview does not run tests, static analysis, or compilation to verify proposed fixes. The only verification is the LLM self-critique via REVIEW_FILTER_TASK.

The architecture document states: "Sub-agent failures are isolated, not retried. Retries belong in the wrapping CI pipeline, not the agent."

This means the tool can suggest a fix that does not compile. It can suggest a fix that passes the type checker but breaks the test suite. It can suggest a fix that looks correct in isolation but introduces a regression in another module.

Whether this matters depends on your workflow. If you use OpenCodeReview as a first-pass filter before human review, the lack of fix verification is acceptable. The human reviewer catches bad suggestions. If you want fully automated review with verified fixes, this tool is not there yet.

## Should You Use It?

OpenCodeReview is not a general-purpose agent. It is a specialized tool that makes specific tradeoffs:

- **Per-file isolation** means 9x cheaper reviews but no cross-file bug detection
- **LLM self-critique** means fewer false positives but no execution-based fix verification
- **Extension-based language support** means 71+ file types work out of the box but there are no language-specific AST analyzers
- **Go CLI with VS Code extension** means it fits into existing workflows but requires some setup

If your PRs are large, your team is cost-sensitive, and you are okay with a tool that catches local bugs and leaves cross-file reasoning to humans, OpenCodeReview is worth trying. The architecture is well thought out, the code is clean, and the tradeoffs are documented honestly.

If you need cross-file analysis, verified fixes, or deep language-specific checks, you will need something else. Or you will need to run OpenCodeReview alongside a traditional static analysis tool and treat it as one layer in a defense-in-depth strategy.
