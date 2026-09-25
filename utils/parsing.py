import re


def extract_next_action(response: str) -> str:
    """
    Tolerant extraction: looks for a 'NEXT' token anywhere in a line
    (case-insensitive, ignoring markdown noise), rather than requiring
    an exact 'NEXT:' prefix. Falls back to the last non-empty line of
    the response if no explicit NEXT marker is found, so a malformed
    response still contributes signal instead of silently defaulting.
    """
    cleaned_lines = []
    for raw_line in response.split("\n"):
        line = re.sub(r"[*_`#>-]", "", raw_line).strip()
        if not line:
            continue
        cleaned_lines.append(line)
        if re.match(r"^next\s*:", line, re.IGNORECASE):
            return re.split(r"^next\s*:", line, flags=re.IGNORECASE)[-1].strip()

    return cleaned_lines[-1] if cleaned_lines else ""