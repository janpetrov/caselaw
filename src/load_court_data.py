import re
from pathlib import Path

import pandas as pd


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


def load_sc_data(path_or_str: Path | str) -> pd.DataFrame:
    """Load data from a JSON file or string."""

    df = (
        pd.read_json(path_or_str)
        .assign(
            decision_date=lambda d: pd.to_datetime(d.datum_rozhodnuti, format="%d. %m. %Y"),
            publication_date=lambda d: pd.to_datetime(d.zverejneno_na_webu, format="%d. %m. %Y"),
            sp_zn=lambda d: d.spisova_znacka.mask(d.spisova_znacka == "", d.id)
        )
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
