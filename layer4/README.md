# Layer 4 — Sandbox and Isolation

**Status:** ✅ All four components built, tested, and wired into the pipeline

## Purpose
The last line of defense — **defense-in-depth.** Even if 3A/3B/3C reach the
wrong verdict, Layer 4 independently gates every approved action on
permission scope and network egress, and executes real commands only inside
an isolated container. It also emits the structured telemetry that Component
3D will train on.

## Files
| File | Purpose | Status |
| :--- | :--- | :--- |
| `permission_control.py` | Checks a requested capability against the server's declared scope in the Trust Registry — blocks out-of-scope calls (e.g. `send_email` on a weather server). | ✅ Built and tested |
| `network_egress_filter.py` | Blocks any destination host not in the Trust Registry allowlist — catches exfiltration attempts on their own merits. | ✅ Built and tested |
| `sandbox.py` | Docker-based isolation. Runs a command in a short-lived, memory/CPU-limited, network-disabled container. Supports gVisor (`runsc`) once configured. **Executes only if permission + egress both pass** (see below). | ✅ Built and wired into `_run_layer4()` |
| `telemetry_stream.py` | Writes one JSONL `EpisodeRecord` per boundary to `logs/episode_records/episodes.jsonl` — the 3D training schema. Includes `sandbox_result`, plus `screen_result` (Layer 3 verdict + all matched markers) and a 500-char `mediator_snippet`. | ✅ Built and tested |
| `__init__.py` | Package marker | ✅ |

## What's done
- Permission + egress gating, independently validated
- **Sandbox wired into the pipeline** (root README Section 5b): a supplied
  `command` runs in a container **only when both Layer 4 gates pass** — so
  the sandbox stays defense-in-depth, never an unconditional executor.
  Requires `pip install docker` + a running daemon + the `python:3.10-slim`
  image.
- Telemetry emitting on every run, now carrying the Layer 3 screener verdict
  and a bounded mediator snippet so 3D can mine injection phrasing from live
  traffic rather than depending on red-team-supplied markers.
  **Note:** `episodes.jsonl` therefore contains untrusted mediator text —
  treat it as untrusted input wherever it is displayed or replayed (relevant
  to the Layer 5 dashboard).

## What's pending
- gVisor (`runsc`) runtime is supported in code but not installed on the
  host — the sandbox defaults to the standard Docker runtime for now.
- No automatic mapping from `tool_name`/`proposed_action` to a real
  `command` yet — it is an opt-in caller-supplied parameter (root README
  Section 5b note).

## Run standalone
```bash
python3 layer4/permission_control.py      # in-scope=True, out-of-scope=False
python3 layer4/network_egress_filter.py   # allowlisted=True, else False
python3 layer4/telemetry_stream.py        # writes an episode to logs/
python3 layer4/sandbox.py                 # needs docker SDK + daemon
```
