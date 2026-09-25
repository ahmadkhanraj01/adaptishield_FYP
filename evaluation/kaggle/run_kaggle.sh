#!/usr/bin/env bash
#
# Path A driver (Phase.md §6): push the labeled-episode dataset + the GRPO
# kernel to Kaggle, run it on a free P100, and pull the trained ProposedUpdate
# back — all from this session, no browser round-trips per cycle.
#
# The ONLY manual prerequisite is the API token (Phase.md §6): kaggle.com →
# Settings → API → Create New Token, then
#   ! mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
# Everything below is automatic once that file exists. The Kaggle username is
# read from kaggle.json, so no id needs hand-editing.
#
# Usage:
#   bash evaluation/kaggle/run_kaggle.sh            # full push → run → pull
#   bash evaluation/kaggle/run_kaggle.sh --pull     # just re-pull the last output
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
DATASET_DIR="$HERE/dataset"
KERNEL_DIR="$HERE/kernel"
OUT_DIR="$HERE/output"
# Credential file location. A kaggle.json downloaded from the browser most often
# lands in the project directory the user is working in, not in ~/.kaggle, so
# check the repo root too and point the CLI at whichever we find — otherwise the
# run fails with "Unauthenticated" while a perfectly good key sits two
# directories away. (.gitignore excludes kaggle.json anywhere in the tree.)
if [ -z "${KAGGLE_CONFIG_DIR:-}" ] && [ -f "$ROOT/kaggle.json" ]; then
  export KAGGLE_CONFIG_DIR="$ROOT"
fi
KJSON="${KAGGLE_CONFIG_DIR:-$HOME/.kaggle}/kaggle.json"

# Use the project venv's kaggle CLI + python3.
if [ -f "$ROOT/venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$ROOT/venv/bin/activate"
fi
PY="$(command -v python3)"
KAGGLE="$(command -v kaggle)"

# Load repo-root .env if present (KAGGLE_USERNAME / KAGGLE_KEY live here).
if [ -f "$ROOT/.env" ]; then
  set -a; # shellcheck disable=SC1091
  source "$ROOT/.env"; set +a
fi

# ── preflight: credentials ───────────────────────────────────────────
# The installed CLI (1.7.4.5) uses a username+key pair. Two ways to supply it:
#   (a) .env / environment: KAGGLE_USERNAME + KAGGLE_KEY  (preferred, this repo)
#   (b) ~/.kaggle/kaggle.json  (fallback, standard location)
# The new "API Tokens" access tokens need CLI >= 1.8.0 and are NOT supported.
if [ -n "${KAGGLE_USERNAME:-}" ] && [ -n "${KAGGLE_KEY:-}" ]; then
  USERNAME="$KAGGLE_USERNAME"
  echo "[run_kaggle] using KAGGLE_USERNAME/KAGGLE_KEY from environment/.env"
elif [ -f "$KJSON" ]; then
  chmod 600 "$KJSON" 2>/dev/null || true
  USERNAME="$("$PY" -c "import json;print(json.load(open('$KJSON'))['username'])")"
  echo "[run_kaggle] using credentials from $KJSON"
else
  cat >&2 <<EOF
[run_kaggle] No Kaggle credentials found.
  The installed CLI (1.7.4.5) needs a legacy USERNAME + KEY (not the new
  "API Tokens" access token, which requires CLI >= 1.8.0). Get them from
  kaggle.com → Settings → API → (legacy section) → Create New Token, then
  EITHER put them in the repo-root .env:
    cp evaluation/kaggle/.env.example .env   &&   \$EDITOR .env
  OR drop the downloaded kaggle.json at $KJSON (chmod 600).
EOF
  exit 1
fi
DATASET_ID="$USERNAME/adaptishield-episodes"
KERNEL_ID="$USERNAME/adaptishield-grpo-3d"
echo "[run_kaggle] user=$USERNAME  dataset=$DATASET_ID  kernel=$KERNEL_ID"

# ── --pull shortcut ──────────────────────────────────────────────────
if [ "${1:-}" = "--pull" ]; then
  mkdir -p "$OUT_DIR"
  "$KAGGLE" kernels output "$KERNEL_ID" -p "$OUT_DIR"
  echo "[run_kaggle] pulled -> $OUT_DIR/proposed_update.json"
  exit 0
fi

# ── stage dataset (episodes.jsonl must already exist) ────────────────
if [ ! -f "$DATASET_DIR/episodes.jsonl" ]; then
  echo "[run_kaggle] $DATASET_DIR/episodes.jsonl missing — build it first:" >&2
  echo "    python -m evaluation.kaggle.package_episodes --run-campaign" >&2
  exit 1
fi
cp "$HERE/grpo_env.py" "$DATASET_DIR/grpo_env.py"          # trainer imports this on Kaggle
"$PY" - "$DATASET_DIR/dataset-metadata.json" "$DATASET_ID" <<'PYEOF'
import json, sys
path, ds_id = sys.argv[1], sys.argv[2]
try:
    meta = json.load(open(path))
except FileNotFoundError:
    meta = {"title": "AdaptiShield 3D labeled episodes", "licenses": [{"name": "CC0-1.0"}]}
meta["id"] = ds_id
json.dump(meta, open(path, "w"), indent=2)
PYEOF

# ── stage kernel (generate a fresh staging dir from the template) ────
# KERNEL_DIR is generated + git-ignored; the committed source of truth is
# kernel-metadata.template.json. Regenerating (never mutating the template)
# keeps this idempotent across runs and usernames.
mkdir -p "$KERNEL_DIR"
cp "$HERE/grpo_train.py" "$KERNEL_DIR/grpo_train.py"
sed "s#__USERNAME__#$USERNAME#g" "$HERE/kernel-metadata.template.json" \
    > "$KERNEL_DIR/kernel-metadata.json"

# ── push dataset (create first time, version after) ──────────────────
if "$KAGGLE" datasets status "$DATASET_ID" >/dev/null 2>&1; then
  echo "[run_kaggle] dataset exists → new version"
  "$KAGGLE" datasets version -p "$DATASET_DIR" -m "episodes $(date -u +%FT%TZ)" --dir-mode zip
else
  echo "[run_kaggle] dataset new → create"
  "$KAGGLE" datasets create -p "$DATASET_DIR" --dir-mode zip
fi

# ── wait for the dataset to finish processing ────────────────────────
# Upload returns as soon as the bytes are accepted, but Kaggle then processes
# the version asynchronously and only mounts it into /kaggle/input once it is
# "ready". Pushing the kernel immediately is a race the kernel loses: it starts
# against an empty input directory and dies with
#   ModuleNotFoundError: No module named 'grpo_env'
# which reads like a packaging bug and is not one. Observed on the first real
# run, 2026-07-26.
echo "[run_kaggle] waiting for the dataset to become ready…"
for i in $(seq 1 60); do
  DS_STATUS="$("$KAGGLE" datasets status "$DATASET_ID" 2>/dev/null | tr -d '\r' || true)"
  case "$(printf '%s' "$DS_STATUS" | tr '[:upper:]' '[:lower:]')" in
    *ready*)
      echo "[run_kaggle] dataset ready (after ~$((i * 10))s)"
      break ;;
    *error*|*fail*)
      echo "[run_kaggle] dataset processing failed: $DS_STATUS" >&2
      exit 1 ;;
  esac
  if [ "$i" -eq 60 ]; then
    echo "[run_kaggle] dataset still not ready after 10 min (last: $DS_STATUS)" >&2
    exit 1
  fi
  sleep 10
done

# ── push kernel + poll to completion ─────────────────────────────────
echo "[run_kaggle] pushing kernel…"
"$KAGGLE" kernels push -p "$KERNEL_DIR"

# The CLI reports e.g. '... has status "KernelWorkerStatus.ERROR"' — UPPERCASE.
# The patterns here were lowercase and `case` is case-sensitive, so NEITHER the
# success nor the failure branch could ever match: the loop ran its full 60
# iterations against a kernel that had already died, fell through, downloaded
# whatever happened to exist, printed "done" and exited 0. A failed run was
# reported as a successful one. Lowercase the status before matching, and treat
# "fell out of the loop" as a timeout rather than as success.
echo "[run_kaggle] waiting for the kernel to finish…"
KSTATE="timeout"
for _ in $(seq 1 60); do
  sleep 20
  STATUS="$("$KAGGLE" kernels status "$KERNEL_ID" 2>/dev/null | tr -d '\r' || true)"
  echo "    $STATUS"
  case "$(printf '%s' "$STATUS" | tr '[:upper:]' '[:lower:]')" in
    *complete*)          KSTATE="complete"; break ;;
    *error*|*cancel*)    KSTATE="failed";   break ;;
  esac
done

mkdir -p "$OUT_DIR"

if [ "$KSTATE" != "complete" ]; then
  echo "[run_kaggle] kernel did not complete (state: $KSTATE) — pulling the log" >&2
  "$KAGGLE" kernels output "$KERNEL_ID" -p "$OUT_DIR" || true
  echo "[run_kaggle] log: $OUT_DIR/${KERNEL_ID#*/}.log" >&2
  exit 1
fi

# ── pull the ProposedUpdate ──────────────────────────────────────────
"$KAGGLE" kernels output "$KERNEL_ID" -p "$OUT_DIR"
if [ ! -f "$OUT_DIR/proposed_update.json" ]; then
  echo "[run_kaggle] kernel reported COMPLETE but produced no proposed_update.json" >&2
  exit 1
fi
echo "[run_kaggle] done → $OUT_DIR/proposed_update.json"
echo "[run_kaggle] apply it:  python -m evaluation.kaggle.apply_and_validate --proposal $OUT_DIR/proposed_update.json"
