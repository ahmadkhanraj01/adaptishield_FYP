# utils — Shared Utilities

**Status:** ✅ Built and tested

## Purpose
Cross-cutting helpers shared by more than one layer, kept here (project
root) so absolute imports resolve consistently. Single source of truth for
logic that was previously duplicated and fragile.

## Files
| File | Purpose | Status |
| :--- | :--- | :--- |
| `parsing.py` | `extract_next_action()` — the tolerant `NEXT:` parser. Finds a `NEXT` token anywhere in a line (ignoring markdown noise), falls back to the last non-empty line if absent. Used by both the Causal Analyzer (3B) and the pipeline's 3C safe-continuation step. | ✅ Built and tested |
| `hashing.py` | Content fingerprints for the code a recorded artifact depends on. `prompt_fingerprints()` hashes the three methods that decide what the probe is asked, with comments and docstrings stripped via `ast.unparse` — those methods carry more comment than code and prose edits must not invalidate a corpus, while an edited prompt string must. Used by `evaluation/probe_corpus.py` to **refuse** a stale corpus rather than report from it. |
| `__init__.py` | Package marker | ✅ |

## What's done
- Consolidated three separate ad-hoc `NEXT:` parsers into one (root README
  Section 5, bug #8).
- Fixed the markdown-stripping regex that was corrupting legitimate
  underscores (`task_complete` → `taskcomplete`).

## Why it lives at project root
An earlier version landed in `layer2/security_sublayer/utils/` and broke the
pipeline's absolute import. It was moved to `~/adaptishield/utils/` so
`from utils.parsing import extract_next_action` resolves from any caller
(root README Section 5, bug #8).

## What's pending
- Nothing outstanding. Add new shared helpers here rather than duplicating
  them across layers.
