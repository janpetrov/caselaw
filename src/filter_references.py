import itertools
import re
from typing import Iterable


def is_civil_code_reference(item: str) -> bool:
    NEEDLES = "89/2012", "o. z.", "o.z."
    return any(needle in item.lower() for needle in NEEDLES) or bool(
        re.search(r"občansk\w*\s+zákon\w*", item, re.IGNORECASE)
    )


def filter_civil_code_references(items: Iterable[str]) -> list[str]:
    predicates = [is_civil_code_reference(item) for item in items]
    return list(itertools.compress(items, predicates))


def extract_section_number(text: str):
    match = re.search(r"§\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def extract_section_numbers(items: Iterable[str]) -> list[int]:
    extracted = [extract_section_number(item) for item in items]
    filtered = [item for item in extracted if item is not None]
    return list(set(filtered))
