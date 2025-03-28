import itertools
import json
import re
from typing import Iterable


def is_civil_code_reference(item: str) -> bool:
    # Check for civil code identifiers with optional parentheses
    patterns = [
        r"(?:\(\s*)?89\s*/\s*2012(?:\s*\))?",           # 89/2012 with optional parentheses
        r"(?:\(\s*)?o\s*\.\s*z\s*\.(?:\s*\))?",         # o.z. with optional parentheses
        r"(?:\(\s*)?OZ(?:\s*\))?",                      # OZ with optional parentheses
        r"(?:\(\s*)?občansk\w+\s+zákon\w*(?:\s*\))?"    # občanský zákoník with optional parentheses
    ]

    lower_item = item.lower()

    # Replace non-breaking spaces with regular spaces for consistent matching
    lower_item = lower_item.replace('\xa0', ' ')

    for pattern in patterns:
        if re.search(pattern, lower_item, re.IGNORECASE):
            return True

    return False


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


def process_raw_results(raw_results: Iterable[str]) -> list[list[int]]:
    stripped = (
        raw_result.replace("```json", "").replace("```", "").strip() for raw_result in raw_results
    )
    parsed = map(json.loads, stripped)
    filtered = map(filter_civil_code_references, parsed)
    extracted = map(extract_section_numbers, filtered)
    return list(extracted)
