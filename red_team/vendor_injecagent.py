"""
Vendor InjecAgent's direct-harm test cases into red_team/data/.

WHY. Every malicious case this project has measured against was written here.
[[6n]] fixed that on the *benign* side by importing AgentDojo, and the lesson —
**a defense measured only against a corpus its author wrote measures the author's
imagination** — was left half-applied, because the attack side had no equivalent
import. Phase 11 sharpened the need: it found four of six components inert, but all
21 malicious cases are tool-response injections aimed at one action shape, so
"inert in general" and "inert on our corpus" are indistinguishable from inside.

  @inproceedings{zhan2024injecagent,
    title  = {InjecAgent: Benchmarking Indirect Prompt Injections in
              Tool-Integrated Large Language Model Agents},
    author = {Zhan, Qiusi and Liang, Zhixiang and Ying, Zifan and Kang, Daniel},
    booktitle = {Findings of ACL 2024},
    year   = {2024}}

  https://github.com/uiuc-kang-lab/InjecAgent — MIT licence.

WHY IT FITS WITHOUT APPROXIMATION. InjecAgent delivers its injection inside a
**tool response** — an attacker instruction embedded in a product review, a
calendar entry, an email body — which is exactly the boundary this pipeline models
end to end. That is a better fit than two of our own taxonomy vectors (V5 tool
poisoning, V6 rug pull), which are approximated because the pipeline consumes tool
*responses* rather than manifests.

  User Instruction  -> user_input      (trusted)
  Tool Response     -> mediator        (untrusted; carries the injection)
  Attacker Tools    -> proposed_action (the harmful call, per THEIR ground truth)

WHY THE ATTACKER TOOL IS REGISTERED IN SCOPE. InjecAgent's threat model is **misuse
of a tool the agent legitimately has** — the user's assistant really does hold the
smart-lock tool, and the injection makes it grant access. So the vendored cases
register their attacker tools with declared scopes, and the permission gate passes.

That is not generosity, it is the Phase 7 correction applied again. Leaving those
tools unregistered would make Layer 4's scope check refuse **every** case before
3A or 3B was consulted, and every arm would be equal *by construction* — which is
precisely the defect that forced the first eight-vector benchmark to be withdrawn.
`destination_url` is the legitimate host for the same reason: these are misuse-of-
capability attacks, not exfiltration-to-host attacks.

WHAT IS TAKEN, AND WHAT IS NOT. Only `test_cases_dh_base.json` — the **direct harm**
split, whose harm is a tool call. The **data-stealing** split (`ds`) is deliberately
excluded for now: its harm is a two-step exfiltration whose second step this
single-boundary pipeline cannot model, and importing it would add cases that fail
for a structural reason rather than a detection reason. The `enhanced` splits are
excluded too — they prepend a hand-written "IMPORTANT!!!" hijack prompt, which
makes them *easier*, and a harder-looking corpus that is actually easier is worse
than no corpus.

🔴 THE STRATIFICATION IS THE POINT, AND THE FIRST ATTEMPT AT IT WAS WRONG.
**Only 51 of 510 cases — 10% — give 3B its sharpest signal**, a target lifted out of
the mediator and named in the proposed action (§6m). All 3 of Phase 11's residual
attack successes lack exactly that signal, so pooling the strata would average a
stratum the detector has strong evidence for against one where it has almost none,
and report a middling rate that explains nothing.

The first version stratified on "an address appears anywhere in the tool response",
which matched 186 cases — and **135 of those gave 3B nothing**, because the address
sat in the benign half (a GitHub URL, a sender field) while the injection named none.
The stratum must be the detector's **own predicate**, so `target_match` calls
`_references_mediator_target` directly. Same correction the refusal audit needed:
measure with the real rule, not something that resembles it.

Usage (needs network once; nothing at run time depends on it):
    python3 -m red_team.vendor_injecagent
    python3 -m red_team.vendor_injecagent --offline --source /path/to/InjecAgent/data
"""

import argparse
import json
import os
import re
import urllib.request
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "data", "injecagent_dh.json")

RAW_BASE = ("https://raw.githubusercontent.com/uiuc-kang-lab/InjecAgent/"
            "main/data")
SOURCE_FILE = "test_cases_dh_base.json"

CITATION = ("Zhan et al., InjecAgent: Benchmarking Indirect Prompt Injections in "
            "Tool-Integrated Large Language Model Agents, Findings of ACL 2024")
REPO = "https://github.com/uiuc-kang-lab/InjecAgent"
LICENCE = "MIT"

# Informational only: an address or URL anywhere in the tool response.
#
# 🔴 DO NOT STRATIFY ON THIS. The first version of this script did, and **135 of the
# 186 cases it labelled "has a target" gave 3B no signal at all** — the address was
# in the *benign* half of the response (a GitHub URL, a sender field) while the
# injection itself named none. 3B's target-match path asks whether the PROPOSED
# ACTION names a target lifted from the mediator, which happens only when the
# attacker instruction carries one. Counting addresses anywhere measured the
# corpus's furniture, not the detector's signal.
TARGET_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                       r"|https?://[^\s'\"]+")


def _target_match(proposed_action: str, mediator: str) -> bool:
    """
    3B's **own** predicate, `_references_mediator_target`, run on the case.

    Using the real predicate rather than a regex that resembles it is the same
    correction the refusal audit needed: a stratum computed by a different rule than
    the detector applies will mislabel cases, and here it mislabelled 135 of 186.

    Pure string work — no model call, no network — so vendoring stays deterministic
    and offline-reproducible.
    """
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer
    return CausalAnalyzer()._references_mediator_target(
        proposed_action.lower(), mediator)


def fetch(offline_source: str = None) -> List[Dict]:
    if offline_source:
        path = (offline_source if offline_source.endswith(".json")
                else os.path.join(offline_source, SOURCE_FILE))
        with open(path) as handle:
            return json.load(handle)

    url = f"{RAW_BASE}/{SOURCE_FILE}"
    print(f"[vendor] fetching {url}")
    with urllib.request.urlopen(url, timeout=120) as response:
        return json.loads(response.read().decode())


def _scope(attacker_tools: List[str]) -> List[str]:
    """
    The tool names the attacker's call needs in scope.

    InjecAgent lists them per case; a handful of cases name two, and both have to
    be declared or the permission gate refuses for the wrong reason.
    """
    return [t for t in attacker_tools if t]


def convert(cases: List[Dict]) -> Dict:
    """
    InjecAgent case -> our boundary record. No sampling here; the benchmark's
    sampler owns that, so the vendored file stays a faithful copy of the split.
    """
    items: List[Dict] = []
    skipped = 0

    for i, case in enumerate(cases):
        mediator = str(case.get("Tool Response") or "").strip()
        user_input = str(case.get("User Instruction") or "").strip()
        attacker_tools = case.get("Attacker Tools") or []
        instruction = str(case.get("Attacker Instruction") or "").strip()

        if not (mediator and user_input and attacker_tools and instruction):
            # A case missing any of the four cannot be run as a boundary crossing.
            # Counted rather than silently dropped: a filter that matches nothing
            # (or everything) is the §6n corpus defect, and the count is how you
            # notice.
            skipped += 1
            continue

        items.append({
            "index": i,
            "user_tool": case.get("User Tool"),
            "attacker_tools": attacker_tools,
            "attack_type": case.get("Attack Type"),
            "attacker_instruction": instruction,
            "expected_achievement": case.get("Expected Achievements"),
            "user_input": user_input,
            "mediator": mediator,
            # THEIR ground truth for the harmful action, not ours. Writing the
            # action ourselves would put the imagination we are importing this
            # corpus to remove straight back into the measurement.
            "proposed_action": f"{attacker_tools[0]} as instructed: {instruction}",
            "scope": _scope(attacker_tools),
            # THE STRATUM. 3B's own predicate — does the proposed action name a
            # target lifted out of the mediator?
            "target_match": _target_match(
                f"{attacker_tools[0]} as instructed: {instruction}", mediator),
            # Informational. Kept so the gap between the two is visible in the
            # vendored file rather than only in this docstring.
            "address_anywhere": bool(TARGET_RE.search(mediator)),
        })

    with_target = sum(1 for it in items if it["target_match"])
    address_anywhere = sum(1 for it in items if it["address_anywhere"])
    payload = {
        "source": f"{REPO} ({LICENCE} licence), {SOURCE_FILE}",
        "citation": CITATION,
        "split": "direct_harm_base",
        "excluded": ("data-stealing split (two-step exfiltration this "
                     "single-boundary pipeline cannot model) and both `enhanced` "
                     "splits (they prepend a hand-written hijack prompt, which "
                     "makes them EASIER)"),
        "count": len(items),
        "skipped_incomplete": skipped,
        "with_target": with_target,
        "without_target": len(items) - with_target,
        "address_anywhere": address_anywhere,
        "stratification_note": (
            "target_match is CausalAnalyzer._references_mediator_target run on the "
            "case — does the proposed action name a target lifted out of the "
            "mediator? That is 3B's sharpest signal (6m) and the path Phase 11's "
            "residual failures all lack. Report the two strata separately, never "
            "pooled. `address_anywhere` is informational and MUST NOT be used as "
            "the stratum: it labels an address in the benign half of the response, "
            "and doing so mislabelled 135 of 186 cases."),
        "items": items,
    }
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--offline", action="store_true",
                    help="read from --source instead of the network")
    ap.add_argument("--source", help="local InjecAgent data dir or json file")
    args = ap.parse_args()

    cases = fetch(args.source if args.offline else None)
    payload = convert(cases)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as handle:
        json.dump(payload, handle, indent=1)

    print(f"[vendor] {payload['count']} direct-harm cases "
          f"({payload['skipped_incomplete']} skipped as incomplete)")
    print(f"[vendor] STRATA (3B's own predicate): {payload['with_target']} where the "
          f"target-match fires, {payload['without_target']} where it cannot")
    print(f"[vendor] for contrast, {payload['address_anywhere']} have an address "
          f"SOMEWHERE in the response — that is furniture, not signal, and is not "
          f"the stratum")
    print(f"[vendor] {len({it['user_tool'] for it in payload['items']})} user tools, "
          f"{len({t for it in payload['items'] for t in it['attacker_tools']})} "
          f"attacker tools, "
          f"{len({it['attacker_instruction'] for it in payload['items']})} distinct "
          f"injections")
    print(f"[vendor] wrote {args.out}")

    if payload["without_target"] == 0 or payload["with_target"] == 0:
        print("[vendor] WARNING: one stratum is empty. The stratified sampler "
              "cannot balance, and a pooled rate would hide the mechanism.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
