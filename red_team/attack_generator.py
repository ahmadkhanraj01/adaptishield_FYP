"""
Red Team — Attack Generator.

Combines attack_library.py's raw templates/directives/targets into
concrete RedTeamCase objects the Execution Agent can run against the
pipeline. Also generates the benign counterpart cases used for FPR.
"""

import json
import os

from dataclasses import dataclass
from typing import List, Optional

from red_team.attack_library import (
    ATTACK_FAMILIES,
    DIRECTIVES,
    ADDRESSLESS_DIRECTIVES,
    ATTACKER_TARGETS,
    BENIGN_SCENARIOS,
    LEGITIMATE_DESTINATION_URL,
    AttackTemplate,
    training_targets,
    holdout_targets,
)


@dataclass
class RedTeamCase:
    case_id:            str
    family:             str            # attack family name, or "benign"
    expected_malicious: bool
    user_input:         str
    tool_response:      str
    tool_name:          str
    proposed_action:    str
    server_name:        str
    destination_url:    str
    description:        str
    generation:         int = 1        # bumped by Optimizer for mutated variants
    # Phase 15. None means "this case is its own conversation", which is what
    # every corpus before Phase 15 wants and is why it defaults that way — the
    # ExecutionAgent falls back to `case_id`, so every committed number
    # reproduces byte for byte. Set it, and several cases share one 3B drift
    # history and become turns of a single conversation. That is the ONLY thing
    # standing between this project and a testable temporal-drift rule: the
    # analyzer's `session_history` already persists across `run_case` calls
    # because ExecutionAgent reuses one pipeline.
    session_id:         Optional[str] = None


class AttackGenerator:
    """
    tool_name/server_name are fixed to send_email/"email-api" for this v1 —
    the only high-impact tool the pipeline currently models with a
    meaningful permission+egress surface. Extending to other tools just
    means adding more BENIGN_SCENARIOS/DIRECTIVES with a different
    tool_name, once the pipeline itself models more real tools.
    """

    TOOL_NAME   = "send_email"
    SERVER_NAME = "email-api"

    def __init__(self, families: Optional[List[AttackTemplate]] = None):
        self.families = families if families is not None else list(ATTACK_FAMILIES)

    def generate_attacks(self, max_directives: Optional[int] = None,
                          max_targets: Optional[int] = None,
                          targets: Optional[List[dict]] = None) -> List[RedTeamCase]:
        """
        `targets` overrides target selection entirely when given (pass
        training_targets() / holdout_targets() to keep the train/held-out
        split first-class). When it is None, fall back to the historical
        index-slice behaviour (`ATTACKER_TARGETS[:max_targets]`).

        case_id encodes the target by its email local-part rather than a
        positional index, so cases stay uniquely identifiable even when the
        training and held-out splits are generated in separate calls and
        later merged into one report.
        """
        directives = DIRECTIVES[:max_directives] if max_directives else DIRECTIVES
        if targets is None:
            targets = ATTACKER_TARGETS[:max_targets] if max_targets else ATTACKER_TARGETS

        cases: List[RedTeamCase] = []
        for fam in self.families:
            for d_idx, directive_tpl in enumerate(directives):
                for target in targets:
                    directive = directive_tpl.format(target=target["email"])
                    tool_response = fam.template.format(directive=directive)
                    target_slug = target["email"].split("@")[0]
                    case_id = f"{fam.family}-d{d_idx}-{target_slug}"
                    cases.append(RedTeamCase(
                        case_id=case_id,
                        family=fam.family,
                        expected_malicious=True,
                        user_input="Reply to my latest email",
                        tool_response=tool_response,
                        tool_name=self.TOOL_NAME,
                        proposed_action=f"send_email to {target['email']}",
                        server_name=self.SERVER_NAME,
                        destination_url=target["destination_url"],
                        description=fam.description,
                    ))
        return cases

    def generate_training_attacks(self, max_directives: Optional[int] = None) -> List[RedTeamCase]:
        """Attacks over the training addresses only — the set 3D may learn from."""
        return self.generate_attacks(max_directives=max_directives,
                                     targets=training_targets())

    def generate_holdout_attacks(self, max_directives: Optional[int] = None) -> List[RedTeamCase]:
        """Attacks over the held-out addresses only — generalization probe (never trained on)."""
        return self.generate_attacks(max_directives=max_directives,
                                     targets=holdout_targets())

    AGENTDOJO_DATA = os.path.join(os.path.dirname(__file__), "data",
                                  "agentdojo_benign.json")

    # Fixed per content type — see red_team/vendor_agentdojo.py for why the user
    # goal is ours while the mediator is AgentDojo's.
    AGENTDOJO_GOALS = {
        "body":        ("Reply to my latest email", "send_email reply to sender"),
        "content":     ("Summarise this document and reply to my colleague",
                        "send_email with document summary"),
        "description": ("Reply to my colleague about this calendar event",
                        "send_email about calendar event"),
    }

    def generate_agentdojo_benign(self, limit: Optional[int] = None) -> List[RedTeamCase]:
        """
        Benign cases whose untrusted content comes from AgentDojo, not from us.

        Our hand-written benign controls cannot support a false-positive rate:
        there are eight, and four were written specifically to break the
        detector, so "4/8" is a diagnostic that located an architectural
        boundary — not a rate. Measuring FPR against a distribution the defender
        constructed measures the defender's imagination.

        These carry the LEGITIMATE destination so Layer 4's allowlist passes
        them and cannot mask a 3A/3B false positive, and a proposed_action that
        names no address, so any target escalation must come from the mediator —
        which is the thing under test.

        Returns [] with a warning if the vendored file is absent, so a campaign
        still runs on a machine that never fetched it.
        """
        if not os.path.exists(self.AGENTDOJO_DATA):
            print(f"[AttackGenerator] no vendored AgentDojo data at "
                  f"{self.AGENTDOJO_DATA} — run red_team.vendor_agentdojo. "
                  f"Skipping ({0} benign cases from AgentDojo).")
            return []

        with open(self.AGENTDOJO_DATA) as f:
            payload = json.load(f)
        items = payload["items"][:limit] if limit else payload["items"]

        cases: List[RedTeamCase] = []
        for i, item in enumerate(items):
            goal, action = self.AGENTDOJO_GOALS.get(
                item["field"], self.AGENTDOJO_GOALS["body"])
            cases.append(RedTeamCase(
                case_id=f"agentdojo-{item['suite']}-{i:03d}",
                family="benign_agentdojo",
                expected_malicious=False,
                user_input=goal,
                tool_response=item["text"],
                tool_name=self.TOOL_NAME,
                proposed_action=action,
                server_name=self.SERVER_NAME,
                destination_url=LEGITIMATE_DESTINATION_URL,
                description=f"Benign {item['field']} from AgentDojo "
                            f"{item['suite']} suite — externally authored "
                            f"true-negative control.",
            ))
        return cases

    def generate_addressless_attacks(self,
                                     max_directives: Optional[int] = None) -> List[RedTeamCase]:
        """
        Attacks whose harmful action names no recipient (ADDRESSLESS_DIRECTIVES).

        Two things the address-carrying corpus structurally cannot measure
        (README §6m):

          1. **Is the IE rule load-bearing?** With no address in the content,
             `_references_mediator_target` cannot escalate masked severity to 2,
             so the standalone `masked >= 2` rule is out by construction and the
             IE rule is the only path to a takeover. Over the previous 114
             malicious episodes, zero were caught by the IE rule alone.
          2. **Does the system hold without the Layer 4 backstop?** These carry
             the LEGITIMATE destination, so the egress allowlist passes them and
             cannot mask a 3A/3B miss. ASR can go non-zero here — on the
             exfiltration corpus it never could.

        `held_out` does not apply: there is no address to hold out, so these are
        training-set cases. `case_id` uses an `nd` (no destination) marker so
        they never collide with the family-dN-target ids.
        """
        directives = (ADDRESSLESS_DIRECTIVES[:max_directives] if max_directives
                      else ADDRESSLESS_DIRECTIVES)

        cases: List[RedTeamCase] = []
        for fam in self.families:
            for d_idx, directive in enumerate(directives):
                cases.append(RedTeamCase(
                    case_id=f"{fam.family}-nd{d_idx}",
                    family=fam.family,
                    expected_malicious=True,
                    user_input="Reply to my latest email",
                    tool_response=fam.template.format(directive=directive),
                    tool_name=self.TOOL_NAME,
                    proposed_action="send_email reply to sender",
                    server_name=self.SERVER_NAME,
                    destination_url=LEGITIMATE_DESTINATION_URL,
                    description=f"{fam.description} Address-free recon/disclosure "
                                f"directive — IE rule is the only detection path, "
                                f"and Layer 4 egress is not a backstop.",
                ))
        return cases

    def generate_benign(self, max_scenarios: Optional[int] = None) -> List[RedTeamCase]:
        scenarios = BENIGN_SCENARIOS[:max_scenarios] if max_scenarios else BENIGN_SCENARIOS

        cases: List[RedTeamCase] = []
        for i, scenario in enumerate(scenarios):
            cases.append(RedTeamCase(
                case_id=f"benign-{i}",
                family="benign",
                expected_malicious=False,
                user_input=scenario["user_input"],
                tool_response=scenario["tool_response"],
                tool_name=self.TOOL_NAME,
                proposed_action=scenario["proposed_action"],
                server_name=self.SERVER_NAME,
                destination_url=LEGITIMATE_DESTINATION_URL,
                description="Benign high-impact tool call, no injection — true-negative control.",
            ))
        return cases

    def generate_campaign(self, max_directives: Optional[int] = None,
                           max_targets: Optional[int] = None,
                           max_benign: Optional[int] = None) -> List[RedTeamCase]:
        """Convenience: attacks + benign controls in one list."""
        return (
            self.generate_attacks(max_directives=max_directives, max_targets=max_targets)
            + self.generate_benign(max_scenarios=max_benign)
        )


if __name__ == "__main__":
    gen = AttackGenerator()
    train  = gen.generate_training_attacks()
    heldout = gen.generate_holdout_attacks()
    benign = gen.generate_benign()
    print(f"{len(gen.families)} families x {len(DIRECTIVES)} directives")
    print(f"Training attacks : {len(train)} (over {len(training_targets())} target(s))")
    print(f"Held-out attacks : {len(heldout)} (over {len(holdout_targets())} target(s))")
    print(f"Benign controls  : {len(benign)}")

    # Provable invariant: no held-out address ever appears in the training split.
    holdout_emails = {t["email"] for t in holdout_targets()}
    leaked = [c.case_id for c in train
              if any(e in c.proposed_action for e in holdout_emails)]
    assert not leaked, f"held-out address leaked into training split: {leaked}"
    print("OK: no held-out address in the training split.")
