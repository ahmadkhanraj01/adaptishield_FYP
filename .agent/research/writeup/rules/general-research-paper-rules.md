# Rules for writing a professional research paper

These are general rules for any research paper in computer science. The
companion file, `journal-paper-rules.md`, adds what a journal demands on top.
Where a rule has already bitten this project, the example is named so the rule
is a scar and not a preference.

---

## 1. Before writing a word

- **Know your one claim.** Write it as a single sentence you could defend in a
  viva. Everything in the paper either sets it up, supports it, or scopes it.
  Ours: *the causal contrast carries signal when the injected content contains a
  liftable target, and close to none otherwise.*
- **Know your reader.** A reviewer who is an expert in the field, is short of
  time, is looking for a reason to reject, and will read the abstract, the
  figures, the tables and the conclusion before any prose.
- **Freeze the numbers first.** Do not draft a section whose numbers can still
  move. Every number in a draft must already have a source file.
- **Outline in claims, not topics.** A section heading that is a topic ("Results")
  hides the finding. A heading that is a claim ("Only Two Components Do
  Anything") tells the skimming reviewer what to expect.

## 2. Structure: what each section is for

| Section | Its one job | Length (journal) |
| :--- | :--- | :--- |
| Title | Name the finding, not the system | ≤ 15 words |
| Abstract | The whole paper in 200–250 words; no citations | 1 paragraph |
| Introduction | Problem → gap → idea → contributions → claim → road-map | 1.5–2 pages |
| Related work | The field's shape, ending on the gap you fill | 1–1.5 pages |
| Methodology | Enough to reproduce; define every term used later | 3–4 pages |
| Results | What was measured, in the order that builds the argument | 6–8 pages |
| Discussion | What it means together; positioning; limitations | 2.5–3.5 pages |
| Conclusion | The claim again, and why it matters next | ½ page |
| References | Everything cited, nothing uncited | — |

- **The introduction states the result.** A research paper is not a mystery.
  The reader should know the finding by the end of page two.
- **Contributions are a numbered list of bold claims**, each with its evidence
  and a section pointer. This list is what reviewers grade.
- **Results come before discussion**, and the discussion introduces no new numbers.
- **Limitations are a section, not a sentence.** A paper that hides its limits
  gets them found by a reviewer, which is worse.

## 3. Paragraphs and sentences

- **One idea per paragraph, and the first sentence states it.** A reader who
  reads only first sentences should get the argument.
- **Topic sentence, evidence, consequence.** Most good paragraphs have that shape.
- **Prefer short sentences and active voice.** "We measured X" beats "X was
  measured". Passive voice is acceptable only when the actor is irrelevant.
- **Past tense for what you did, present tense for what is true.** "We ran three
  recordings" / "the gap is 86 points".
- **No hedging stacks.** "May possibly suggest" is one hedge too many. Choose
  the strength the evidence supports and use one word for it.
- **Define before use.** Every acronym expanded on first use; every metric
  defined in the methodology before it appears in a table.
- **Do not say "novel", "clearly", "obviously", "it is well known".** Let the
  evidence carry the weight. If it is obvious, the reviewer will think so
  without being told; if it is not, the word annoys them.

## 4. Numbers

- **Every number has its n and its interval.** "96.7%" is not a result;
  "116/120 = 96.7% [91.7%, 98.7%]" is.
- **Every number has its comparison.** A rate on its own means nothing; a rate
  beside its baseline is a finding.
- **Every number has its source.** In the draft, write `(results/phase12/)` after
  it. Strip the pointer at submission if the venue's style forbids it, but keep
  it until then.
- **Never pool cohorts of different provenance.** Hand-written and external
  benign documents are different populations. Pooling them once turned a 4/8
  diagnostic into a fake false-positive rate.
- **Never pool strata drawn in unequal proportion to the population.**
  A 30/30 draw from a 51/459 population pooled gives 51.7%, wrong by 33 points.
- **Round consistently.** One decimal for percentages, and the same precision in
  the table and the prose.
- **Report withdrawn numbers beside their corrections**, marked withdrawn. A
  reviewer who finds an unlisted correction trusts nothing else.
- **A single run is a sample, not a value.** If a metric can vary run-to-run,
  report the distribution or say the number is single-run.

## 5. Figures and tables

- **A figure shows a comparison; a table shows exact values.** If the reader
  needs the number, use a table. If the reader needs the shape, use a figure.
- **Every figure and table is referred to in the text before it appears**, by
  number, and the text says what to look at.
- **Captions are self-contained.** A reviewer skims figures first. The caption
  must state what is plotted, the n, and the one thing the figure shows.
- **Generate figures from committed data; never hand-draw a result figure.**
  Ours are produced by `paper/make_figures.py` and fail if the source file is missing.
- **Use a colourblind-safe palette** (Okabe–Ito or similar) and check the
  figure in greyscale. Print reviewers still exist.
- **Label axes with units. Start bar charts at zero.** A truncated axis is
  read as deception even when it is not.
- **Tables have one caption line stating what they compare and one note stating
  what they do not.** Our positioning tables say "not like-for-like" in the
  caption itself.

## 6. Citations and related work

- **Cite the original source**, not a survey that cites it, unless the survey is
  the point.
- **Every quoted published number carries the verbatim sentence it came from**,
  in your notes if not in the paper. We keep them in `paper/external_numbers.json`.
  A number transcribed by hand from a table was wrong by twelve points once.
- **A human reads the primary source before a number is quoted.** An automated
  fetch or a model's transcription is an intermediary, and the guard exists to
  refuse intermediaries.
- **State the setting with every published number.** Corpus, model, metric,
  version. A published figure without its setting is a comparison you cannot
  defend.
- **Group related work by idea, not by paper.** End on the gap.
- **Do not criticise prior work to make yours look better.** State what it
  assumes and where that assumption fails, with evidence.

## 7. Honesty and scope

- **Say what a result does not establish.** Every results subsection in our
  research log ends with that heading, and it is the most transferable habit in
  the project.
- **Negative results are reported, not dropped.** They are often the most
  defensible claim in the paper, because they came with the least incentive to
  find them.
- **Distinguish "detected" from "blocked", "no gap the knob can close" from "no
  gap", "unidentifiable on this batch" from "irrelevant".** Each has been
  confused once in our documents.
- **Pre-register when you can.** Write the success criterion and commit it
  before the run. When a second attempt is made after seeing the first, say so
  in the paper.
- **Do not tune until it fires.** Two pre-registered attempts is the limit we
  set; a third is indistinguishable from fitting the corpus.

## 8. Drafting process

1. Write the results section first, from the frozen numbers.
2. Write the methodology second, defining everything the results used.
3. Write the discussion third, now that you know what the results mean together.
4. Write the introduction fourth, so its contributions list matches the paper
   that exists.
5. Write related work fifth, ending on the gap the introduction opened.
6. Write the conclusion sixth, mirroring the introduction's claim.
7. Write the abstract last.
8. Write the title last of all, from the claim.

- **Read the whole paper aloud once.** Sentences that cannot be spoken cannot be
  read either.
- **Give it to one person who has not seen it** and ask them to state the
  finding in one sentence. If they cannot, the introduction has failed.
- **Check every cross-reference after any insertion.** Adding one table
  renumbered seven of ours. Grep `Table [IVX]` before and after.

## 9. The common desk-reject reasons, and the fix for each

| Reason | Fix |
| :--- | :--- |
| No baseline from outside your own system | Add an undefended floor and a published defense on the same corpus |
| A headline number with no interval or n | Wilson interval, n, corpus, in the same sentence |
| Contribution list that is a feature list | Rewrite each as a measured claim with a section pointer |
| Related work that is a list of papers | Regroup by idea; end on the gap |
| Limitations in one sentence | Expand into a section; scope each one |
| Figures that cannot be read in greyscale | Colourblind-safe palette, distinct markers |
| Claims not reproducible from the artifact | One committed command per number, with a manifest |
| Abstract over the word limit | Cut sentences that describe the system; keep the ones that state results |
