"""
Tiny Kaggle credential check — does the token in repo-root .env actually work?

Loads KAGGLE_USERNAME / KAGGLE_KEY from .env (no secret is ever printed), then
makes ONE lightweight authenticated API call. Prints PASS/FAIL only.

  python -m evaluation.kaggle.test_credentials
"""

import os
import sys


def _load_dotenv(path):
    """Minimal .env loader (project is dependency-free — no python-dotenv)."""
    if not os.path.exists(path):
        return False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)
    return True


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    env_path = os.path.join(root, ".env")

    loaded = _load_dotenv(env_path)
    print(f"[test] .env {'loaded from ' + env_path if loaded else 'NOT FOUND at ' + env_path}")

    user = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    if not user or not key:
        print("[test] FAIL — KAGGLE_USERNAME / KAGGLE_KEY not set "
              "(check .env has both, no quotes needed).")
        sys.exit(1)
    # Show only the username and a masked key length — never the secret itself.
    print(f"[test] username={user!r}  key=<{len(key)} chars, hidden>")

    # Env vars must be set BEFORE importing kaggle (it authenticates on import).
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception as e:  # noqa: BLE001
        print(f"[test] FAIL — could not import kaggle CLI: {e}")
        sys.exit(1)

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as e:  # noqa: BLE001
        print(f"[test] FAIL — authenticate() error: {e}")
        sys.exit(1)

    # Shape check BEFORE any network call, because it explains the most common
    # failure without needing one. A legacy key is 32 lowercase hex characters.
    # The new "API Tokens" access tokens are longer and not hex, and the pinned
    # CLI (1.7.4.5, the newest on PyPI as of July 2026) cannot use them for
    # writes — reads may appear to succeed while every upload returns 401.
    looks_legacy = len(key) == 32 and all(c in "0123456789abcdef" for c in key.lower())
    if not looks_legacy:
        print(f"[test] WARNING — key is {len(key)} chars and "
              f"{'not ' if not all(c in '0123456789abcdef' for c in key.lower()) else ''}"
              f"hex; a legacy key is 32 hex chars. This is very likely a new-style "
              f"API Token, which CLI {getattr(api, '__version__', '1.7.x')} cannot "
              f"use to push datasets or kernels.")

    # This MUST be an endpoint that genuinely 401s on bad credentials.
    #
    # It previously called dataset_list(mine=True), which returns an EMPTY LIST
    # rather than raising when auth fails — so the test printed PASS against
    # credentials that could not upload a single byte, and two sessions recorded
    # "credentials work" on the strength of it. kernels_list_cli hits an endpoint
    # that authenticates properly.
    try:
        api.kernels_list_cli(mine=True, page_size=1)
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        if any(t in msg for t in ("401", "403", "Unauthorized", "Forbidden")):
            print(f"[test] FAIL — credentials rejected (auth error): {e}")
            print("[test] Fix: kaggle.com -> Settings -> API -> 'Create New Token'.")
            print("[test] That downloads kaggle.json containing a LEGACY 32-hex key.")
            print("[test] Put its username/key in .env. The 'API Tokens' page issues")
            print("[test] a different, longer token that this CLI cannot use.")
        else:
            print(f"[test] FAIL — API call error: {e}")
        sys.exit(1)

    print(f"[test] PASS — authenticated as {user!r} against an endpoint that "
          f"rejects bad credentials.")


if __name__ == "__main__":
    main()
