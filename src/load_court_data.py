import re
from pathlib import Path

import pandas as pd

CC_PARAGRAPH_RE = pattern = re.compile(r"§\s*(\d+)")


def _extract_number(s: str) -> int | None:
    try:
        return re.match(r"^\d+", s).group()  # type: ignore
    except Exception:
        return None


def _make_int(s) -> int | None:
    try:
        return int(s)
    except Exception:
        return None


###################################################################################################
## LOAD SUPREME COURT DATA
###################################################################################################


def load_sc_data(path_or_str: Path | str) -> pd.DataFrame:
    df = pd.read_json(path_or_str).assign(
        decision_date=lambda d: pd.to_datetime(d.datum_rozhodnuti, format="%d. %m. %Y"),
        publication_date=lambda d: pd.to_datetime(d.zverejneno_na_webu, format="%d. %m. %Y"),
        sp_zn=lambda d: d.spisova_znacka.mask(d.spisova_znacka == "", d.id),
    )

    out = []
    for item in df.dotcene_predpisy.tolist():
        items = item.split("\n")
        filtered_items = [
            i for i in items if "89/2012" in i or "o.z." in i.lower() or "o. z." in i.lower()
        ]
        sections = [_make_int(_extract_number(s[1:].strip())) for s in filtered_items]
        out.append(sections)

    # Rename the variable to be more descriptive
    return df.assign(sections_annotated=out)


###################################################################################################
## LOAD CONSTITUTIONAL COURT DATA
###################################################################################################


def _filter_cc_line(line_joined: str) -> str:
    lines = [line.strip() for line in line_joined.split("\n")]
    nos = [i for i, line in enumerate(lines) if "89/2012 Sb." in line]
    if len(nos) > 1:
        raise ValueError("More than one line with 89/2012 Sb. found")
    if len(nos) == 0:
        raise ValueError("No line with 89/2012 Sb. found")
    return lines[nos[0]]


def _extract_cc_line(line: str) -> list[int]:
    numbers_as_str = pattern.findall(line)
    numbers_as_int = [int(num) for num in numbers_as_str]
    return list(set(numbers_as_int))


def load_cc_data(path_or_str: Path | str) -> pd.DataFrame:
    df = pd.read_json(path_or_str).assign(
        decision_date=lambda d: pd.to_datetime(d["Datum rozhodnutí"], format="%d. %m. %Y"),
        publication_date=lambda d: pd.to_datetime(d["Datum zpřístupnění"], format="%d. %m. %Y"),
        sp_zn=lambda d: d["Sp.zn."],
    )

    sections_raw = df["Vztah k předpisům"].tolist()
    sections_lines = [_filter_cc_line(line_joined) for line_joined in sections_raw]
    sections_numbers = [_extract_cc_line(line) for line in sections_lines]

    return df.assign(sections_annotated=sections_numbers)
