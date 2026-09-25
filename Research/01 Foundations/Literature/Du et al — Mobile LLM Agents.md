---
tags: [adaptishield, literature]
type: literature
---

# Du et al — Mobile LLM Agents

*"Measuring the Security of Mobile LLM Agents under Adversarial Prompts from
Untrusted Third-Party Channels"* · **Reviewed:** 18 March 2026

## The gap it identifies

Existing agent research measures **task performance and usability** while
overlooking security and privacy, and relies on threat models too simplified to
reflect adversarial content arriving through advertisements, notifications, and
embedded web views.

## Methodology — the origin of the eight vectors

- 8 state-of-the-art mobile agents evaluated
- **8 diverse attack vectors**: ad-based prompt injection, phishing, credential
  and OTP harvesting, cross-application data exfiltration, malware installation
- **2000+** adversarial and benign trials
- Comparative benign vs adversarial execution
- Mapping to MITRE ATT&CK Mobile

The eight-vector structure is inherited directly by
[[Phase 7 — Eight-Vector Benchmark]], alongside [[MCPSecBench]].

## Contribution to the gap

Empirical evidence of real-world vulnerability — the "static defenses fail in
practice" half of [[Research Gap]]. Also the source of the emphasis on
**untrusted third-party channels**, which becomes
[[Layer 1 — Input and Supply Chain Screening]]'s mediator partition.
