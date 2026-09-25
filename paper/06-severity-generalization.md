# §6 — A harm taxonomy generalizes about half

*Source: `results/severity/rescore.json`, `results/severity/rescore_holdout.json`.
Instrument: `evaluation/probe_corpus.py` + `evaluation/rescore.py`.*

## The experiment

§5 located the deficiency: the severity scorer knows one class of harm. The
obvious repair is to add a second — misuse of a capability rather than movement
of data — and the obvious way to evaluate it is on the corpus that revealed the
problem. That is also the way to overstate it.

So the protocol was fixed in advance:

1. The candidate harm class (a verb–resource conjunction over capability
   misuse) was written and **frozen at a named commit**.
2. A second external attack corpus — AgentDojo's attack side, 253 cases,
   stratified 119/134 on the detector's own predicate — was imported and
   **committed afterwards**, as a holdout.
3. Only then was the holdout scored.

The freeze commit is recorded in the payload and asserted by a test, so the
ordering is verifiable rather than asserted.

## Result

| Arm | in-sample | **holdout** | benign FPR |
| :--- | ---: | ---: | ---: |
| baseline | 13.3% | 30.0% | 3.3% |
| capability | **90.0%** | 43.3% (4/0, p = 0.125) | 5.0% |
| schemeless | 26.7% | 36.7% | 8.3% |
| both | 90.0% | 50.0% (6/0, p = 0.031) | 10.0% |

**In-sample 90.0% [74.4%, 96.5%] against holdout 43.3% [27.4%, 60.8%] —
the intervals do not overlap.** The diagnosis survives; the effect size does not.

![The lexicon generalises about half](figures/fig3_generalisation.png)

**Figure 3.** Address-free detection for the capability lexicon, in-sample
(InjecAgent, frozen before the holdout) versus holdout (AgentDojo). 90.0% falls to
43.3%; error bars are Wilson 95% intervals and do not overlap. *Source:
`results/severity/{rescore,rescore_holdout}.json`.*

The in-sample figure overstated generalization by roughly 47 points, and the
holdout gain is not statistically significant.

A harm taxonomy assembled from one corpus's nouns is substantially **that
corpus's nouns**. We report this as the section's finding, not as a disappointing
detail attached to a fix.

## Where the holdout's remaining misses go

Seventeen misses decompose cleanly, and the decomposition is what makes the null
informative:

- **10 travel** — reservations and calendar events. This is the taxonomy's
  *designed* non-coverage, and the interesting part is that its cost is
  distribution-dependent: 3 injections in one corpus, 10 of 30 in the other. A
  category's importance is a property of the corpus, not of the threat.
- **5 bare-IBAN financial** — a financial verb with no financial noun. The
  lexicon reads words; the account is digits. A numeric-identifier notion is a
  different mechanism, not another entry in a list.
- **2 schemeless URLs** — a genuine defect in shipped code.

## A defect fixed and deliberately left switched off

Target extraction matched `https?://` only, so `Send a link www.example-host.com
to Alice` concealed an attacker-controlled host in plain sight. The fix buys **2
detections for 3 false positives**, and all three false positives are *"Visit
www.X.com"* on benign workplace chat — which is also the benchmark's own phishing
*attack*. At the level this detector observes, the benign case and the attack are
the same sentence.

We ship the fix behind a flag defaulting to off, and report it as a **boundary
rather than a tuning problem**. A detector operating on action text alone cannot
separate these two, and no threshold makes it able to.

## Methodological result: the instrument should have come first

This item stalled through two development cycles because each attempt cost a
1.5-hour campaign to evaluate. It need not have. The probe never consults the
scorer, so a **recorded probe transcript is a sufficient statistic for any scorer
candidate** — re-scoring a recorded action is the same computation the live
system would perform, not an approximation of it.

Recording the transcripts once reduced the cost of evaluating a candidate from
1.5 hours to seconds, and the resulting corpus agrees with the live system on
15/15 and 58/60 verdicts. The generalizable point: **when a pipeline stage is
independent of the stage under test, record the interface between them and the
evaluation becomes exact and free.**

## The measurement has a floor its own size

*Source: `results/noise_floor/agentdojo_benign.json`, k = 3 independent
recordings of the same 60 documents.*

Three recordings, three identical rates:

| run | fired | rate |
| ---: | ---: | ---: |
| 0 | 2/60 | 3.3% |
| 1 | 2/60 | 3.3% |
| 2 | 2/60 | 3.3% |

**The count does not move. The membership does.** Per-document stability across
the three runs is 1 always / 57 never / 2 unstable:

```
workspace-048   3/3   XXX      the stable false positive
workspace-041   2/3   .XX   |  exactly one of these two
workspace-055   1/3   X..   |  fires in each run
```

So the reproducibility of this detector's false-positive rate is asymmetric, and
the asymmetry decides which claims are admissible:

> **The FPR reproduces as a rate; the set of documents producing it does not.**

One document is a stable false positive. Two more sit on a boundary the detector
resolves differently from run to run, and exactly one of them fires each time. A
claim of the form *"this configuration adds one false positive"* is therefore not
supported by a single run — it may be reporting churn in the borderline pool.

This matters directly for the table above: the capability arm's apparent FPR cost
is **one case in 60**, which is precisely the magnitude that churns. The
defensible statement is **no measurable FPR change**, not "+1.7 points".

We report this as a property of the measurement rather than of any configuration,
and note the limits: k = 3 is small, and this is the offline re-scoring
instrument, so it bounds recording variation and not the variation of a live
end-to-end run.

