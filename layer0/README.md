# Layer 0 — MCP Transport and Server Trust

**Status:** ✅ Built and tested

## Purpose
The lowest layer of AdaptiShield. Establishes whether an MCP server can be
trusted *before* any of its tool responses are allowed into the pipeline.
Guards against rug-pull attacks (a server that silently changes its
capabilities/URL after being trusted) and name-squatting.

## Files
| File | Purpose | Status |
| :--- | :--- | :--- |
| `server_trust_registry.py` | Registers servers with a SHA-256 signature over `name+url+version+capabilities`; `verify_server()` re-computes and detects mismatches (rug-pull). Also exposes `get_allowlist()` used by the Layer 4 egress filter. | ✅ Built and tested |
| `__init__.py` | Package marker | ✅ |

## What's done
- Server registration + signature computation
- Rug-pull detection (signature mismatch → `False`)
- Allowlist export consumed by `layer4/network_egress_filter.py`

## What's pending
- Transport Integrity Verifier, Schema Validator, and Name Squatting Guard
  named in the architecture diagram are **not yet separate modules** — only
  the Server Trust Registry exists so far.

## Run standalone
```bash
python3 layer0/server_trust_registry.py   # expect: legitimate=True, rug-pull=False
```

See root `README.md` Section 4 for overall build status.
