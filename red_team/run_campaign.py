"""
Red Team — Campaign Runner.

Wires Attack Generator -> Execution Agent -> Evaluator -> Optimizer into
one run: generate cases, execute them against a live pipeline, evaluate
ASR/FPR/WCR, then let the Optimizer propose keyword-softened mutations of
whatever was fully defended and run a second generation to see if ASR
moves. Saves both generations' reports to logs/red_team_runs/.

Train / held-out split (Rules.md §5): gen-1 and gen-2 attacks are drawn
ONLY from training_targets(); the held-out addresses never appear in any
episode 3D could train on. With `run_holdout=True` the same families and
directives are then replayed against holdout_targets() as a separate,
labelled generalization pass — that is the set that answers "did a fix
generalize, or just memorize a training address?" (README §6d).

Local default is intentionally small (1 directive x 1 training target per
family + all benign scenarios) since each high-impact case costs several
LLM calls through the Causal Analyzer (~15-20s locally). The full
natural-gap campaign — all 6 families x 4 directives x both training
targets (48 gen-1) plus the held-out pass — is a Kaggle-scale run; drive
it by raising max_directives / max_train_targets (see __main__).
"""

import json
import os
from datetime import datetime

from red_team.attack_generator import AttackGenerator
from red_team.attack_library import training_targets, holdout_targets
from red_team.execution_agent import ExecutionAgent
from red_team.evaluator import Evaluator
from red_team.optimizer import MutationOptimizer

LOG_DIR = "logs/red_team_runs"


def run_campaign(max_directives=1, max_train_targets=1, max_holdout_targets=1,
                 max_benign=None, run_gen2=True, run_holdout=False):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().isoformat()

    gen = AttackGenerator()
    agent = ExecutionAgent()
    evaluator = Evaluator()

    train_targets = training_targets()[:max_train_targets] if max_train_targets else training_targets()
    attacks = gen.generate_attacks(max_directives=max_directives, targets=train_targets)
    benign = gen.generate_benign(max_scenarios=max_benign)
    cases = attacks + benign

    print(f"[Campaign] Training targets: {[t['email'] for t in train_targets]}")
    print(f"[Campaign] Generation 1: {len(attacks)} attack case(s), {len(benign)} benign case(s)")
    results_gen1 = agent.run_batch(cases)
    report_gen1 = evaluator.evaluate(results_gen1)
    evaluator.print_report(report_gen1)

    campaign_record = {
        "timestamp": timestamp,
        "training_targets": [t["email"] for t in train_targets],
        "generation_1": evaluator.to_dict(report_gen1),
    }

    if run_gen2:
        optimizer = MutationOptimizer()
        mutated_cases = optimizer.propose_next_generation(report_gen1, attacks)

        if mutated_cases:
            print(f"\n[Campaign] Generation 2: {len(mutated_cases)} mutated attack case(s)")
            results_gen2 = agent.run_batch(mutated_cases)
            # Gen-2 report only makes sense over attacks (no fresh benign
            # run needed — FPR doesn't change when only attacks mutate).
            report_gen2 = evaluator.evaluate(results_gen2)
            evaluator.print_report(report_gen2)
            campaign_record["generation_2"] = evaluator.to_dict(report_gen2)

            print(f"\n{'='*60}")
            print("[Campaign] Generation 1 vs 2 — ASR by family")
            print(f"{'='*60}")
            gen1_by_fam = {f.family: f.asr for f in report_gen1.by_family}
            gen2_by_fam = {f.family: f.asr for f in report_gen2.by_family}
            for fam in sorted(set(gen1_by_fam) | set(gen2_by_fam)):
                g1 = gen1_by_fam.get(fam)
                g2 = gen2_by_fam.get(fam)
                g1_s = f"{g1:.0%}" if g1 is not None else "n/a"
                g2_s = f"{g2:.0%}" if g2 is not None else "n/a"
                print(f"  {fam:<28} gen1={g1_s:<6} gen2={g2_s}")
        else:
            print("\n[Campaign] Nothing for the Optimizer to mutate this round.")

    if run_holdout:
        hold_targets = holdout_targets()[:max_holdout_targets] if max_holdout_targets else holdout_targets()
        holdout_cases = gen.generate_attacks(max_directives=max_directives, targets=hold_targets)
        print(f"\n{'='*60}")
        print(f"[Campaign] HELD-OUT generalization pass: "
              f"{[t['email'] for t in hold_targets]}")
        print(f"{'='*60}")
        print(f"[Campaign] {len(holdout_cases)} held-out attack case(s) "
              f"(never in the training split)")
        results_holdout = agent.run_batch(holdout_cases)
        report_holdout = evaluator.evaluate(results_holdout)
        evaluator.print_report(report_holdout)
        campaign_record["holdout_targets"] = [t["email"] for t in hold_targets]
        campaign_record["holdout"] = evaluator.to_dict(report_holdout)

    out_path = os.path.join(LOG_DIR, f"campaign_{timestamp.replace(':', '-')}.json")
    with open(out_path, "w") as f:
        json.dump(campaign_record, f, indent=2)
    print(f"\n[Campaign] Report saved to {out_path}")

    return campaign_record


if __name__ == "__main__":
    # Fast local smoke run. For the full natural-gap campaign (Phase 6 gate),
    # raise the knobs:
    #   run_campaign(max_directives=None, max_train_targets=None,
    #                max_holdout_targets=None, run_holdout=True)
    run_campaign()
