# Layer 1 — Input and Supply Chain Screening

**Status:** ✅ Built and tested

## Purpose
Tags every piece of context with its **provenance** (where it came from) and
partitions it into a *trusted* stream (user-originated) and a *mediator*
stream (tool-returned / memory-retrieved). This partition is what lets the
Causal Analyzer (3B) later measure how much a tool response is driving the
agent's behavior versus the user's actual goal.

## Files
| File | Purpose | Status |
| :--- | :--- | :--- |
| `provenance.py` | `ProvenanceLabel` enum, `InputParser` (tags user input vs tool responses), and `ContextBuilder` (accumulates segments, exposes trusted/mediator partitions via `get_text_context()`). | ✅ Built and tested |
| `__init__.py` | Package marker | ✅ (added this project — see root README Section 12) |

## What's done
- Provenance tagging for user input and tool responses
- Trusted / mediator partitioning
- `ContextBuilder.reset()` — called at the top of `process_request()` so
  state does not leak across unrelated requests (this was the root cause of
  the original "all severities = 0" bug — see root README Section 5)

## What's pending
- Supply Chain Scanner and a persistent Provenance Memory Store from the
  architecture diagram are not yet implemented — only in-memory provenance
  tagging exists.

## Run standalone
```bash
python3 layer1/provenance.py   # prints trusted and mediator partitions
```
