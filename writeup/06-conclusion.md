# 06 — Conclusion

**Maps to:** manuscript §XIII, plus the Data and Code Availability statement.
**Length target:** half a page. Two paragraphs. No new numbers, no new claims,
no citations.
**Job of this section:** restate what was found in the strongest form the
evidence supports, say why it matters for the next system, and stop.

---

## Paragraph 1 — what we did and what we found

- **We built a causal defense against indirect prompt injection and measured
  where it stops working.**
  `[meaning: one sentence, active voice, past tense; this is the whole paper]`
- **It detects attacks that a static allowlist and a published prompt-level
  defense both miss**, and **four of its six components change no measured
  outcome.**
- **Detection falls from 96.7% on attacks we wrote to roughly 18% on attacks
  someone else wrote**, and the collapse has a **named mechanism** rather than a
  mysterious distribution shift: the causal contrast carries signal when the
  injected content contains a target an action can lift, and close to none
  otherwise.
  `[meaning: we do not say "it generalised badly"; we say exactly why]`
- **The obvious repair generalizes about half.**
- **The adaptive layer proposes nothing, correctly**, because the quantity its
  parameters act on is zero in 80 to 97% of realistic turns.

## Paragraph 2 — what it means for the next system

- **The approach is not refuted, but its operating envelope is far narrower than
  its framing suggests, and the boundary is set by the scorer rather than by the
  causal idea.**
- **For the next system in this family, that is a more useful thing to know
  than another in-corpus accuracy figure.**
  `[meaning: a precise map of where it fails is worth more than one more good-looking number]`
- **It is visible only if detection is reported stratified by the property that
  governs it, which no evaluation we surveyed currently does.**
  `[meaning: the field's reporting habit hides this kind of cliff; we recommend changing the habit]`

## Data and Code Availability (a short separate statement after the conclusion)

- All results are regenerable by committed commands over the released artifact.
- Each phase directory under `results/` contains the benchmark payload and a run
  manifest recording commit SHA, working-tree cleanliness, model tags, corpus
  version, inference-server GPU state and a seeding statement.
- A deterministic test suite of **501 tests** runs in about 8 seconds with no
  model, no network and no GPU; it pins the failure modes of each measurement
  instrument rather than only the behaviour of the system.
- External corpora are vendored with source, licence and version recorded.
- Repository: <https://github.com/ahmadkhanraj01/adaptishield>. Site:
  <https://ahmadkhanraj01.github.io/adaptishield/>.
  `[meaning: anyone can re-run every number in the paper from the repo, and a reviewer can check that claim]`

## Writing rules for this section

- Mirror the introduction's claim sentence word for word. A reader who reads
  only the introduction and the conclusion should get the same paper.
- Do not add "future work" as a list. One sentence of forward-looking
  implication is enough; the concrete items are in §XII "what would change the
  conclusions".
- Do not thank anyone here. Acknowledgements are a separate block.
- The last sentence should be the most quotable in the paper. The current
  draft's is: *"…which is visible only if detection is reported stratified by
  the property that governs it, which no evaluation we surveyed currently does."*
