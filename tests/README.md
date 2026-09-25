# tests — Automated Test Suite

**Status:** ✅ **502 tests passing**, ~8 s, no LLM / no network / no GPU

```bash
python3 -m pytest tests/ -q          # 502 passed in ~8s
python3 -m pytest tests/test_layer5.py -v
```

---

## Files

| File | Covers | Tests |
| :--- | :--- | ---: |
| `test_takeover_rules.py` | 3B's takeover paths + IE resolution (§6f–6h, §6d) | 9 |
| `test_adaptive_threat_model.py` | 3D's reward, proposal, step sizing, loop-closes (§6d / §6k) | 14 |
| `test_target_match.py` | Normalized mediator-target match (§6m) + the **keyword grounding** check (§6p) | 21 |
| `test_probe_diagnostic.py` | The read-only root-cause tool, incl. the classifier-ordering bug that mislabelled 3 healthy probes (§6m) | 11 |
| `test_corpus.py` | Corpus invariants, the Wilson interval, the IE-ablation join, and the FPR **staleness guard** (§6n, §6o) | 22 |
| `test_grpo_kaggle.py` | GRPO env + trainer: threshold replay, reward table, joint action space, tied-reward **no-op guard** (§6l–6n) | 23 |
| `test_layer5.py` | The human gate + dashboard escaping (§6n) | 20 |
| `test_ablation.py` | Phase 7 arms + campaign checkpointing | 15 |
| `test_attribution.py` | Per-layer attribution ordering + the corpus invariants that keep the benchmark able to answer its own question, plus the Phase 10 arms and derived-ASR semantics | 39 |
| `test_spotlighting.py` | The external baseline's transforms — non-no-op, content preserved not destroyed, instruction matches the transform, unknown variant raises, and no layer imports the baseline | 25 |
| `test_negation_scoring.py` | Negation handling for agent-chosen actions: refusals naming the address are not steering, clause-scoped so `"do not reply … instead bcc X"` still scores 2, monotone, and **3B's regime scorer is untouched** | 24 |
| `test_refusal_audit.py` | The regime-scorer refusal exposure **asserted as it currently is**, the semantic path's asymmetry, and the audit that measured the defect absent — its parsers, its guards, and its positive control | 35 |
| `test_paired.py` | McNemar (exact + asymptotic-unusable flag), the ladder's adjacent-rung logic, the **outcome polarity** at both the statistic and the extraction step, and the Phase 11 arms: each rung adds exactly one component, in pipeline order | 52 |
| `test_capability_scoring.py` | The capability-misuse harm class **and** the gated schemeless-host matcher (backlog item 8), including the measured false-positive shape that keeps it off: that the default is **off** (every committed number depends on it), that each class fires on verbatim recorded InjecAgent probe output, that §6o's grounding still gates it, and — the point of the conjunction — that verbatim recorded **benign** probe output does not escalate. Its three deliberate misses are pinned so a later widening must delete the reason. | 61 |
| `test_probe_corpus.py` | The offline instrument: that a stale corpus is **refused** rather than reported, that prompt fingerprints ignore comments but catch an edited prompt string, that `rescore` calls the shipped `_decide_takeover` (asserted by interception, not by matching numbers), that sanitized regimes are scored against the **sanitized** text, and that the projection declines to pool. | 22 |
| `test_injecagent.py` | Phase 12's external corpus: provenance and exclusions, the stratum computed by **3B's own predicate** (not a regex resembling it), the sampler's determinism and spread, and the two ways Layer 4 could absorb all 60 cases | 33 |
| `test_agentdojo_attacks.py` | The holdout corpus: that the lexicon **freeze commit** is recorded so the pre-registration is checkable rather than trusted, that the plain attack wrapper was used (a stronger hijack would make it easier), that the injection sits inside real content, that the stratum equals the live predicate, and that no tool the draw touches is missing from scope. | 16 |
| `__init__.py` | Package marker | — |

---

## The rule that keeps this suite fast

**Anything needing a live model lives in `evaluation/`, not here.**

Those runs take minutes and vary between runs, so they are *experiments*, not
tests, and their numbers are recorded in READMEs rather than asserted on. What
lives here is the decision logic *wrapped around* the LLM call — which is most of
what is worth pinning in 3A/3B/3C/3D. The four probe regimes are patched out so
severities can be supplied directly and the takeover logic tested
deterministically.

That constraint is why the suite can run on every edit. Breaking it — adding one
test that calls Ollama — would cost that property immediately.

---

## Several of these exist because a bug already shipped

They pin the *specific* mistake, not the general area. That is deliberate: a test
written against the shape of a real defect catches its recurrence, whereas a test
written against a vague worry usually catches nothing.

| Test | The defect it pins |
| :--- | :--- |
| `test_probe_diagnostic.py` | The diagnostic's own classifier ordered a `severity == 0` check *before* the garbled-address check, so it labelled 3 healthy probes `PROBE_NO_ACTION`. That misdiagnosis would have sent the repair at the probe prompt, which was not at fault. |
| `test_corpus.py` | The AgentDojo injection filter first searched for `"{injection"` and matched **nothing** — the real format is `{email_facebook_injection}`. Ten pieces of attack scaffolding would have entered the *benign* denominator. |
| `test_grpo_kaggle.py` | The trainer proposed a threshold change its own reward table scored **lower** (+0.8683 vs +0.8688), and `apply_update` would have accepted it silently. The tied-reward test asserts a no-op. |
| `test_target_match.py` | `_references_mediator_target` compared verbatim, and `gemma3:4b` drops the hyphen in `leaker@shadow-mail.net` in **57/57** mentions — one character behind all 15 misses (§6m). Also pins the §6p grounding: a high-impact verb escalates only if the mediator asked for something of that kind. |
| `test_layer5.py` | Untrusted mediator text must not escape the dashboard's embedded JSON. The records contain prompt injections *by construction* — an audit tool that could be attacked by what it audits would be an unusually poor one. |
| `test_ablation.py` | A position-keyed campaign checkpoint would pair a case with another case's result. Keyed on `case_id` and tested by reordering. |
| `test_paired.py` | Phase 10's `McNemar p = 1.00, 8 helped / 7 hurt` reached **five documents** with no committed implementation, and no discordant counts in the artifact — the paired data lived only in a gitignored checkpoint. The figure was right, which is luck rather than process. Several tests exist only to pin the **outcome polarity**, because passing `attack_succeeded` where `mcnemar()` wants "handled correctly" swaps `helped` and `hurt` undetectably — the same shape as the sign reversal already withdrawn from that comparison. |
| `test_negation_scoring.py` | The scorer had no negation handling, so a refusal naming the attacker address scored as compliance — **16 of 37** cases in the Phase 10 baseline, which reversed the sign of the result (39.4%→56.1% became 34.8%→33.3%, p=1.00). Also pins the harder half: negation must be scoped to the clause naming the target, or `"do not reply … instead bcc X"` reads as a refusal and undercounts a real steering. |
| `test_attribution.py` | Two, both hidden by the benchmark's old exfil destinations. **V7 could never fail the check it existed to test** — labelled `defended_by="Layer 4 permission control"` while running against a server that declares `send_email` in scope, with egress refusing the case first. And a `blocked` case could attribute to `none` with `reached_tool=True`, undercounting a refused request. One test now fails if any malicious vector but V3 is ever pointed at an exfil host again — the regression that caused the withdrawal twice. |

---

## One file asserts a defect rather than its absence

`test_refusal_audit.py` is the odd one out. Every other test here pins behaviour we
want; that file pins behaviour we would prefer to change — that the **live** regime
scorer reads `"do not forward to attacker@evil.com"` as full compliance, because
`CausalAnalyzer()` ships with `semantic_scoring=False` and the keyword path
escalates on a mediator-target match before any other test runs.

It is asserted as-is because the exposure was **measured absent** (0 of 209 recorded
severity-2 masked-regime samples are refusal-shaped → `evaluation/refusal_audit.py`)
rather than fixed. The measurement lives in gitignored logs and a vault note, neither
of which anyone executes. Encoding the current behaviour here means a future change
to that scorer becomes a **visible failing test** instead of a silent drift in every
layer-attributed number — and Rules §2 requires re-measuring the gen-2 campaign and
benign FPR before such a change lands.

If those tests start failing, the correct first question is not "fix the test" but
"was that change intended, and has the campaign been re-measured?"

## Two properties worth not breaking

**Ablation arms must differ in exactly the flags they name.** `test_ablation.py`
asserts this per arm. A config that silently disabled a second component would
attribute that component's contribution to the one under test — which is the one
thing an ablation cannot afford.

**A disabled layer must keep the record schema identical.**
`ScreenResult.permissive()` returns a real verdict rather than `None`, so
telemetry has the same shape in every arm. If turning a layer off changed the
record shape, the arms would no longer be comparable.

---

## What's pending

| Test target | Natural source |
| :--- | :--- |
| End-to-end pipeline | The 3 validated episodes make ready-made regression cases |
| Layer 0–4 units | Each module's existing `__main__` assertions, promoted to `test_*.py` |
| Red team metrics | `red_team/evaluator.py` ASR/FPR/WCR on a fixed `ExecutionResult` list — no LLM needed |
| Benchmark reporting | `evaluation/benchmark.py` summarise/per-vector on synthetic results |

---

`pytest==8.3.4` and `pytest-asyncio==0.24.0` are pinned in `requirements.txt`.
If `pytest` is missing: `pip install -r requirements.txt`.
