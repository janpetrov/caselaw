import re
import concurrent.futures
from tqdm import tqdm

import pandas as pd
import requests
from bs4 import BeautifulSoup

FILE_PATH = "NALUS_03-03-2025.csv"


def ecli_to_url(ecli):
    match = re.search(r"(\d+)\.US\.(\d+)\.(\d+)\.(\d+)", ecli)
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

    # Prepare empty list for results
    results: list[None | str] = [None] * len(df)

    # Use ThreadPoolExecutor for parallel downloading
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Start the download tasks and get future objects
        future_to_index = {executor.submit(download_text, url): i for i, url in enumerate(df.url)}

        # Process results as they complete with a progress bar
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

    # Assign results back to the dataframe
    df["text"] = results

    df.to_json(
        FILE_PATH.replace(".csv", ".json"),
        orient="records",
        lines=True,
        force_ascii=False,
        indent=4,
    )
    print("Done.")
