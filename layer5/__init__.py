"""
Layer 5 — Human-in-the-Loop & Observability.

Four components, split by whether they read or write:

  Audit Dashboard          read   `audit_report.py` -> one self-contained HTML file
  Policy Inspection        read   (same file)
  Audit Logs               read   (same file)
  Manual Override          WRITE  `governance.py` + `review.py`

The split is deliberate. The three read-only components are a rendering problem
and are best served by a single file with the data embedded: no server, no build
step, no process to keep alive, and it can be attached to a report. The fourth
mutates a live security control, so it gets a command-line flow and an
append-only decision log instead of a button — a browser control on a local
server has nothing authenticating it, which is not a property one wants in the
approval path of a security system.
"""
