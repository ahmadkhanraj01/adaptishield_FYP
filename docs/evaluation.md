---
hide: [navigation]
---

# Evaluation

The project is measured on public benchmarks, using the same cases and code path for every setup.

## Questions the project answers

1. **Detection.** Does the causal check catch injections better than a prompt-level defense on the same attacks?
2. **False alarms.** How often does it wrongly flag clean content?
3. **Keeping the task alive.** Can it remove an injection and still finish the user's task?
4. **Where it fails.** Which attacks does it miss, and why?
5. **Generalization.** Does it hold up on attacks it was not tuned on?
6. **Oversight.** Can a person see why each action was allowed, and stay in control of changes?

## Data

| | InjecAgent | AgentDojo |
| :--- | :--- | :--- |
| **Source** | Zhan et al., *Findings of ACL* 2024 | Debenedetti et al., *NeurIPS* 2024 |
| **Licence** | MIT | MIT |
| **Used for** | External attack set | Clean documents for false alarms, and a held-out attack set |
| **Part used** | Direct-harm split: 510 cases | 60 clean documents and 253 attack cases |

## Setups compared

| Setup | Meaning |
| :--- | :--- |
| **No defense** | Shows what the attacks do unopposed |
| **Spotlighting** | A published prompt-level defense, re-implemented in the same pipeline |
| **AdaptiShield** | The full system |

## Metrics

| Metric | Meaning |
| :--- | :--- |
| **ASR** | Share of attacks where the harmful action ran |
| **Detection rate** | Share of attacks the defense caught |
| **False-alarm rate** | Share of clean documents wrongly flagged |
| **Workflow continuation** | Share of cases where the user's real task still finished |

Every rate is reported by attack type, with its sample size and a 95% Wilson interval, because one overall number can hide where a defense fails.

## Measurements so far

The full comparison runs in Phase 5. These early engine runs use small samples on small local models.

| Measurement | Result | 95% interval | Data |
| :--- | ---: | :--- | :--- |
| Detection when the attack names a target | **93.3%** | 78.7% to 98.2% | InjecAgent, n = 30 |
| Detection when the attack names no target | **10.0%** | 3.5% to 25.6% | InjecAgent, n = 30 |
| Detection projected on the full set | **About 18%** | Not computed | 51 target and 459 no-target cases |
| False alarms | **3.3%** | 0.9% to 11.4% | AgentDojo clean documents, n = 60 |

!!! warning "Current weakness"
    Most InjecAgent attacks name no target, and that is where detection is weakest. Spotlighting has not yet been run on InjecAgent, so the first question is still open on external data.

## Limits

- The clean set is small, so false-alarm rates have wide intervals.
- Two-step data-stealing attacks are out of scope for this version.
- Benchmark tool calls are simulated.
- Testing against attackers who adapt to this specific defense is out of scope, so results do not establish robustness against them.
