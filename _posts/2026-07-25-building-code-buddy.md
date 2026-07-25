---
layout: post
title: "Building Code Buddy: A Multi-Agent GenAI Code Review Platform at Qualcomm"
date: 2026-07-25
tags: [LLM, Multi-Agent, Code Review, GenAI, Qualcomm]
---

At Qualcomm, I had the opportunity to architect **Code Buddy**, a multi-agent GenAI code-review platform that's now deployed across 4,000+ repositories and serves 12,000+ engineers. Here's the story of how we built it, the architecture decisions that mattered, and what we learned along the way.

## The Problem

Qualcomm's codebase is massive — spanning thousands of repositories across modem firmware, AI/ML stacks, Linux kernel drivers, and application layers. Code reviews were a bottleneck. Engineers spent hours waiting for reviews, and senior reviewers were overwhelmed. We needed a system that could:

1. **Scale** across 4,000+ repos with different languages and conventions
2. **Be accurate** — false positives erode trust fast
3. **Be actionable** — not just flag issues, but suggest fixes
4. **Integrate** with existing Gerrit/Git workflow

## Architecture: Detect-Then-Fix Agents

The core insight was separating **detection** from **fixing**. A single monolithic agent trying to do both produced mediocre results. Instead, we built a pipeline of specialized agents:

### 1. The Orchestrator

A tool-calling orchestrator agent receives the code diff and decides which specialized agents to invoke. It uses a lightweight classifier to route the review to the right set of agents based on file type, change size, and context.

### 2. Reviewer Agent

The reviewer agent performs static-analysis-style checks — but with LLM reasoning. It catches:
- Logic errors and off-by-one bugs
- Memory leaks and use-after-free (critical for C/C++ modem code)
- API misuse and contract violations
- Concurrency issues (race conditions, deadlocks)

### 3. Test-Author Agent

For every detected issue, the test-author agent generates a corresponding test case. This ensures fixes are verifiable and prevents regressions.

### 4. Security Agent

A dedicated security agent scans for:
- Buffer overflows and format string vulnerabilities
- Integer overflow/underflow
- Unvalidated input paths
- Privilege escalation vectors

### 5. The Guardrail

Before any fix is posted, it must pass a **static-analysis guardrail** — a deterministic check that the fix doesn't introduce new warnings. This is the safety net that lets us deploy with confidence.

## The Retrieval Layer

One of the biggest challenges was giving agents enough context without blowing up the prompt window. A typical code review might touch files that reference symbols across dozens of other files.

We built a **Tree-sitter symbolic retrieval layer** that:

- Parses the changed files with Tree-sitter to extract symbol references
- Walks a ccls/ctags dependency graph to find definitions and callers
- Caches symbol lookups with TTL-based invalidation
- Feeds only the relevant context into the agent's prompt

This cut review-retrieval latency dramatically and improved precision by giving agents exactly the context they needed — no more, no less.

## Results

The numbers speak for themselves:

- **2M+ automated code reviews** delivered
- **180,000+ reviews per month**
- **114,000+ engineer-hours saved per month**
- Deployed across **4,000+ repos** for **12,000+ engineers**

## Lessons Learned

1. **Specialized agents beat monolithic ones.** Each agent does one thing well. The orchestrator's job is coordination, not review.

2. **Guardrails are non-negotiable.** An LLM that posts bad fixes loses trust instantly. The static-analysis guardrail is our safety net.

3. **Context retrieval is the secret sauce.** The quality of the agent's output is directly proportional to the quality of the context you feed it. Tree-sitter + ctags was the right call for a C/C++ heavy codebase.

4. **Benchmark everything.** We built prompt-evaluation harnesses on golden datasets to measure precision/recall across model upgrades. Without this, you're flying blind.

5. **Start small, scale fast.** We launched with 50 repos and iterated for 3 months before scaling to 4,000+. The early feedback loop was invaluable.

---

*This is the first in a series of posts about building AI systems at scale. Next up: how we built an autonomous agent that triages modem hotline escalations end-to-end.*
