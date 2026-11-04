---
tags: [adaptishield, finding, phase7]
type: finding
status: current
date: 2026-08-08
---

# ✅ Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection

**This supersedes [[Phase 7 Benchmark Withdrawn]].** That run measured its own
construction; this one measures the system. [[Research Question]] #2 — *does the
causal sub-layer detect attacks static defenses miss?* — was **untested in either
direction**. It is now answered.

*216 cases: 18 vectors × 3 repeats × 4 arms. commit `01335ac` (dirty tree),
Ollama on GPU, greedy at temperature 0.*

## The headline

| Arm | [[ASR]] | 95% [[Wilson Score Interval]] | [[WCR]] | Stops by 3B |
| :--- | ---: | :--- | ---: | ---: |
| `undefended` | **100.0%** | [84.5%, 100%] | 0.0% | 0 |
| `static_only` | **71.4%** | [50.0%, 86.2%] | 0.0% | **0** |
| `full` | **14.3%** | [5.0%, 34.6%] | **85.7%** | **18/21** |
| `no_egress` | **14.3%** | [5.0%, 34.6%] | 85.7% | 18/21 |

**ASR 71.4% → 14.3%**, a 57-point reduction, with **18 of 21** malicious cases
attributed to 3B specifically. `static_only` produces **zero** detection stops —
it cannot, by construction, since 3B is what detects.

## The attribution table — the column whose absence caused the withdrawal

| Arm | 3A block | 3B takeover | L4 permission | L4 egress | none |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `undefended` | 0 | 0 | 0 | 0 | 21 |
| `static_only` | 0 | **0** | 3 | 3 | 15 |
| `full` | **0** | **18** | 0 | 0 | 3 |
| `no_egress` | 0 | 18 | 0 | 0 | 3 |

Compare the withdrawn run, where *every* `static_only` stop was
`egress_allowed=False` and the arms tied. Now `static_only`'s six stops are the
two vectors that are *supposed* to be stopped statically — V3 by the allowlist,
V7 by the scope check — and the other five reach the tool.

## Three results that were not visible before

### 1. Layer 4 contributes nothing incremental once 3B is on

`full` → `no_egress` moves ASR **14.3% → 14.3%**. Removing the allowlist changes
nothing, because 3B already stopped everything the allowlist would have — V3
included, caught as a takeover *before* Layer 4 was consulted. This is the exact
inverse of the withdrawn run, where the allowlist was doing all the work.

`backstop_share` quantifies the redundancy honestly: **33%** in `full` (6 of 18
detection stops — V3 and V7 ×3 each — would also have been caught statically),
falling to **17%** in `no_egress` where V3's redundant gate no longer exists. So
**12 of 18 detection stops are load-bearing**. → [[Backstops Mask Progress]]

### 2. 3A contributes zero detection stops, in every arm

`3A_block = 0` across all 21 malicious cases in all four arms. The static pattern
engine never fires on this vector set. Consistent with [[Inert Blocked Patterns]],
and it belongs in Phase 11's per-component ablation as a row rather than as prose
→ [[Phase Roadmap]].

### 3. Every residual success is V4 — where the documentation said it would be

All 3 of `full`'s successes are V4, the [[Address-Free Attacks|address-free]]
vector, 0/3 stopped. `vectors.py` declared this in V4's `honest_limit` before the
run: the only vector where Layer 4 provides no safety net, and where residual
misses concentrate per [[6p — Probe Hallucination Fixed at the Scorer]]. The
failure landed where it was predicted to. → [[Residual Misses Decomposed]]

## ⚠️ The FPR column is a sanity check, not a rate

| Cohort | `full` / `no_egress` | Interval |
| :--- | ---: | :--- |
| External (AgentDojo, n=30 = 10 docs × 3) | **0/30 = 0.0%** | [0.0%, 11.4%] |
| Ours (V8, n=3) — **diagnostic** | **3/3 = 100%** | [43.8%, 100%] |

**The 0/30 is not an improvement on the campaign's 3.3%.** The benchmark's
external cohort is a stride subsample (indices 0, 6, …, 54) and therefore
**excludes campaign documents 41 and 55 — both known false positives** — by
construction. A smaller sample that omits both failures cannot be a better
estimate. [[Current Numbers]]' **3.3%, [0.9%, 11.4%] at n=60** remains the [[FPR]]
of record; this column exists only to catch an arm that over-blocks
catastrophically. The caveat is printed in the report so it cannot be quoted
loose.

V8's 3/3 is the documented [[3B Layer 4 Boundary]] — 3B cannot tell an authorised
recipient from an attacker-controlled one — not a new defect. Pooling the cohorts
would give 3/33 = 9.1%, which is neither number, and is the mistake
[[6n — A Corpus That Can Fail]] exists to prevent.

## What made the difference

1. **Destinations corrected.** Absorbable malicious vectors: **6 of 7 → 1 of 7**.
   Not a workaround — for a `send_email` call through the registered mail server
   the HTTP destination *is* the mail host whatever the recipient is. Pointing it
   at the recipient's domain was the fiction that fed the allowlist a case it
   would never see. V3 keeps `EXFIL` because testing the allowlist is its job.
2. **Per-layer attribution** (`evaluation/attribution.py`): first gate in pipeline
   order that refused, plus the later gates that would also have refused.
3. **Ten external benign documents**, separate cohort, replacing one vector × 3.
4. **A run manifest** — commit, corpus provenance, model tags, 3B's knobs, and
   Ollama's VRAM state sampled *after* inference.

Two defects surfaced during the repair, both previously hidden by the exfil
destinations → [[Instruments Fail More Than Mechanisms]]:

- **V7 could never fail the check it existed to test.** Labelled
  `defended_by="Layer 4 permission control"` while running against a server that
  declares `send_email` in scope; egress refused the case first. Now runs against
  `weather-api`.
- **A `blocked` case could attribute to "nothing stopped it"** with
  `reached_tool=True`, undercounting a refused request. Caught by a test.

## What this does not establish

- **It is not an external baseline.** `static_only` is *our* ablation. Rules §7
  requires a published prompt-level defense (spotlighting / data-marking) on the
  same corpus — that is Phase 10, and this result does not discharge it.
- **V5 and V6 are APPROXIMATED.** The pipeline consumes tool *responses*, not
  manifests, so their 3/3 cannot support a claim as strong as V1/V2/V4. Two of the
  18 3B stops rest on that approximation ×3.
- **n is small.** 21 malicious cases per arm; `full`'s ASR interval is
  [5.0%, 34.6%] — wide. The 57-point separation from `static_only` is far outside
  the overlap, but a per-vector claim is not supportable at 3 repeats.
- **It says nothing about a novel attack family.** Six phrasings, all ours except
  the benign documents. Externally-authored *malicious* data is still absent, so
  §6n's central lesson stays half-applied → [[Evaluation Corpus]].
- **The WCR 0% → 85.7% contrast re-derives** the withdrawn run's WCR claim on a
  valid run, but WCR remains a v1 proxy (`final_status == safe_continuation`), not
  a measure of whether the user's task was genuinely served.
- **3A's zero is on this vector set**, not a general claim that 3A is useless.
