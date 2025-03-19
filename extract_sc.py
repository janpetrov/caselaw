import re
from pathlib import Path

import pandas as pd


FILE_PATH = Path("data") / "sc_opinions.json"


def read_df(path: Path):
    df = pd.read_json(path).assign(
        datum_rozhodnuti=lambda d: pd.to_datetime(d.datum_rozhodnuti, format="%d. %m. %Y"),
        zverejneno_na_webu=lambda d: pd.to_datetime(d.zverejneno_na_webu, format="%d. %m. %Y"),
        spisova_znacka=lambda d: d.spisova_znacka.mask(d.spisova_znacka == "", d.id),
    )

    def get_number(s):
        try:
            return re.match(r"^\d+", s).group()  # type: ignore
        except Exception:
            return None

    def make_int(s):
        try:
            return int(s)
        except Exception:
            return None

    column_numbers = []
    for item in df.dotcene_predpisy.tolist():
        items = item.split("\n")
        filtered_items = [
            i for i in items if "89/2012" in i or "o.z." in i.lower() or "o. z." in i.lower()
        ]
        # remove the § character, strip and extract the first number there
        current_numbers = [make_int(get_number(s[1:].strip())) for s in filtered_items]
        column_numbers.append(current_numbers)

    return df.assign(numbers=column_numbers)


if __name__ == "__main__":
    df = read_df(FILE_PATH)
    print(len(df))
