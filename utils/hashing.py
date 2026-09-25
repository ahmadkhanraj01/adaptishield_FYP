"""
Content fingerprints for the code a recorded artifact depends on.

`evaluation/probe_corpus.py` records what the probe said so that a scorer change
can be re-measured without re-running it. That trade is only sound while the
probe itself is unchanged, and the probe is three inline prompts inside
`CausalAnalyzer`. §6p is the reason this is hashed rather than trusted: those
prompts were edited three times in one session, and a version constant would
have needed someone to remember to bump it each time.

WHY COMMENTS ARE STRIPPED. Those same methods carry more comment than code — the
masked prompt has a 20-line note explaining why it must not be tuned — and that
prose is edited routinely without the prompt changing. Hashing raw source would
invalidate the corpus on a typo fix. So the source is parsed and re-emitted
through `ast.unparse`, which drops comments, and the docstring is removed
explicitly; what remains is the executable text, which is what actually decides
what the model is asked.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import textwrap
from typing import Callable, Dict


def code_fingerprint(func: Callable) -> str:
    """
    Short hash of a function's executable source, ignoring comments/docstring.

    Falls back to hashing the raw source if the function's source cannot be
    parsed in isolation — a fingerprint that is too sensitive is recoverable
    (re-record), one that is absent is not.
    """
    try:
        source = textwrap.dedent(inspect.getsource(func))
    except (OSError, TypeError):
        return "unavailable"

    try:
        tree = ast.parse(source)
        node = tree.body[0]
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:] or [ast.Pass()]
        normalized = ast.unparse(tree)
    except (SyntaxError, ValueError):
        normalized = source

    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def prompt_fingerprints() -> Dict[str, str]:
    """
    Fingerprints of every method whose text decides what the probe is asked.

    `_run_regime_once` holds both the masked and the orig prompt;
    `_sanitize_mediator` produces the text the two sanitized regimes are shown;
    `_extract_next_action` turns a response into the action that gets scored, so
    a change there moves the recorded action just as surely as a prompt edit.
    """
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer

    return {
        name: code_fingerprint(getattr(CausalAnalyzer, name))
        for name in ("_run_regime_once", "_sanitize_mediator",
                     "_extract_next_action")
    }
