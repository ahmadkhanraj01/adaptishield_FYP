"""
The project website stays about the FYP, and every page in its menu exists.

These tests read files only, so they need no build and no network.
"""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

BANNED = re.compile(
    r"research|manuscript|\bpapers?\b|journal|arxiv|preprint|obsidian|\bvault\b|"
    r"\bstud(?:y|ies)\b|\bphase ?(?:7|10|11|12|13|15|16)\b|\bgrpo\b|§\s?6|\.agent/",
    re.IGNORECASE,
)


def site_files():
    files = list(DOCS.glob("*.md")) + [ROOT / "mkdocs.yml"]
    files += sorted((ROOT / "design" / "mockups").glob("*.html"))
    files += [DOCS / "assets" / "extra.css"]
    return files


@pytest.mark.parametrize("path", site_files(), ids=lambda p: p.name)
def test_site_stays_about_the_fyp(path):
    hits = [m.group(0) for m in BANNED.finditer(path.read_text(encoding="utf-8"))]
    assert not hits, f"{path.name} mentions: {sorted(set(hits))}"


def test_every_page_in_the_menu_exists():
    # mkdocs.yml uses no custom YAML tags, so a safe load is enough.
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    pages = [page for item in config["nav"] for page in item.values()]
    assert pages
    for page in pages:
        assert (DOCS / page).is_file(), page


def test_research_stays_out_of_the_site_source():
    assert not (DOCS / "Research").exists()
    assert not (DOCS / "paper").exists()
    assert not (DOCS / "writeup").exists()
