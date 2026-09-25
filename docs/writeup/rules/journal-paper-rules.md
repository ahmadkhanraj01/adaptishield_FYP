# Rules for a journal research paper

A journal paper is reviewed by two to four experts over weeks, with a revision
round, and is expected to be complete rather than preliminary. Everything in
`general-research-paper-rules.md` applies. This file adds what changes because
the venue is a journal, with IEEE Transactions and IEEE Access conventions as the
default since the manuscript already follows them. The project's own evidentiary
bar is `Rules.md` §7, adopted when the supervisor changed the target on
3 August 2026; the rules below are consistent with it.

---

## 1. What a journal expects that a conference does not

- **Completeness over novelty.** A conference paper can be a promising first
  result. A journal paper must have the baselines, the ablations, the repeats
  and the limitations already in it. Reviewers will ask *compared to what*,
  *over how many episodes*, and *with what interval*, and expect the answers to
  be in the submitted version.
- **Room for negative results.** Journals have the pages; use them. Our three
  negative results about adaptive configuration are first-class contributions
  precisely because a journal has room to explain them.
- **A reproducibility artifact is expected.** A committed repository, tracked
  result files with manifests, a test suite, and a Data and Code Availability
  statement. IEEE Access requires the statement even when the answer is "on request".
- **A revision round is normal.** Expect "major revision" as the good outcome.
  Write the paper so every claim can be defended in a point-by-point response.

## 2. Front matter (IEEE style)

- **Title**: names the finding. Ours names the property that governs the result
  and the design of the evaluation. Avoid system names in titles unless the
  system is the contribution.
- **Author block**: full names, affiliations with department and city,
  corresponding author with email. IEEE Access adds ORCID for each author and
  membership grade after the name ("Member, IEEE"). Author order is the
  supervisor's decision; confirm it before submission.
- **Funding statement**: required by IEEE Access even when there is none.
  Write "This work received no external funding" rather than omitting it.
- **Abstract**: 200–250 words, one paragraph, no citations, no undefined
  abbreviations, no figures. States problem, approach, the main results with
  their key numbers, and the claim.
- **Index terms**: five to eight, alphabetical in IEEE style, drawn from the
  IEEE taxonomy where possible.

## 3. Section numbering and cross-references

- **IEEE uses Roman numerals for sections** (I, II, III) and letters for
  subsections (A, B, C). Tables are numbered in Roman (Table I), figures in
  Arabic (Fig. 1).
- **Every table and figure is cited in the text before it appears**, as
  "Table IV" and "Fig. 2", never "the table below".
- **Inserting a table renumbers everything after it.** After any structural
  edit, grep the manuscript for every `Table [IVX]+` and `Fig. [0-9]+` and
  check each against its caption. We renumbered VI–XII to VII–XIII once and the
  only prose reference was in a different section from the insertion.
- **Appendices** hold what a reviewer may need but a reader does not:
  implementation diagrams, extended tables, pre-registration text.

## 4. Statistics a journal reviewer will check

- **Confidence intervals on every proportion.** Wilson score intervals for
  small n and rates near 0 or 1; the normal approximation is wrong there. Say
  which interval you used and cite it once (Wilson, 1927).
- **Paired designs get paired tests.** When two arms saw identical cases,
  overlapping intervals are not the test; the discordant pairs are. Report
  `helped / hurt / discordant` and McNemar's test, exact below about 25
  discordant pairs. Cite McNemar (1947).
- **Never read a high p-value as equivalence.** Two discordant pairs and
  p = 1.0 is near-zero power, not "the same". Say so in the sentence.
- **A statistic is a result, not arithmetic.** No p-value or interval enters
  the paper before the code computing it is committed and its inputs are in a
  tracked file. A p-value once reached five of our documents with no committed
  implementation. It happened to be right.
- **Repeats, and what they bound.** If greedy decoding is not literally
  deterministic (ours: 2 of 564 severities disagreed), report repeat-level
  spread and say whether repeats bound the instrument or the full system.
- **Pre-registration.** State what was registered, where it is committed, and
  whether any later attempt was written after seeing an earlier result.
- **Diagnostics are labelled diagnostics.** A rate on n = 3 or n = 8 is not a
  rate. Label it in the text and in the table, every time.

## 5. Reproducibility and the artifact

- **One committed command per number.** Name it in the artifact's README.
- **A run manifest per result**: commit SHA, working-tree dirty flag, model
  tags, corpus name and version, temperature, sample count, GPU state, date.
- **A replayed result says so in its manifest.** Recomputing an old run with
  new reporting code produces a report stamped with the current commit, which is
  a provenance lie unless the manifest records the replay.
- **External corpora vendored with source, licence and version.** AgentDojo
  v0.1.35 (MIT), InjecAgent (MIT). A reviewer cannot check a number from an
  unversioned corpus.
- **Deterministic tests that pin the instruments.** Our suite pins the failure
  modes of each measurement tool, not only the system's behaviour, and runs
  with no model, network or GPU. State the count and runtime in the Data and
  Code Availability statement, and keep it current (it drifted to 494 in the
  draft while the suite was at 501).
- **A Data and Code Availability statement** after the conclusion: where the
  code is, what regenerates what, what cannot be regenerated and why. Ours
  discloses that the campaign artifact is a replay over untracked checkpoints.

## 6. Positioning against published work

- **Never present a cross-paper comparison as like-for-like** unless corpus,
  model, metric and threat model all match. Put "not like-for-like" in the
  caption, not only in the prose.
- **Quote published numbers verbatim, with the sentence they came from.** If a
  paper gives two figures for one quantity (AgentDojo's 7.5% in prose, 6.84% in
  Table 5), quote the one you use and name the other beside it. Report the
  discrepancy; do not resolve it silently.
- **Prefer published results that carry their own baseline.** A difference
  measured in one table is worth more than a level quoted from another.
- **A human reads the primary table before a number is marked verified.**

## 7. Figures for print

- **Vector for the PDF submission** (PDF or EPS), with a PNG preview. IEEE
  typesets at column width (about 3.5 in) or page width (about 7.16 in); design
  for one of those.
- **Minimum 8 pt text in the final rendered size.** Check by printing the page.
- **Colourblind-safe and greyscale-readable**; distinct markers as well as
  colours for series that must be told apart.
- **Print-only white background.** No dark theme figures in a journal PDF.
- **One message per figure.** If a caption needs "and also", split the figure.

## 8. Language discipline

- **Choose the exact verb.** "Detected" is not "blocked". "Proposes a no-op" is
  not "does nothing". "Unidentifiable on this batch" is not "irrelevant".
- **State provenance in the sentence.** "On attacks we wrote" versus "on
  externally-authored attacks", every time the number changes population.
- **British or American spelling, one throughout.** IEEE accepts either; the
  manuscript currently mixes "sanitise/sanitize" and must be normalised at
  submission.
- **Avoid "we believe" except once**, in the introduction, where a judgement is
  being made about the value of a finding.

## 9. The submission package

- Manuscript PDF, built from source (ours regenerates the `.docx` from
  `paper/manuscript.md`; never edit the Word file).
- Figures as separate vector files if the venue asks.
- Cover letter: one page. Names the contribution in three sentences, says why
  this journal, states no concurrent submission, lists suggested reviewers if
  invited to, discloses conflicts.
- Author block confirmed: ORCIDs, grades, order, funding.
- Artifact link that resolves to a tagged commit.
- Graphical abstract if the venue uses one (IEEE Access does).

## 10. The response to reviewers

- **Every comment gets a numbered reply** quoting the comment, stating what
  changed, and pointing to the page and line.
- **Concede quickly where the reviewer is right.** A paper that argues every
  point reads as defensive.
- **Where you disagree, disagree with evidence**, not with assertion, and offer
  the sentence you added to the paper to make the point clear to the next reader.
- **Never add a number in the response that is not also in the revised paper.**
- **Keep a change log** of every edit between versions. Reviewers ask for it.

## 11. Ethics and authorship

- **Authorship follows contribution.** Everyone listed contributed to
  conception, work, or writing, and approved the final version. The supervisor
  decides order.
- **Disclose what a reader would want to know**: funding, conflicts, data
  licences, and any AI tools used in preparing the manuscript, in the form the
  venue requires.
- **Attacker-authored text in artifacts.** Our raw logs contain injected
  attack text verbatim and are not tracked; the paper says so. Do not paste
  attacker payloads into the manuscript beyond short illustrative quotes.

## 12. A checklist before pressing submit

- [ ] One claim, stated identically in abstract, introduction and conclusion
- [ ] Every proportion has n, corpus and a Wilson interval
- [ ] Every paired comparison reports discordant pairs and an exact p
- [ ] Every table and figure cited before it appears, numbered in order
- [ ] Every published number verbatim, verified by a human, with its setting
- [ ] Positioning tables captioned "not like-for-like"
- [ ] Limitations section scopes each limit and says what still holds
- [ ] Data and Code Availability statement current (test count, runtime, replay disclosure)
- [ ] Author block complete: ORCID, grade, order, funding
- [ ] Spelling normalised to one variant
- [ ] Abstract within the word limit
- [ ] Artifact link resolves to a tagged commit
