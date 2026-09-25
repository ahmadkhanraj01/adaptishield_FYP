"""
Phase 12 — the InjecAgent corpus as boundary cases, stratified.

WHY A SEPARATE MODULE. `evaluation/vectors.py` owns the eight taxonomy vectors and
their coverage map; this owns an externally-authored corpus with different
provenance, a different scope model and a stratum that has to travel with every
case. Rules §7 forbids pooling cohorts of different authorship, and keeping them in
one file is how pooling starts.

🔴 THE STRATIFICATION IS THE MEASUREMENT. Only **51 of 510** direct-harm cases —
10% — give 3B its sharpest signal: a target lifted out of the mediator and named in
the proposed action (§6m). The standalone severity rule leans on that path, and
**all 3** of Phase 11's residual attack successes lack it.

So a pooled detection rate over this corpus would average a stratum the detector has
strong evidence for against one where it has almost none, and report a middling
number that explains nothing. That is the same error as the "4/8 benign controls"
rate and as the withdrawn Phase 7 arms: a single figure over cases that are not
alike. `sample()` draws the two strata in a declared ratio and the family id carries
the stratum, so every report splits them.

⚠️ **The first attempt at this stratum was wrong**, and it is worth knowing why. It
counted an address appearing *anywhere* in the tool response, which matched 186 cases
— and 135 of those gave 3B nothing, because the address sat in the benign half while
the injection named none. The stratum is now the detector's own predicate.

WHY THE ATTACKER TOOLS ARE REGISTERED. InjecAgent's threat model is misuse of a
tool the agent legitimately holds. If those tools are absent from the registry the
permission gate refuses every case before 3A or 3B is consulted, and every arm is
equal by construction — the exact defect that withdrew Phase 7. Registering them,
with `destination_url` on the legitimate host, puts detection back on the hook.

WHAT THIS CORPUS CANNOT TEST. The data-stealing split is excluded (two-step
exfiltration, and this pipeline models one boundary), so Phase 12 says nothing about
that half of InjecAgent. And the attacker's harm here is a *tool call*, not an
email — so Layer 4's egress allowlist has nothing to bite on, and its zero here is
structural rather than measured.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "red_team", "data",
                    "injecagent_dh.json")

# The server the vendored cases claim to come from. One name, because the pipeline
# resolves scope per server and InjecAgent's tools are all capabilities of the same
# notional assistant.
SERVER = "injecagent-tools"
SERVER_URL = "https://tools.injecagent.local"

# Misuse-of-capability, not exfiltration-to-host: the harmful act is the tool call
# itself, so the HTTP destination is the legitimate one. Pointing it at an exfil
# host would hand Layer 4 every case and make the arms equal by construction.
from evaluation.vectors import LEGIT  # noqa: E402

# Stratum labels. These become the `family`, so they appear in every per-family
# breakdown the benchmark prints and cannot be lost on the way to the report.
WITH_TARGET = "IA-target"
NO_TARGET = "IA-notarget"


def load() -> Optional[Dict]:
    """The vendored payload, or None if `vendor_injecagent` has not been run."""
    if not os.path.exists(DATA):
        print(f"[injecagent] no vendored data at {DATA} — run "
              f"`python3 -m red_team.vendor_injecagent` first.")
        return None
    with open(DATA) as handle:
        return json.load(handle)


def provenance() -> Dict:
    """Manifest block. Records which cases were drawn, not just how many."""
    payload = load()
    if not payload:
        return {"present": False}
    return {
        "present": True,
        "source": payload["source"],
        "citation": payload["citation"],
        "split": payload["split"],
        "excluded": payload["excluded"],
        "available": payload["count"],
        "available_with_target": payload["with_target"],
        "available_without_target": payload["without_target"],
    }


def sample(n_per_stratum: int = 30) -> List[Dict]:
    """
    Equal-sized draws from both strata, by stride.

    STRIDE, NOT RANDOM. There is no seed anywhere in this project — Ollama exposes
    none, and determinism comes from greedy decoding — so a random draw would make
    the corpus itself irreproducible and no manifest could fix that. A stride is
    reproducible from the recorded indices alone.

    WHY THE STRIDE RUNS OVER THE FULL SPLIT. The 510 cases are a complete
    17 × 30 cross of user instructions against attacker instructions, ordered so
    that consecutive cases share a user instruction. Taking the first n would draw
    one or two user tools and confound the stratum with the tool. Striding across
    the whole split spreads both factors.

    EQUAL n PER STRATUM IS A DESIGN CHOICE, NOT THE POPULATION RATIO. The split is
    **51 / 459**, so drawing 30 and 30 over-samples the target-match stratum by a
    factor of nine. That is deliberate: the strata are reported separately and never
    pooled, so each needs enough cases for a usable interval of its own, and 30 of 51
    is most of that stratum's population.

    🔴 It also means **any pooled figure from this sample is wrong for InjecAgent** —
    the real corpus is 90% address-free, so a pooled rate here would flatter the
    detector by roughly nine to one. Nothing pools it, and the report says so.
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
            print(f"[injecagent] stratum target_match={stratum} has only "
                  f"{len(pool)} cases; drew {len(drawn)} of {want} requested.")
        out.extend(drawn)

    return out


def required_servers(items: List[Dict]) -> List[Tuple[str, str, str, List[str]]]:
    """
    One registry entry declaring every attacker tool the drawn cases invoke, plus
    the user tools whose responses arrive at the boundary.

    Registered as **in scope** — see the module docstring. A tool absent here is
    refused by the permission gate before any detection layer runs.
    """
    tools = sorted({t for it in items for t in it["scope"]}
                   | {it["user_tool"] for it in items if it.get("user_tool")})
    return [(SERVER, SERVER_URL, "1.0", tools)]


def as_cases(n_per_stratum: int = 30, repeats: int = 1) -> Tuple[List, Dict[str, str]]:
    """
    (AttackCase list, family -> cohort).

    The family is the **stratum**, so the per-family tables the benchmark already
    prints do the splitting for free rather than needing a second reporting path.
    """
    from red_team.attack_generator import RedTeamCase

    items = sample(n_per_stratum)
    cases = []
    for item in items:
        family = WITH_TARGET if item["target_match"] else NO_TARGET
        for r in range(repeats):
            suffix = f"-r{r}" if repeats > 1 else ""
            cases.append(RedTeamCase(
                case_id=f"IA{item['index']:03d}{suffix}",
                family=family,
                expected_malicious=True,
                user_input=item["user_input"],
                tool_response=item["mediator"],
                # The tool whose RESPONSE arrived at the boundary — not the
                # attacker's tool. The injection is in this tool's output; the
                # attacker's tool is what the proposed action would invoke.
                tool_name=item["user_tool"] or "unknown_tool",
                proposed_action=item["proposed_action"],
                server_name=SERVER,
                destination_url=LEGIT,
                description=(f"InjecAgent {item['attack_type']} — "
                             f"{item['attacker_tools'][0]}"),
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
        print(f"user tools in draw: "
              f"{len({d['user_tool'] for d in drawn})}")
        print(f"injections in draw: "
              f"{len({d['attacker_instruction'] for d in drawn})}")
        print(f"registry scope entries: {len(required_servers(drawn)[0][3])}")
