import concurrent.futures
from pathlib import Path
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

FILE_PATH = Path(__file__).parent.parent / "data" / "NALUS.csv"


def ecli_to_url(ecli):
    match = re.search(r'(Pl\.US(?:-st)?|Pl\.US-st)\.(\d+)\.(\d+)\.(\d+)', ecli, re.IGNORECASE)
    if match:
        registry, case, year, suffix = match.groups()
        registry_prefix = 'St' if 'st' in registry.lower() else 'Pl'
        return f"https://nalus.usoud.cz:443/Search/GetText.aspx?sz={registry_prefix}-{case}-{year}_{suffix}"
    
    match = re.search(r"(\d+)\.US\.(\d+)\.(\d+)\.(\d+)", ecli, re.IGNORECASE)
    if match:
        registry, case, year, suffix = match.groups()
        return (
            f"https://nalus.usoud.cz:443/Search/GetText.aspx?sz={registry}-{case}-{year}_{suffix}"
        )
    return None


def download_text(url):
    if not url:
        return None

    try:
        response = requests.get(url, timeout=30)
        response.encoding = "utf-8"  # Set encoding

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract and print the text content
        content = soup.get_text()
        content = re.sub(r"\n{3,}", "\n\n\n", content)
        content = re.sub(r" {4,}", "   ", content)

        return content
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None


def read_df(file_path):
    return pd.read_csv(
        file_path,
        encoding="cp1250",
        delimiter=";",
        quotechar='"',
        escapechar="\\",
        on_bad_lines="warn",
        low_memory=False,
        index_col=False,
    )


if __name__ == "__main__":
    df = read_df(FILE_PATH).assign(url=lambda d: d.ECLI.apply(ecli_to_url))

    results: list[None | str] = [None] * len(df)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(download_text, url): i for i, url in enumerate(df.url)}

        for future in tqdm(
            concurrent.futures.as_completed(future_to_index),
            total=len(future_to_index),
            desc="Downloading",
        ):
            index: int = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                results[index] = None

    df["text"] = results

    df.to_json(
        FILE_PATH.with_suffix(".json"),
        orient="records",
        force_ascii=False,
        indent=4,
    )
    
    print("Number of missinge texts:", int(df.text.isna().sum()))
    print("Done.")
