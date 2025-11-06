import re
from typing import Tuple

_NUMBER = r"\d+(?:[.,]\d+)?"


def parse_expenses_message(s: str) -> Tuple[float, str] | None:
    s = s.strip()
    if not s:
        return None

    # number at the start: "<num> <text>"
    m = re.match(rf"^({_NUMBER})\s+(.*)$", s)
    if m:
        raw_value = m.group(1)
        text = m.group(2).strip()

        # text must: (1) exist, (2) start with a word char (no punctuation before the space),
        # (3) contain no other digits.
        if not text or not re.match(r"^\w", text) or re.search(r"\d", text):
            return None

        value = float(raw_value.replace(",", "."))
        return value, text

    # number at the end: "<text> <num>"
    m = re.match(rf"^(.*)\s+({_NUMBER})$", s)
    if m:
        text = m.group(1).strip()
        raw_value = m.group(2)

        # text must: (1) exist, (2) end with a word char (no punctuation hugging the space),
        # (3) contain no other digits.
        if not text or not re.search(r"\w$", text) or re.search(r"\d", text):
            return None

        value = float(raw_value.replace(",", "."))
        return value, text

    return None
