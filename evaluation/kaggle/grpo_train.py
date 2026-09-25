"""
GRPO trainer for Component 3D — the Kaggle P100 kernel (Phase 6 step 2).

Replaces the *internals* of `AdaptiveThreatModel.propose_update()` (the v1
directional heuristic) with a real policy-gradient loop, while keeping the exact
same reward and the same `LabeledEpisode → ProposedUpdate → apply_update`
contract. It reads the JSONL the packager produced, learns a distribution over
the `ie_threshold` grid by GRPO, and writes a `proposed_update.json` in the
`ProposedUpdate` schema for `apply_and_validate.py` to apply locally.

Why GRPO here is honest, not theatre
────────────────────────────────────
The action space is the one knob the whole Phase 5b story is about: which IE
grid value to set `ie_threshold` to. Each step samples a *group* of candidate
thresholds from the current policy, scores each on the full batch with the exact
project reward (grpo_env.evaluate_policy), and uses the group mean as the
baseline — advantage = reward − group_mean. That group-relative advantage is
GRPO's defining move (no learned critic); the update is REINFORCE on the policy
logits. If the data has no threshold gap (Phase 5's natural-set finding), every
candidate scores alike, advantages vanish, and the policy stays put → a no-op
proposal, which `apply_update` refuses. That "GRPO adds nothing when there's
nothing to learn" outcome is itself a valid Phase 6 result.

On hardware, and why the GPU is not the point
─────────────────────────────────────────────
The categorical policy is tiny and the joint search is a few thousand float
operations over a 188-row table — it finishes in about a quarter of a second on
CPU. The GPU never made this faster; the reason to run on Kaggle is that it is
the only environment available here where `torch` is importable at all, so the
torch backend can be *executed* and cross-checked against the pure-Python one
(`--compare-backends`). Two implementations of one algorithm that have never
been compared are two algorithms.

Kaggle's P100 is in fact unusable for this: it is compute capability sm_60 and
the PyTorch in the kernel image supports sm_70 and above, so `is_available()`
returns True and the first allocation dies with "no kernel image is available
for execution on the device". `_torch_device()` probes with a real allocation
and falls back to CPU, which costs nothing measurable.

No Ollama/pipeline here: the reward is replayed from the recorded diagnostics,
which is exact for campaign episodes (see grpo_env.py).
"""

import argparse
import json
import os
import sys
from statistics import mode
from typing import List, Optional

# grpo_env sits beside this file locally and inside the attached Kaggle Dataset.
#
# The fixed-depth glob below used to be one and two levels under /kaggle/input,
# which is where an attached dataset normally lands. When it did not, the kernel
# died with a bare "ModuleNotFoundError: No module named 'grpo_env'" and no
# indication of what /kaggle/input actually contained — so the failure could not
# be told apart from a dataset that never mounted, a dataset that mounted under
# an unexpected slug, or a genuine packaging mistake. Walk the tree instead, and
# if the module really is absent, say what IS there before giving up. A remote
# kernel that cannot be attached to a debugger has to explain itself.
try:
    from grpo_env import (RewardConfig, Policy, EpisodeFeatures,
                          load_episodes, evaluate_policy, ie_grid,
                          status_under_policy)
except ImportError:  # running as a module, or on Kaggle with a nested input dir
    _here = os.path.dirname(os.path.abspath(__file__))
    _found = None
    for _root in [_here, "/kaggle/input", "/kaggle/working", "/kaggle/src"]:
        if not os.path.isdir(_root):
            continue
        if os.path.exists(os.path.join(_root, "grpo_env.py")):
            _found = _root
            break
        for _dirpath, _dirnames, _filenames in os.walk(_root):
            if "grpo_env.py" in _filenames:
                _found = _dirpath
                break
        if _found:
            break

    if _found:
        sys.path.insert(0, _found)
        print(f"[grpo] found grpo_env.py in {_found}")
    else:
        print("[grpo] grpo_env.py NOT FOUND. Contents of the Kaggle mounts:")
        for _root in ("/kaggle/input", "/kaggle/working", "/kaggle/src"):
            if not os.path.isdir(_root):
                print(f"    {_root}: (does not exist)")
                continue
            _listing = []
            for _dirpath, _dirnames, _filenames in os.walk(_root):
                for _f in _filenames:
                    _listing.append(os.path.join(_dirpath, _f))
                if len(_listing) > 40:
                    break
            print(f"    {_root}: {len(_listing)} file(s)")
            for _p in _listing[:40]:
                print(f"        {_p}")
        print("[grpo] If /kaggle/input is empty, the dataset did not attach — "
              "check dataset_sources in kernel-metadata.json and that the "
              "dataset is 'ready' before the kernel is pushed.")

    from grpo_env import (RewardConfig, Policy, EpisodeFeatures,   # noqa: E402
                          load_episodes, evaluate_policy, ie_grid,
                          status_under_policy)


def _find_episodes() -> Optional[str]:
    """
    Locate the packaged dataset.

    The Kaggle mount is deeper than it looks: an attached dataset lands at
    /kaggle/input/datasets/<owner>/<slug>/, so the fixed one- and two-level
    globs this used to rely on missed it by two levels and the kernel exited
    with "no episodes.jsonl found" while the file sat right there. Walk instead
    of guessing the depth — the same mistake cost two failed kernel runs on the
    grpo_env import above.
    """
    for cand in ["episodes.jsonl",
                 os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "dataset", "episodes.jsonl")]:
        if os.path.exists(cand):
            return cand

    for root in ("/kaggle/input", "/kaggle/working"):
        if not os.path.isdir(root):
            continue
        # Prefer an exact 'episodes.jsonl' over the historical prefixed variants
        # (episodes_v2_prefix.jsonl and friends ship in the same dataset).
        for dirpath, _dirnames, filenames in os.walk(root):
            if "episodes.jsonl" in filenames:
                return os.path.join(dirpath, "episodes.jsonl")
    return None


def _on_kaggle() -> bool:
    return bool(os.environ.get("KAGGLE_KERNEL_RUN_TYPE")) or os.path.isdir("/kaggle/input")


def _default_out() -> str:
    return "/kaggle/working/proposed_update.json" if os.path.isdir("/kaggle/working") \
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), "proposed_update.json")


# ── generalizable pattern / tool extraction (mirrors fix A) ──────────
def _looks_like_literal_target(marker: str) -> bool:
    """Reject anything that pins a concrete destination — fix A (no memorizing)."""
    m = marker.lower()
    return "@" in m or "http://" in m or "https://" in m or m.startswith("www.")


def _candidate_patterns(missed: List[EpisodeFeatures]) -> List[str]:
    pats = set()
    for ep in missed:
        for marker in ep.flagged_markers:
            marker = marker.lower().strip()
            if marker and not _looks_like_literal_target(marker):
                pats.add(marker)
    return sorted(pats)


def _candidate_tools(missed: List[EpisodeFeatures]) -> List[str]:
    return sorted({ep.tool_name for ep in missed})


def _missed_under(episodes, policy) -> List[EpisodeFeatures]:
    out = []
    for ep in episodes:
        if ep.is_malicious and status_under_policy(ep, policy) not in ("blocked", "safe_continuation"):
            out.append(ep)
    return out


# ── GRPO ──────────────────────────────────────────────────────────────
# Two backends implementing the IDENTICAL algorithm — sample a group of
# thresholds from the current categorical policy, use the group mean as the
# baseline (advantage = reward − group_mean), and take a policy-gradient step on
# the logits. torch is used on Kaggle (GPU parity / room for larger policies);
# the pure-Python backend lets the exact same loop run on the 4 GB dev box,
# which has neither torch nor numpy. Both maximize expected reward.

def _base_rewards(episodes, grid, rc, min_intervention_eps, current):
    # Each grid threshold's mean batch reward (env is deterministic in the
    # threshold), minus a tiny minimal-intervention penalty proportional to the
    # distance from the CURRENT threshold. This breaks reward-ties toward the
    # smallest move: no gap → argmax stays at `current` → a no-op proposal
    # (which apply_update refuses), matching the v1 heuristic's "unchanged when
    # missed == false_pos". When a gap exists the reward difference dwarfs eps,
    # so it still moves — and among equally-good thresholds picks the one
    # closest to current (e.g. 1.5 → 1.0, not 1.5 → 0.0).
    return [evaluate_policy(episodes, Policy(ie_threshold=t), rc)["mean_reward"]
            - min_intervention_eps * abs(t - current) for t in grid]


def train_torch(episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed, current):
    import torch
    device = _torch_device()
    torch.manual_seed(seed)
    reward_t = torch.tensor(_base_rewards(episodes, grid, rc, min_intervention_eps, current),
                            dtype=torch.float32, device=device)
    logits = torch.zeros(len(grid), requires_grad=True, device=device)
    opt = torch.optim.Adam([logits], lr=lr)
    for _ in range(steps):
        dist = torch.distributions.Categorical(logits=logits)
        idx = dist.sample((group_size,))                   # a GRPO group
        advantages = reward_t[idx] - reward_t[idx].mean()  # group-relative baseline
        loss = -(advantages.detach() * dist.log_prob(idx)).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        probs = torch.softmax(logits, dim=0).cpu().tolist()
    return probs, _base_rewards(episodes, grid, rc, min_intervention_eps, current), device


def train_pure(episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed, current):
    import math, random
    random.seed(seed)
    base = _base_rewards(episodes, grid, rc, min_intervention_eps, current)
    n = len(grid)
    logits = [0.0] * n
    for _ in range(steps):
        m = max(logits)
        exps = [math.exp(l - m) for l in logits]
        Z = sum(exps)
        probs = [e / Z for e in exps]
        idxs = random.choices(range(n), weights=probs, k=group_size)  # GRPO group
        rewards = [base[i] for i in idxs]
        mean_r = sum(rewards) / len(rewards)                 # group-relative baseline
        grad = [0.0] * n
        for i, r in zip(idxs, rewards):
            adv = r - mean_r
            for j in range(n):                               # ∇ log π: [i==j] − p_j
                grad[j] += adv * ((1.0 if i == j else 0.0) - probs[j])
        logits = [l + lr * (g / group_size) for l, g in zip(logits, grad)]  # ascent
    m = max(logits)
    exps = [math.exp(l - m) for l in logits]
    Z = sum(exps)
    probs = [e / Z for e in exps]
    return probs, base, "cpu(pure-python)"


# ══════════════════════════════════════════════════════════════════════
#  JOINT ACTION SPACE (README §6n)
# ══════════════════════════════════════════════════════════════════════
#
# One scalar over five values made 3D an exhaustive search with the policy as
# decoration, and — worse — it could only express changes to a threshold that
# has no reachable gap on this corpus, so the loop was structurally incapable of
# proposing anything useful no matter how well it trained.
#
# The joint space is a product of per-dimension grids and is NOT enumerated: the
# policy is factored (one independent categorical per dimension) and GRPO samples
# groups of joint actions from it. Adding one marker to the corpus multiplies the
# space; the trainer's cost does not change.
#
# HOW THE DEFECT IS PREVENTED HERE — and why not by the prescribed remedy.
# The 1-D defect was argmax over noisy learned probabilities selecting an action
# whose own reward was lower than the incumbent's. The proposed fix was to raise
# `min_intervention_eps` until the penalty dominates the ~1e-2 probability noise.
# That does not work, and the arithmetic says so:
#
#   * the penalty lives in REWARD space, the noise lives in PROBABILITY space —
#     they are not commensurable, so "eps > noise" is not a meaningful inequality;
#   * the smallest genuine improvement is one episode changing outcome. The
#     smallest reward gap between two outcomes is 0.3 (correct_stop +1.0 ->
#     correct_block +0.7), so on 128 episodes a real single-episode gain is
#     0.3/128 = 0.0023 of mean reward. An eps of 1e-2 would therefore MASK every
#     improvement smaller than four episodes — trading a false-positive proposal
#     for silent false negatives, which is the worse failure for a security knob.
#
# So eps is instead auto-scaled to sit safely BELOW the smallest real gain
# (`_auto_intervention_eps`), and the noise is defended against directly by
# PROPOSE-AND-VERIFY: the policy proposes, then the exact batch reward of that
# proposal is compared against the incumbent's, and anything not strictly better
# becomes a no-op. That is two reward evaluations, not enumeration, so it scales
# to a space that cannot be enumerated — which is the point of this task.

# Dimension grids. Values are the ones the live components actually accept.
RISK_THRESHOLD_GRID = [0.4, 0.6, 0.8, 1.0]
WINDOW_SIZE_GRID    = [2, 3, 4, 5]
MARKER_WEIGHT_GRID  = [0.0, 0.5, 1.0]      # 1.0 reaches the default block_threshold


class ActionSpace:
    """
    Factored joint action space. `dims` is an ordered list of
    (name, [candidate values]); a joint action is one index per dimension.

    Marker dimensions are discovered from the batch rather than hard-coded, so a
    corpus that introduces a new screener marker automatically gets a knob.
    """

    def __init__(self, ie_grid_values: List[float], markers: List[str],
                 include_drift_dims: bool = True):
        self.dims: List[tuple] = [("ie_threshold", list(ie_grid_values))]
        if include_drift_dims:
            self.dims.append(("risk_threshold", list(RISK_THRESHOLD_GRID)))
            self.dims.append(("window_size", list(WINDOW_SIZE_GRID)))
        for m in markers:
            self.dims.append((f"marker_weight:{m}", list(MARKER_WEIGHT_GRID)))

    @property
    def names(self) -> List[str]:
        return [n for n, _ in self.dims]

    def sizes(self) -> List[int]:
        return [len(v) for _, v in self.dims]

    def cardinality(self) -> int:
        n = 1
        for s in self.sizes():
            n *= s
        return n

    def index_of(self, name: str, value) -> int:
        for n, vals in self.dims:
            if n == name:
                return vals.index(value)
        raise KeyError(name)

    def incumbent(self, current: "Policy") -> List[int]:
        """The joint action representing the policy currently in force."""
        idx = []
        for name, vals in self.dims:
            if name == "ie_threshold":
                idx.append(_nearest(vals, current.ie_threshold))
            elif name == "risk_threshold":
                idx.append(_nearest(vals, current.risk_threshold))
            elif name == "window_size":
                idx.append(_nearest(vals, current.window_size))
            else:
                marker = name.split(":", 1)[1]
                idx.append(_nearest(vals, current.marker_weights.get(marker, 0.0)))
        return idx

    def to_policy(self, action: List[int], base: "Policy") -> "Policy":
        weights = dict(base.marker_weights)
        ie, risk, window = base.ie_threshold, base.risk_threshold, base.window_size
        for (name, vals), i in zip(self.dims, action):
            v = vals[i]
            if name == "ie_threshold":
                ie = v
            elif name == "risk_threshold":
                risk = v
            elif name == "window_size":
                window = v
            else:
                weights[name.split(":", 1)[1]] = v
        return Policy(ie_threshold=ie, blocked_patterns=list(base.blocked_patterns),
                      high_impact_tools=list(base.high_impact_tools),
                      marker_weights=weights, block_threshold=base.block_threshold,
                      risk_threshold=risk, window_size=window)

    def describe(self, action: List[int]) -> dict:
        return {name: vals[i] for (name, vals), i in zip(self.dims, action)}


def _nearest(values: List, target) -> int:
    return min(range(len(values)), key=lambda i: abs(values[i] - target))


def discover_markers(episodes: List[EpisodeFeatures]) -> List[str]:
    """Every screener marker present in the batch, deterministically ordered."""
    seen = set()
    for ep in episodes:
        seen.update(ep.flagged_markers or [])
    return sorted(seen)


def _auto_intervention_eps(episodes: List[EpisodeFeatures], rc: RewardConfig) -> float:
    """
    A tie-breaking penalty small enough that it can never mask a genuine
    single-episode improvement.

    The smallest reward difference between two outcomes for one episode, divided
    by the batch size, is the smallest real gain expressible on this batch. The
    penalty for the largest possible move is set to a quarter of that.
    """
    values = [rc.correct_stop, rc.correct_block, rc.correct_pass,
              rc.missed_attack, rc.false_positive]
    gaps = [abs(a - b) for i, a in enumerate(values) for b in values[i + 1:] if a != b]
    smallest_real_gain = (min(gaps) if gaps else 0.3) / max(len(episodes), 1)
    return 0.25 * smallest_real_gain


def _normalized_distance(space: ActionSpace, action: List[int],
                         incumbent: List[int]) -> float:
    """Mean per-dimension normalized index distance, in [0, 1]."""
    if not space.dims:
        return 0.0
    total = 0.0
    for (_, vals), a, c in zip(space.dims, action, incumbent):
        span = max(len(vals) - 1, 1)
        total += abs(a - c) / span
    return total / len(space.dims)


def joint_reward(episodes: List[EpisodeFeatures], space: ActionSpace,
                 action: List[int], base: Policy, incumbent: List[int],
                 rc: RewardConfig, eps: float) -> float:
    """Exact batch reward for one joint action, minus the intervention penalty."""
    policy = space.to_policy(action, base)
    return (evaluate_policy(episodes, policy, rc)["mean_reward"]
            - eps * _normalized_distance(space, action, incumbent))


def train_joint_pure(episodes, space, base, incumbent, rc, group_size, steps, lr,
                     eps, seed):
    """
    GRPO over the factored joint policy, standard library only.

    One categorical per dimension; a joint action is sampled dimension-wise.
    Each step samples a group, scores each member with the exact reward, uses the
    group mean as the baseline (advantage = reward - group_mean, GRPO's defining
    move — no learned critic), and takes a REINFORCE step on every dimension's
    logits using that shared advantage.
    """
    import math, random
    random.seed(seed)
    sizes = space.sizes()
    logits = [[0.0] * s for s in sizes]

    def softmax(ls):
        m = max(ls)
        exps = [math.exp(l - m) for l in ls]
        Z = sum(exps)
        return [e / Z for e in exps]

    cache: dict = {}

    def reward(action):
        key = tuple(action)
        if key not in cache:
            cache[key] = joint_reward(episodes, space, list(key), base, incumbent, rc, eps)
        return cache[key]

    for _ in range(steps):
        probs = [softmax(ls) for ls in logits]
        group = [[random.choices(range(s), weights=p, k=1)[0]
                  for s, p in zip(sizes, probs)] for _ in range(group_size)]
        rewards = [reward(a) for a in group]
        baseline = sum(rewards) / len(rewards)
        grads = [[0.0] * s for s in sizes]
        for action, r in zip(group, rewards):
            adv = r - baseline
            for d, i in enumerate(action):
                for j in range(sizes[d]):        # ∇ log π: [i==j] − p_j
                    grads[d][j] += adv * ((1.0 if i == j else 0.0) - probs[d][j])
        logits = [[l + lr * (g / group_size) for l, g in zip(ls, gs)]
                  for ls, gs in zip(logits, grads)]

    probs = [softmax(ls) for ls in logits]
    return probs, "cpu(pure-python)", cache


def train_joint_torch(episodes, space, base, incumbent, rc, group_size, steps, lr,
                      eps, seed):
    """Same algorithm on torch (Kaggle P100); reward stays a Python callable."""
    import torch
    device = _torch_device()
    torch.manual_seed(seed)
    sizes = space.sizes()
    logits = [torch.zeros(s, requires_grad=True, device=device) for s in sizes]
    opt = torch.optim.Adam(logits, lr=lr)
    cache: dict = {}

    def reward(action):
        key = tuple(action)
        if key not in cache:
            cache[key] = joint_reward(episodes, space, list(key), base, incumbent, rc, eps)
        return cache[key]

    for _ in range(steps):
        dists = [torch.distributions.Categorical(logits=l) for l in logits]
        samples = [d.sample((group_size,)) for d in dists]
        group = [[int(s[g]) for s in samples] for g in range(group_size)]
        rewards = torch.tensor([reward(a) for a in group], dtype=torch.float32, device=device)
        advantages = (rewards - rewards.mean()).detach()
        logp = sum(d.log_prob(s) for d, s in zip(dists, samples))
        loss = -(advantages * logp).mean()
        opt.zero_grad(); loss.backward(); opt.step()

    with torch.no_grad():
        probs = [torch.softmax(l, dim=0).cpu().tolist() for l in logits]
    return probs, device, cache


def train_joint(episodes: List[EpisodeFeatures], space: ActionSpace, base: Policy,
                rc: RewardConfig, group_size: int = 12, steps: int = 400,
                lr: float = 0.1, min_intervention_eps: Optional[float] = None,
                seed: int = 0, backend: str = "auto"):
    """
    Train the joint policy and return a VERIFIED proposal.

    Returns (chosen_action, probs, incumbent, eps, device, diagnostics).

    The proposal is the policy's argmax, gated by propose-and-verify: it is
    accepted only if its exact batch reward strictly beats the incumbent's.
    Two evaluations — no enumeration — so this is the same guard whether the
    space has 60 joint actions or 10^6.
    """
    incumbent = space.incumbent(base)
    eps = _auto_intervention_eps(episodes, rc) if min_intervention_eps is None \
        else min_intervention_eps

    trainer = train_joint_torch if (backend == "torch" or
                                    (backend == "auto" and _torch_available())) \
        else train_joint_pure
    probs, device, cache = trainer(episodes, space, base, incumbent, rc,
                                   group_size, steps, lr, eps, seed)

    policy_choice = [max(range(len(p)), key=lambda i: p[i]) for p in probs]

    r_incumbent = joint_reward(episodes, space, incumbent, base, incumbent, rc, eps)
    r_choice = joint_reward(episodes, space, policy_choice, base, incumbent, rc, eps)

    accepted = r_choice > r_incumbent

    # MINIMALITY PASS. Verification accepts or rejects the joint action as a
    # whole, so a dimension that moved for no reason rides along with one that
    # earned its move — the first run of this trainer proposed ie_threshold
    # 0.5 -> 1.0 (worth exactly nothing, the reward is flat there) bundled with
    # the marker weight that carried the entire gain. That is the same class of
    # defect as the 1-D one: an unjustified change to a security knob, arriving
    # inside a justified proposal where it is harder to notice.
    #
    # So each moved dimension is greedily reverted to the incumbent and kept
    # reverted unless the revert costs reward. One evaluation per dimension, so
    # this stays linear in dimensions rather than in the size of the space.
    chosen = list(policy_choice) if accepted else list(incumbent)
    reverted = []
    if accepted:
        best = r_choice
        for d in range(len(space.dims)):
            if chosen[d] == incumbent[d]:
                continue
            trial = list(chosen)
            trial[d] = incumbent[d]
            r_trial = joint_reward(episodes, space, trial, base, incumbent, rc, eps)
            if r_trial >= best:
                chosen, best = trial, r_trial
                reverted.append(space.dims[d][0])
        r_choice = best

    diagnostics = {
        "reward_incumbent": r_incumbent,
        "reward_policy_choice": r_choice,
        "policy_choice": space.describe(policy_choice),
        "verified_accepted": accepted,
        "reverted_as_unnecessary": reverted,
        "intervention_eps": eps,
        "joint_actions_evaluated": len(cache),
        "joint_space_cardinality": space.cardinality(),
        "flat_dimensions": _flat_dimensions(episodes, space, base, incumbent, rc, eps),
    }
    return chosen, probs, incumbent, eps, device, diagnostics


def _flat_dimensions(episodes, space, base, incumbent, rc, eps) -> List[str]:
    """
    Dimensions along which the batch reward does not move at all — i.e. the data
    cannot identify them. Reported rather than silently trained: on campaign
    episodes `risk_threshold` and `window_size` are always flat, because every
    case runs under a unique session_id so the temporal-drift rule never fires.
    """
    flat = []
    for d, (name, vals) in enumerate(space.dims):
        rewards = set()
        for i in range(len(vals)):
            action = list(incumbent)
            action[d] = i
            policy = space.to_policy(action, base)
            rewards.add(round(evaluate_policy(episodes, policy, rc)["mean_reward"], 10))
        if len(rewards) == 1:
            flat.append(name)
    return flat


def train(episodes: List[EpisodeFeatures], grid: List[float],
          current_ie_threshold: float, rc: RewardConfig,
          group_size: int = 8, steps: int = 300, lr: float = 0.1,
          min_intervention_eps: float = 1e-3, seed: int = 0,
          backend: str = "auto"):
    if backend == "torch" or (backend == "auto" and _torch_available()):
        probs, base_rewards, device = train_torch(
            episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed,
            current_ie_threshold)
    else:
        probs, base_rewards, device = train_pure(
            episodes, grid, rc, group_size, steps, lr, min_intervention_eps, seed,
            current_ie_threshold)
    # 1-D PATH ONLY. Decide on the exact reward table, not on the learned
    # probabilities. This is a regression guard for the single-scalar case, kept
    # because the 5-point grid is trivially enumerable and the defect below must
    # never recur here. It is deliberately NOT the decision rule in the joint
    # space (train_joint), which cannot be enumerated — there the equivalent
    # protection is propose-and-verify against the incumbent, two evaluations.
    #
    # The env is deterministic in the threshold and the grid has 5 points, so
    # `base_rewards` IS the quantity the policy is estimating — computed exactly,
    # already carrying the minimal-intervention penalty. `probs` is a noisy
    # estimator of the same thing after 300 sampled REINFORCE steps.
    #
    # Deciding on the noisy one is not merely inelegant, it proposes changes the
    # data does not support. Measured on the 128-episode corpus (README §6n):
    # rewards at 0.0 / 0.5 / 1.0 are tied at +0.868 (missed = 5 at all three)
    # while 1.5 / 2.0 drop to +0.664 — so the policy correctly learned to avoid
    # the high thresholds (0.27/0.26/0.26/0.11/0.10), but among the three tied
    # ones its probabilities differed by ~0.01 of sampling noise, which swamped
    # the 1e-3 intervention penalty and made argmax(probs) select 0.0. That is a
    # proposal to lower a security threshold for no measured benefit, and
    # `apply_update` would have accepted it as a real change.
    #
    # The policy is still trained and still reported — it is the evidence that
    # the reward structure was learnable rather than merely tabulated — but the
    # proposal comes from the exact optimum. On a larger or continuous policy
    # space this shortcut would not be available and the policy would have to
    # decide.
    chosen = grid[int(max(range(len(grid)), key=lambda i: base_rewards[i]))]

    policy_choice = grid[int(max(range(len(grid)), key=lambda i: probs[i]))]
    if policy_choice != chosen:
        print(f"[grpo] note: policy argmax ({policy_choice}) != reward argmax "
              f"({chosen}); rewards differ by "
              f"{abs(max(base_rewards) - base_rewards[grid.index(policy_choice)]):.4f}. "
              f"Deciding on the exact reward — see train() for why.")
    return chosen, probs, base_rewards, device


def _torch_available() -> bool:
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


def _torch_device() -> str:
    """
    Pick a device torch can actually allocate on, not merely one it reports.

    `torch.cuda.is_available()` answers "is there a CUDA driver and a visible
    device", which is not the same question as "can this build run code on it".
    Kaggle's P100 is compute capability sm_60 and the PyTorch shipped in the
    kernel image supports sm_70 and above, so `is_available()` returns True and
    the first allocation then dies with:

        CUDA error: no kernel image is available for execution on the device

    That killed a run after the trainer had already loaded its episodes and
    announced `backend=torch`. Probe with a real allocation and fall back to CPU
    on any failure.

    Falling back costs nothing measurable here: the joint search is a few
    thousand float operations over a 188-row table and completes in well under a
    second on CPU. The GPU was never load-bearing for this workload — the reason
    to run on Kaggle at all is that it is the only environment where torch is
    importable, so the torch code path can be executed and cross-checked against
    the pure-Python one.
    """
    import torch
    if not torch.cuda.is_available():
        return "cpu"
    try:
        torch.zeros(1, device="cuda") + 1
        return "cuda"
    except Exception as e:                                   # noqa: BLE001
        name = "unknown"
        try:
            name = torch.cuda.get_device_name(0)
        except Exception:                                    # noqa: BLE001
            pass
        print(f"[grpo] CUDA reported available ({name}) but cannot execute: "
              f"{type(e).__name__}: {str(e).splitlines()[0]}")
        print("[grpo] falling back to CPU — this workload does not need a GPU; "
              "the point of running here is that torch is importable at all.")
        return "cpu"


def compare_backends(episodes, space, base, rc, args) -> int:
    """
    Run BOTH backends on identical data and report whether they agree.

    The algorithm is implemented twice — once in torch for the accelerator and
    once in the standard library so it can run on the 4 GB development box — and
    until this ran, the torch path had never been executed at all: there is no
    torch locally, and tests/test_grpo_kaggle.py is explicitly torch-free. Two
    implementations of one algorithm that have never been compared are two
    algorithms.

    What is compared, and why it is not the learned probabilities. Both backends
    sample from their own RNG (torch's generator vs the stdlib's `random`), so
    the sampled trajectories differ even at a fixed seed and the learned
    distributions cannot be expected to match bit for bit. What MUST match is
    everything downstream of the reward function, because that part is exact
    arithmetic over the same episodes:

      * the incumbent's reward, and the reward of whatever each backend chose
      * the accept/reject verdict from propose-and-verify
      * the final chosen action

    A disagreement on the chosen action while the rewards agree means the two
    policies landed in different places on a flat or near-flat reward surface —
    which is a finding about the surface, not a bug, and is reported as such. A
    disagreement on the REWARDS is a genuine defect: the same action scored
    differently by the same reward function under two backends.

    Returns a process exit code so the Kaggle kernel fails loudly on a
    reward-level disagreement rather than burying it in stdout.
    """
    if not _torch_available():
        print("[compare] torch is not importable here — this mode only means "
              "anything on a machine that has it (i.e. the Kaggle kernel).")
        return 2

    results = {}
    for backend in ("pure", "torch"):
        chosen, probs, incumbent, eps, device, diag = train_joint(
            episodes, space, base, rc,
            group_size=args.group_size, steps=args.steps, lr=args.lr,
            min_intervention_eps=None, seed=args.seed, backend=backend)
        results[backend] = {
            "chosen": list(chosen), "incumbent": list(incumbent),
            "device": device, "eps": eps,
            "probs": probs,
            "policy_choice": [max(range(len(p)), key=lambda i: p[i]) for p in probs],
            "r_incumbent": diag["reward_incumbent"],
            "r_choice": diag["reward_policy_choice"],
            "accepted": diag["verified_accepted"],
            "action": space.describe(chosen),
        }

    p, t = results["pure"], results["torch"]
    print("\n" + "=" * 74)
    print("  BACKEND AGREEMENT — torch vs pure-python, identical episodes")
    print("=" * 74)
    for name, r in (("pure-python", p), ("torch", t)):
        print(f"  {name:<12} device={r['device']:<18} accepted={r['accepted']}")
        print(f"  {'':<12} r_incumbent={r['r_incumbent']:+.6f}  "
              f"r_choice={r['r_choice']:+.6f}")
        print(f"  {'':<12} chosen={r['action']}")

    # WHAT MAY AND MAY NOT BE COMPARED.
    #
    # An earlier version of this check compared `r_choice` across backends and
    # reported FAIL on a 6.6e-06 gap. That was wrong, and wrong in an instructive
    # way: `r_choice` is the reward of *each backend's own policy choice*, and
    # the two backends draw from different RNGs, so they generally choose
    # different actions. Comparing those two numbers compares the rewards of two
    # different things and will "fail" whenever the policies diverge — which is
    # expected behaviour, not a defect. The check was accusing the trainer of a
    # bug that lived in the check.
    #
    # The invariants that DO hold:
    #   1. r_incumbent is the same action scored by the same function on both
    #      sides, so it must agree exactly.
    #   2. Each backend's reported r_choice must match an INDEPENDENT
    #      recomputation of the action that backend chose. This is the real test
    #      of the torch path: it catches a backend that mis-scores or misreports,
    #      without demanding that two stochastic searches land in the same place.
    #   3. The accept/reject verdict and final chosen action should agree.
    incumbent = p["incumbent"]
    gap_incumbent = abs(p["r_incumbent"] - t["r_incumbent"])
    rewards_agree = gap_incumbent < 1e-9

    recomputed = {}
    for name, r in (("pure", p), ("torch", t)):
        recomputed[name] = joint_reward(episodes, space, r["policy_choice"],
                                        base, incumbent, rc, r["eps"])
    self_gap = max(abs(recomputed["pure"] - p["r_choice"]),
                   abs(recomputed["torch"] - t["r_choice"]))
    self_consistent = self_gap < 1e-9

    verdict_agree = p["accepted"] == t["accepted"]
    action_agree = p["chosen"] == t["chosen"]
    same_policy_choice = p["policy_choice"] == t["policy_choice"]

    print(f"\n  incumbent reward agrees (<1e-9) : {rewards_agree}   "
          f"(gap {gap_incumbent:.3e})")
    print(f"  each backend's reported reward matches an independent")
    print(f"    recomputation of the action it chose  : {self_consistent}   "
          f"(max gap {self_gap:.3e})")
    print(f"  accept/reject verdict agrees    : {verdict_agree}")
    print(f"  final chosen action agrees      : {action_agree}")
    print(f"  (policies picked the same argmax: {same_policy_choice} — "
          f"different RNGs, so this is not required)")

    if not rewards_agree:
        print("\n  FAIL — the incumbent scores differently under the two "
              "backends. That is one action through one function, so this is a "
              "defect, not sampling noise.")
        return 1
    if not self_consistent:
        print("\n  FAIL — a backend reported a reward that does not match an "
              "independent recomputation of the action it chose. The backend is "
              "misreporting its own result.")
        return 1
    if not (verdict_agree and action_agree):
        print("\n  Rewards are consistent, but the two backends reached "
              "different final proposals. On a flat reward surface two "
              "stochastic searches can settle on different equally-scored "
              "actions — report it, do not 'fix' it.")
        return 0

    print("\n  OK — the two implementations agree end to end.")
    return 0


def build_proposal(episodes, chosen_threshold, current_ie_threshold,
                   probs, grid, rc, device) -> dict:
    """Assemble a ProposedUpdate-schema dict from the learned threshold."""
    final_policy = Policy(ie_threshold=chosen_threshold)
    missed_after = _missed_under(episodes, final_policy)
    patterns = _candidate_patterns(missed_after)
    tools = _candidate_tools(missed_after)
    stats = evaluate_policy(episodes, final_policy, rc)

    rationale = [
        f"GRPO over IE grid {grid} on {len(episodes)} labeled episode(s) "
        f"[device={device}]",
        f"learned distribution: " +
        ", ".join(f"{g:.1f}:{p:.2f}" for g, p in zip(grid, probs)),
        f"chosen ie_threshold {current_ie_threshold:.2f} -> {chosen_threshold:.2f} "
        f"(argmax of the exact reward table; the learned policy is reported "
        f"above as evidence, but does not decide — see train())",
        f"post-update batch: mean_reward={stats['mean_reward']:+.3f} "
        f"missed={stats['missed']} false_pos={stats['false_pos']} "
        f"workflow_lost={stats['workflow_lost']}",
    ]
    if patterns:
        rationale.append(f"generalizable blocked_patterns from still-missed attacks: {patterns}")
    if tools:
        rationale.append(f"tools in still-missed attacks, nominate high-impact: {tools}")

    return {
        "old_ie_threshold": current_ie_threshold,
        "new_ie_threshold": chosen_threshold,
        "new_blocked_patterns": patterns,
        "new_high_impact_tools": tools,
        "rationale": rationale,
        "mean_reward": stats["mean_reward"],
        # provenance (ignored by apply_update; recorded for the report)
        "_meta": {
            "trainer": "grpo",
            "grid": grid,
            "learned_probs": probs,
            "device": device,
            "n_episodes": len(episodes),
        },
    }


def _run_joint(episodes, grid, current, rc, args, out_path, resolved):
    """Joint-action-space training path (§6n) — see train_joint()."""
    markers = discover_markers(episodes)
    space = ActionSpace(grid, markers)
    base = Policy(ie_threshold=current)

    print(f"[grpo] JOINT action space: {len(space.dims)} dimensions, "
          f"{space.cardinality()} joint actions")
    for name, vals in space.dims:
        print(f"          {name:<28} {vals}")

    chosen, probs, incumbent, eps, device, diag = train_joint(
        episodes, space, base, rc,
        group_size=args.group_size, steps=args.steps, lr=args.lr,
        min_intervention_eps=(args.min_intervention_eps
                              if args.min_intervention_eps != 1e-3 else None),
        seed=args.seed, backend=args.backend)

    print(f"\n[grpo] intervention eps (auto-scaled below the smallest real "
          f"single-episode gain) = {eps:.6f}")
    print(f"[grpo] joint actions actually evaluated: {diag['joint_actions_evaluated']}"
          f" of {diag['joint_space_cardinality']} (sampled, not enumerated)")
    if diag["flat_dimensions"]:
        print(f"[grpo] UNIDENTIFIABLE on this batch (reward exactly flat): "
              f"{diag['flat_dimensions']}")
        print(f"          campaigns use a unique session_id per case, so the "
              f"temporal-drift rule never fires and its knobs cannot be learned.")

    print(f"\n[grpo] learned per-dimension distribution:")
    for (name, vals), p in zip(space.dims, probs):
        top = max(range(len(p)), key=lambda i: p[i])
        print(f"        {name:<28} " +
              " ".join(f"{v}:{pi:.2f}" for v, pi in zip(vals, p)) +
              f"   argmax={vals[top]}")

    print(f"\n[grpo] propose-and-verify:")
    print(f"        incumbent      reward={diag['reward_incumbent']:+.4f}  "
          f"{space.describe(incumbent)}")
    print(f"        policy choice  reward={diag['reward_policy_choice']:+.4f}  "
          f"{diag['policy_choice']}")
    print(f"        -> {'ACCEPTED' if diag['verified_accepted'] else 'REJECTED (no-op)'}")
    if diag["reverted_as_unnecessary"]:
        print(f"        minimality pass reverted (moved for no reward): "
              f"{diag['reverted_as_unnecessary']}")

    chosen_policy = space.to_policy(chosen, base)
    after = evaluate_policy(episodes, chosen_policy, rc)
    print(f"\n[grpo] chosen joint action: {space.describe(chosen)}")
    print(f"[grpo] post-update batch: mean_reward={after['mean_reward']:+.3f} "
          f"missed={after['missed']} false_pos={after['false_pos']} "
          f"workflow_lost={after['workflow_lost']}")

    # The ie_threshold dimension's own distribution — not a flattened mash of
    # every dimension's first bucket, which is what an earlier version passed.
    ie_probs = probs[space.names.index("ie_threshold")]
    proposal = build_proposal(episodes, chosen_policy.ie_threshold, current,
                              ie_probs, grid, rc, device)
    proposal["joint"] = {
        "action_space": {n: v for n, v in space.dims},
        "chosen": space.describe(chosen),
        "incumbent": space.describe(incumbent),
        "per_dimension_probs": {n: p for (n, _), p in zip(space.dims, probs)},
        "diagnostics": diag,
        "post_update": after,
    }
    # build_proposal summarises the SCALAR path; drop its post-update line and
    # restate the outcome under the JOINT policy, so one file cannot carry two
    # disagreeing summaries.
    proposal["rationale"] = [
        r for r in proposal.get("rationale", [])
        if "argmax of the exact reward table" not in r
        and "post-update batch" not in r
    ] + [
        f"- post-update batch under the JOINT policy: "
        f"mean_reward={after['mean_reward']:+.3f} missed={after['missed']} "
        f"false_pos={after['false_pos']} workflow_lost={after['workflow_lost']}",
        f"- JOINT action space ({len(space.dims)} dims, "
        f"{space.cardinality()} actions): {space.describe(chosen)}",
        f"- decided by the learned policy, then verified against the incumbent "
        f"({diag['reward_policy_choice']:+.4f} vs {diag['reward_incumbent']:+.4f}) — "
        f"{'accepted' if diag['verified_accepted'] else 'rejected, proposing a no-op'}",
    ]
    if diag["reverted_as_unnecessary"]:
        proposal["rationale"].append(
            f"- minimality pass reverted dimensions that moved for no reward: "
            f"{', '.join(diag['reverted_as_unnecessary'])}")
    if diag["flat_dimensions"]:
        proposal["rationale"].append(
            f"- unidentifiable on this batch (reward exactly flat): "
            f"{', '.join(diag['flat_dimensions'])}")

    with open(out_path, "w") as f:
        json.dump(proposal, f, indent=2)
    print(f"[grpo] wrote {out_path}")
    for r in proposal["rationale"]:
        print(f"        {r}")


def main():
    ap = argparse.ArgumentParser(description="GRPO trainer for Component 3D (Kaggle P100)")
    ap.add_argument("--episodes", default=None, help="path to packaged episodes.jsonl")
    ap.add_argument("--out", default=None, help="output proposed_update.json path")
    ap.add_argument("--current-ie-threshold", type=float, default=None,
                    help="threshold to move from (default: mode of capture_ie_threshold)")
    ap.add_argument("--ie-resolution", type=float, default=0.5)
    ap.add_argument("--group-size", type=int, default=8)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--lr", type=float, default=0.1)
    ap.add_argument("--min-intervention-eps", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--backend", choices=["auto", "torch", "pure"], default="auto",
                    help="auto uses torch when importable (Kaggle), else pure-python")
    ap.add_argument("--action-space", choices=["scalar", "joint"], default="joint",
                    help="'joint' trains over ie_threshold + risk_threshold + "
                         "window_size + per-marker Policy Engine weights (§6n); "
                         "'scalar' is the legacy ie_threshold-only path")
    ap.add_argument("--compare-backends", action="store_true",
                    help="run BOTH backends on identical data and check they "
                         "agree on rewards, verdict and chosen action. Only "
                         "meaningful where torch exists (the Kaggle kernel); "
                         "exits non-zero on a reward-level disagreement.")
    args = ap.parse_args()

    # Kaggle runs this file as a bare script and passes no arguments, so a flag
    # that only ever arrives via the CLI can never fire in the one environment
    # where it means anything. The accelerator run is the sole opportunity to
    # execute the torch backend at all, so take it automatically.
    if _on_kaggle() and not args.compare_backends:
        print("[grpo] Kaggle kernel detected → enabling --compare-backends "
              "(the only place torch is importable).")
        args.compare_backends = True

    episodes_path = args.episodes or _find_episodes()
    if not episodes_path:
        sys.exit("[grpo] no episodes.jsonl found — run package_episodes.py first, "
                 "or pass --episodes.")
    out_path = args.out or _default_out()

    episodes = load_episodes(episodes_path)
    if not episodes:
        sys.exit(f"[grpo] {episodes_path} is empty.")

    # Default the starting threshold to what the data was captured at.
    if args.current_ie_threshold is not None:
        current = args.current_ie_threshold
    else:
        caps = [ep.causal["capture_ie_threshold"] for ep in episodes
                if ep.causal and ep.causal.get("capture_ie_threshold") is not None]
        current = mode(caps) if caps else 0.5

    grid = ie_grid(args.ie_resolution)
    rc = RewardConfig()

    backend = args.backend
    if backend == "torch" and not _torch_available():
        sys.exit("[grpo] --backend torch requested but torch is not importable.")
    resolved = "torch" if (backend == "torch" or (backend == "auto" and _torch_available())) \
        else "pure-python"

    print(f"[grpo] episodes={len(episodes)} from {episodes_path}")
    print(f"[grpo] IE grid={grid}  current ie_threshold={current}  backend={resolved}")

    if args.compare_backends:
        space = ActionSpace(grid, discover_markers(episodes))
        rc_ = rc
        code = compare_backends(episodes, space, Policy(ie_threshold=current), rc_, args)
        # Still emit the normal proposal afterwards, so the kernel produces its
        # deliverable even when it is also acting as a cross-check.
        _run_joint(episodes, grid, current, rc, args, out_path, resolved)
        sys.exit(code)

    if args.action_space == "joint":
        _run_joint(episodes, grid, current, rc, args, out_path, resolved)
        return

    chosen, probs, base_rewards, device = train(
        episodes, grid, current, rc,
        group_size=args.group_size, steps=args.steps, lr=args.lr,
        min_intervention_eps=args.min_intervention_eps, seed=args.seed,
        backend=backend)

    print(f"[grpo] per-threshold mean reward (+ intervention bonus):")
    for g, r in zip(grid, base_rewards):
        print(f"        ie_threshold={g:.1f}  reward={r:+.4f}")
    print(f"[grpo] learned argmax ie_threshold = {chosen}  (was {current})")

    proposal = build_proposal(episodes, chosen, current, probs, grid, rc, device)
    with open(out_path, "w") as f:
        json.dump(proposal, f, indent=2)
    print(f"[grpo] wrote {out_path}")
    for line in proposal["rationale"]:
        print(f"        - {line}")


if __name__ == "__main__":
    main()
