---
tags: [adaptishield, meta]
type: meta
---

# Vault Map

This vault mirrors the AdaptiShield repository at `~/adaptishield`, but as a
**graph rather than a set of documents**. The repo's Markdown files are long and
sequential; this vault splits them into one idea per note so the graph view shows
which ideas actually depend on which.

## Folders

| Folder | Holds |
| :--- | :--- |
| *(root)* | [[AdaptiShield]] — the hub |
| `00 Meta` | This note, [[Source Documents]] |
| `01 Foundations` | Concepts: the problem, the method, the vocabulary |
| `01 Foundations/Literature` | One note per cited paper or benchmark |
| `02 Architecture` | Layers, components, mechanisms |
| `03 Findings` | One note per result, positive or negative |
| `04 Research Log` | One note per dated log entry (I–XV) |
| `05 Phases` | The roadmap and the two phases with live detail |
| `06 Metrics` | Metric definitions and the current figures |
| `07 Practice` | Rules, traps, how to run, environment |
| `08 Open` | What is unanswered and what comes next |

## Conventions

- **A note states one thing.** If a note needs "and also", it should be two notes.
- **Negatives are first-class.** A withdrawn or reversed result keeps its note;
  it is marked, not deleted. The corrections have been the most transferable part
  of this work.
- **Every finding note ends with `## What this does not establish.`** This is
  inherited from the research log's own convention and is the most important
  habit in the project.
- **Frontmatter `tags`** carry the type (`concept`, `component`, `finding`,
  `log`, `metric`, `phase`, `rule`, `open`) so the graph can be filtered.
- **Status markers** follow the repo: ✅ done · 🟡 partial · 🔴 open defect ·
  ⛔ withdrawn.

## Extending it

New session, new result → add a note in `03 Findings`, link it from
[[Findings Index]], add a log note in `04 Research Log`, and update
[[Current Numbers]]. That is the whole ritual.

**🔴 This is now a hard rule, not a habit** (`Rules.md` §8, 8 Aug 2026): *every
session's work lands in this vault before the session ends* — code changed, a
campaign run, a number moved, a decision taken, a result withdrawn. §8 carries the
full Did → Write routing table, and [[Rules and Invariants]] mirrors it. The two
files are one thing in two views: change one, change the other in the same edit.

**Keep a wikilink on one line.** A `[[link]]` wrapped across a line break does not
resolve in Obsidian — it silently becomes plain text and drops out of the graph.
Four were introduced and fixed on 8 Aug; prose can wrap, links cannot.

The repo remains the source of truth for code and numbers; this vault is the
source of truth for *how the pieces relate*. Numbers that are *quotable* live in
the repo's tracked `results/` tree with a run manifest beside them (Rules §7) —
`logs/` is working output and goes stale.
