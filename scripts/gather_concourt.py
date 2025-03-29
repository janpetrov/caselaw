import argparse
import concurrent.futures
import re
from pathlib import Path
from typing import Collection, Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from striprtf.striprtf import rtf_to_text
from tqdm import tqdm

FILE_PATH = Path(__file__).parent.parent / "data" / "NALUS.csv"
RTF_DIR_PATH = Path(__file__).parent.parent / "data" / "rtf"


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


def ecli_to_url(ecli):
    match = re.search(r"(Pl\.US(?:-st)?|Pl\.US-st)\.(\d+)\.(\d+)\.(\d+)", ecli, re.IGNORECASE)
    if match:
        registry, case, year, suffix = match.groups()
        registry_prefix = "St" if "st" in registry.lower() else "Pl"
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


def download_texts_parallel(urls: Collection[str]) -> list[None | str]:
    results: list[None | str] = [None] * len(urls)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(download_text, url): i for i, url in enumerate(urls)}

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

    return results


def read_rtf_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        rtf_text = file.read()
        plain_text = rtf_to_text(rtf_text)
        return plain_text


def _extract_id_from_url(url: str) -> str:
    splits = url.split("aspx?sz=")
    if len(splits) != 2:
        raise ValueError(f"URL does not contain 'aspx?sz=' or contains it multiple times: {url}")
    return splits[1]


def headings_and_texts_from_rtf_files(urls: Iterable[str]) -> tuple[list[str], list[str]]:
    ids = [_extract_id_from_url(url) for url in urls]
    paths = [(RTF_DIR_PATH / doc_id).with_suffix(".rtf") for doc_id in ids]
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"RTF file not found: {path}")

    full_decisions = [read_rtf_file(path) for path in paths]

    headings, texts = [], []
    for i, text in enumerate(full_decisions):
        if text.count("PRÁVNÍ VĚTY") != 1:
            raise ValueError(f"Text at index {i} does not contain 'PRÁVNÍ VĚTY' exactly once")

        content = text.split("PRÁVNÍ VĚTY")[1].strip()

        parts = content.split("Česká republika", 1)
        if len(parts) != 2:
            raise ValueError(f"Text at index {i} does not contain 'Česká republika' exactly once")

        headings.append(parts[0].strip())
        texts.append(parts[1].strip())

    return headings, texts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download or read constitutional court decisions.")
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download texts from URLs instead of reading from RTF files",
    )
    args = parser.parse_args()

    df = read_df(FILE_PATH).assign(url=lambda d: d.ECLI.apply(ecli_to_url))

    if args.download:
        results = download_texts_parallel(df.url.tolist())
        df["text"] = results
    else:
        headings, texts = headings_and_texts_from_rtf_files(df.url.tolist())
        df["pravni_veta"] = headings
        df["text"] = texts

    df.to_json(
        FILE_PATH.with_suffix(".json"),
        orient="records",
        force_ascii=False,
        indent=4,
    )

    print("Number of missinge texts:", int(df.text.isna().sum()))
    print("Done.")
