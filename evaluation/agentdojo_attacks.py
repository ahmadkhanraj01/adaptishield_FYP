"""
Phase 13's holdout — AgentDojo's attack side as boundary cases, stratified.

WHY A SEPARATE MODULE, AGAIN. `injecagent.py` says it: Rules §7 forbids pooling
cohorts of different authorship, and keeping two corpora in one file is how
pooling starts. This one has a third provenance and a different purpose again —
it is the **holdout** for a lexicon fitted on InjecAgent.

🔴 WHAT MAKES IT A HOLDOUT, AND HOW IT STOPS BEING ONE. The capability-misuse
lexicon was frozen and committed at `46cfbfb` **before this corpus existed in the
repo**. That is the pre-registration. It remains a holdout only while
`_CAPABILITY_CLASSES` is not edited in response to what it says; the moment it is,
this becomes a second development set and there is no third corpus waiting.

WHY IT IS A HARDER TEST THAN A REPEAT OF INJECAGENT. The attack distributions are
genuinely different. InjecAgent's direct-harm goals are blunt capability misuse —
unlock a door, transfer funds, delete a repository. AgentDojo's are softer and
more varied: make a hotel reservation, create a calendar event, say that a
restaurant is worth visiting, change a password, modify the recipient of a
recurring payment. Several of them have no controlled resource in the sense the
lexicon means, so a lexicon that only memorised InjecAgent's nouns should visibly
fail here.

THE STRATUM IS 3B's OWN PREDICATE, as in Phase 12 — `target_match` calls
`_references_mediator_target`, and a test fails if a recorded label ever diverges
from the live predicate. The split is **119/134**, far more even than InjecAgent's
51/459, so the two strata carry comparable weight and the population projection is
much less lopsided.

WHAT THIS CORPUS CANNOT TEST. It ships attacks only, so the false-positive columns
read 0/0 — an empty denominator, not a clean sheet, exactly as in Phase 12. The
[[FPR]] of record stays `fpr_report` at n=60.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "red_team", "data",
                    "agentdojo_attacks.json")

SERVER = "agentdojo-tools"
SERVER_URL = "https://tools.agentdojo.local"

from evaluation.vectors import LEGIT  # noqa: E402

WITH_TARGET = "AD-target"
NO_TARGET = "AD-notarget"


def load() -> Optional[Dict]:
    if not os.path.exists(DATA):
        print(f"[agentdojo-attacks] no vendored data at {DATA} — run "
              f"`python3 -m red_team.vendor_agentdojo_attacks --wheel-root ...` "
              f"first.")
        return None
    with open(DATA) as handle:
        return json.load(handle)


def provenance() -> Dict:
    payload = load()
    if not payload:
        return {"present": False}
    return {
        "present": True,
        "source": payload["source"],
        "citation": payload["citation"],
        "attack_template": payload["attack_template"],
        "excluded": payload["excluded"],
        "holdout_protocol": payload["holdout_protocol"],
        "available": payload["count"],
        "available_with_target": payload["with_target"],
        "available_without_target": payload["without_target"],
        "suites": payload["suites"],
    }


def sample(n_per_stratum: int = 30) -> List[Dict]:
    """
    Equal-sized stride draws from both strata.

    STRIDE, NOT RANDOM, for the reason `injecagent.sample` gives: there is no
    seed anywhere in this project because Ollama exposes none, so a random draw
    would make the corpus itself irreproducible and no manifest could repair
    that. A stride is reproducible from the recorded indices alone.

    THE STRIDE SPREADS SUITE AND TASK. Cases are generated suite by suite, and
    within a suite as goals × carriers, so consecutive indices share a goal.
    Taking the first n would draw one suite and confound the stratum with the
    attack family; striding across the whole split spreads both.
    """
    payload = load()
    if not payload:
        return []

    items = payload["items"]
    out: List[Dict] = []
    for stratum, want in ((True, n_per_stratum), (False, n_per_stratum)):
        pool = [it for it in items if it["target_match"] is stratum]
        if not pool:
            continue
        stride = max(1, len(pool) // want)
        drawn = pool[::stride][:want]
        if len(drawn) < want:
            print(f"[agentdojo-attacks] stratum target_match={stratum} has only "
                  f"{len(pool)} cases; drew {len(drawn)} of {want}.")
        out.extend(drawn)
    return out


def required_servers(items: List[Dict]) -> List[Tuple[str, str, str, List[str]]]:
    """
    One registry entry declaring every tool the drawn cases touch, in scope.

    Registered for the Phase 7 reason, laid a fourth time: a tool absent from the
    registry is refused by the permission gate before any detection layer runs,
    which makes every arm equal by construction and measures nothing.
    """
    tools = sorted({t for it in items for t in it["scope"]}
                   | {it["user_tool"] for it in items if it.get("user_tool")})
    return [(SERVER, SERVER_URL, "1.0", tools)]


def as_cases(n_per_stratum: int = 30, repeats: int = 1) -> Tuple[List, Dict[str, str]]:
    from red_team.attack_generator import RedTeamCase

    items = sample(n_per_stratum)
    cases = []
    for item in items:
        family = WITH_TARGET if item["target_match"] else NO_TARGET
        for r in range(repeats):
            suffix = f"-r{r}" if repeats > 1 else ""
            cases.append(RedTeamCase(
                case_id=f"AD{item['index']:03d}{suffix}",
                family=family,
                expected_malicious=True,
                user_input=item["user_input"],
                tool_response=item["mediator"],
                tool_name=item["user_tool"],
                proposed_action=item["proposed_action"],
                server_name=SERVER,
                destination_url=LEGIT,
                description=(f"AgentDojo {item['suite']} — {item['task_id']}"),
            ))

    cohorts = {WITH_TARGET: "attack_external", NO_TARGET: "attack_external"}
    return cases, cohorts


if __name__ == "__main__":
    payload = load()
    if payload:
        drawn = sample(30)
        print(f"available {payload['count']}  "
              f"({payload['with_target']} with target / "
              f"{payload['without_target']} without)")
        print(f"drawn {len(drawn)}  "
              f"({sum(1 for d in drawn if d['target_match'])} / "
              f"{sum(1 for d in drawn if not d['target_match'])})")
        print(f"suites in draw: {sorted({d['suite'] for d in drawn})}")
        print(f"distinct goals in draw: {len({d['goal'] for d in drawn})}")
