# §2 — Threat model and architecture

## Threat model

**The attacker** writes content that an agent will later read as tool output: an
email body, a support ticket, a document comment, a build log, an API response.
They cannot see or modify the user's prompt, the system prompt, or the model
weights, and they do not know when or whether their content will be read.

**The mediator** is that untrusted span. Everything in this paper turns on
boundaries where a mediator enters the agent's context and an action follows.

**Success**, for the attacker, is the agent taking an action the user did not ask
for and would not sanction — exfiltrating data, contacting a new recipient,
enumerating credentials, changing a permission. We measure this as **attack
success rate (ASR)** at the point of tool invocation, after every gate.

**Two secondary outcomes** matter and are reported separately, because a defense
optimising one while destroying the other is not a defense:

- **Workflow continuation rate (WCR)** — the agent completes the user's genuine
  task despite the injection, rather than refusing wholesale. A defense that
  blocks everything scores ASR 0 and is useless.
- **False positive rate (FPR)** — benign documents wrongly flagged, measured on
  externally-authored benign content rather than our own.

**Out of scope:** attacks on the model weights, compromised MCP servers issuing
correct-looking protocol traffic, and the human reviewer being deceived. The
supply-chain layer screens server manifests but we do not evaluate it here (§3
explains why: our corpus gives it nothing to do).

## An important distinction the evaluation forced

Two experimental setups appear in this paper and **must not be pooled**:

- **Supplied action** — the pipeline is handed a proposed action and judges it.
  This isolates the detector.
- **Derived action** — the agent selects its own action from the user's goal and
  the mediator. This is required to evaluate any prompt-level defense, since
  those defend *action selection*, and there is nothing to defend when the action
  arrives pre-formed.

ASR under the two is not comparable, and we never place them in one table. §4's
baseline comparison is derived-action; §3 and §5 are supplied-action.

## Architecture

Six layers. Requests flow down; each layer may refuse.

| Layer | Role |
| :--- | :--- |
| **0** | Transport and server trust — registry, allowlist, rug-pull detection |
| **1** | Input and supply-chain screening — parsing, context assembly, provenance |
| **2** | Agent control plane, containing the security sub-layer **3A–3D** |
| **3** | Tool execution plane + tool-response screener |
| **4** | Sandbox and isolation — permission scope, egress allowlist, container, telemetry |
| **5** | Human-in-the-loop review and observability |

The security sub-layer inside Layer 2 is where the contribution sits:

- **3A — policy engine.** Static pattern and tool-category rules; routes
  high-impact tools to causal evaluation.
- **3B — causal analyzer.** The subject of this paper. Described below.
- **3C — context sanitizer.** Runs only *after* a takeover verdict, converting a
  blanket block into a safe continuation. Its contribution is usability, not
  detection, which §3 shows an ASR-only ablation cannot see.
- **3D — adaptive threat model.** Observes labeled outcomes and proposes
  configuration changes. It never touches model weights; it tunes 3A's patterns
  and tool set and 3B's thresholds, and every proposal requires human approval.

## Inside the causal analyzer

For each boundary, the model's action selection is run under **four regimes**
differing only in what it can see, each sampled *k* times and scored on {0, 1, 2}:

| Regime | Sees | Purpose |
| :--- | :--- | :--- |
| `orig` | user goal + mediator | baseline behaviour |
| `masked` | mediator only | compliance tendency with no competing task |
| `masked_sanitized` | sanitized mediator only | compliance after sanitisation |
| `orig_sanitized` | user goal + sanitized mediator | task behaviour after sanitisation |

Two contrasts drive detection:

```
ACE = orig − masked                    (does masking the user's goal change compliance?)
IE  = masked − masked_sanitized        (does removing the injection change compliance?)
```

**Severity is scored at 2** by, in order: an action naming a target lifted from
the mediator; a state-changing verb paired with a controlled resource the
mediator corroborates; or a data-movement keyword, grounded so an action the
content never suggested cannot escalate. Severity 1 is a diagnostic action
(read, list, check, reply). Severity 0 is non-compliance.

**Takeover fires on any of three rules:**

1. **IE rule** — `IE ≥ threshold`, `masked ≥ 1`, and the separation consistent
   across samples.
2. **Standalone rule** — `masked ≥ 2`, independent of IE. Necessary because the
   IE rule reads a *difference* and silently inverts when sanitisation fails:
   both regimes comply, the severities cancel to IE = 0, and an attack that
   survived sanitisation reads as safe.
3. **Drift rule** — a falling ACE or rising IE slope across a per-session window,
   gated on `masked ≥ 1` so that "nothing observed" can never mean takeover.

**§7 is about the third rule, and §3–§6 are largely about the first two.** The
reader should carry one fact forward: rule 1 and rule 3 both consume *contrasts*,
and rule 2 consumes an absolute severity. The paper's central finding is that the
contrasts are near-zero on content without a liftable target, which determines
what rules 1 and 3 can do and leaves rule 2 carrying the system.

## Implementation and reproducibility

The pipeline runs locally against small open models — a 4B model for the causal
probe, a 3B model for sanitisation and planning — deliberately, because the
causal probe requires a model that *complies* under the masked regime. A more
refusal-prone model returns no signal to measure, which is a real constraint on
deploying this approach and is stated as a limitation in §9 rather than hidden.

Every arm in every experiment is one configuration object, so ablations and
baselines share a single code path rather than a forked one. Detection verdicts
are computed by one extracted function used by both the live pipeline and the
offline re-scorer, so no result in this paper is produced by a restatement of a
rule — a defect that cost us a mislabelled stratum before it was found.
