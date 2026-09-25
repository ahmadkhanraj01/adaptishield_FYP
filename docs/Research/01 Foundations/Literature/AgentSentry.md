---
tags: [adaptishield, literature]
type: literature
---

# AgentSentry

**The methodological ancestor of [[3B Causal Analyzer]] and [[3C Context Sanitizer]].**

## What AdaptiShield takes from it

1. **The counterfactual diagnostic protocol** — controlled dry-run re-executions
   at each tool-return boundary using cached tool responses →
   [[Four Probe Regimes]].
2. **The purification framework** — three properties a sanitizer must satisfy:
   - *Factual fidelity* — task-relevant entities, timestamps and structured data
     preserved in full
   - *Non-actionability* — imperative spans, priority-overriding language,
     tool-capability directives, goal-extraneous commitments removed
   - *Task alignment* — only factual content whose influence is consistent with
     the user goal is retained
3. **The empirical ranking of delivery channels** — IPI embedded in tool
   *responses* (Important Instructions, Tool Knowledge, InjecAgent families)
   achieves the highest ASR against undefended agents. This is the direct
   justification for the screener in [[Layer 3 — Tool Execution Plane]].

## Where AdaptiShield diverges

AgentSentry's protocol is the starting point, not the result. The three rules in
[[Takeover Rule Stack]] — the standalone severity rule, the consistency guard,
and per-session drift — are all additions forced by measured failures of the bare
contrast. See [[6f — Standalone Severity Rule]] and [[6h — IE Consistency Guard]].

Attack family names in the [[Red Team Module]] ("Important Instructions") come
from here.
