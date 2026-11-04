# site_src — the GitHub Pages site

**Everything under `docs/` and `mkdocs.yml` is generated. Do not edit them.**

The review deck was hand-written and drifted until it contradicted the repo. This
site cannot: `build.py` splits the manuscript from `paper/manuscript.md`, copies
figures regenerated from `results/`, and reads every number on the home page from
a `results/*.json`. `.github/workflows/site.yml` runs it on each push to `main`
and deploys to the `gh-pages` branch.

```bash
python3 site_src/build.py && mkdocs serve      # preview at localhost:8000
```

Repo setting: **Settings → Pages → Source: GitHub Actions.** The workflow uploads `site/` as the Pages artifact; no `gh-pages` branch is needed.

Planned sessions: 2 — vault import (architecture, literature, findings, log with
wikilinks resolved); 3 — per-phase results pages generated from JSON, with a
build test that fails on any hand-typed number; 4 — design pass and phase timeline.
