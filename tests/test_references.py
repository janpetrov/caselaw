import pytest

from src.filter_references import (
    extract_section_number,
    extract_section_numbers,
    filter_civil_code_references,
    is_civil_code_reference,
    process_raw_results,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        # With parentheses
        ("This refers to (89/2012)", True),
        ("This refers to ( 89 / 2012 )", True),
        ("This refers to (o.z.)", True),
        ("This refers to ( o . z . )", True),
        ("This refers to (OZ)", True),
        ("This refers to ( OZ )", True),
        ("This refers to (občanský zákoník)", True),
        ("This refers to ( občanského zákoníku )", True),
        ("This refers to ( občanský zákoník )", True),
        ("This refers to (občanským zákoníkem )", True),
        # Without parentheses
        ("This refers to 89/2012", True),
        ("This refers to 89 / 2012", True),
        ("This refers to o.z.", True),
        ("This refers to o . z .", True),
        ("This refers to OZ", True),
        ("This refers to občanský zákoník", True),
        ("This refers to občanského zákoníku", True),
        ("This refers to občanským zákoníkem", True),
        # With hard spaces
        ("This refers to 89\xa0/\xa02012", True),
        ("This refers to o\xa0.\xa0z\xa0.", True),
        ("This refers to občanský\xa0zákoník", True),
        # Case insensitivity
        ("This refers to (oz)", True),
        ("This refers to (O.Z.)", True),
        ("This refers to (Občanský Zákoník)", True),
        # Negative cases
        ("This has nothing relevant", False),
        ("This is 90/2012", False),
        ("This is o.s.ř.", False),
        ("This is OSŘ", False),
        ("This is trestný zákoník", False),
    ],
)
def test_is_civil_code_reference(text, expected):
    assert is_civil_code_reference(text) == expected


def test_filter_civil_code_references():
    items = [
        "This refers to (89/2012)",
        "This has nothing relevant",
        "This refers to občanský zákoník",
        "This is o.s.ř.",
    ]
    expected = ["This refers to (89/2012)", "This refers to občanský zákoník"]
    assert filter_civil_code_references(items) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("§ 123", 123),
        ("Text § 456 more text", 456),
        ("No section here", None),
    ],
)
def test_extract_section_number(text, expected):
    assert extract_section_number(text) == expected


def test_extract_section_numbers():
    items = ["§ 123", "Text § 456 more text", "Also § 123", "No section here"]
    assert sorted(extract_section_numbers(items)) == [123, 456]


def test_process_raw_results():
    raw_results = [
        '```json\n["This refers to (89/2012) § 123", "This has nothing relevant"]\n```',
        '```json\n["This refers to OZ § 456", "This is o.s.ř. § 789"]\n```',
    ]
    expected = [[123], [456]]
    assert process_raw_results(raw_results) == expected
