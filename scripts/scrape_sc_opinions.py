import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TypedDict

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
LINKS_DIR = BASE_DIR / "sc_case_links"
OUTPUT_FILE = BASE_DIR / "data" / "sc_opinions.json"


class CaseLink(TypedDict):
    """Type definition for a case link dictionary."""
    case_id: str
    permanent_link: str
    source_file: str


@dataclass
class CourtDecision:
    id: str = ""
    pravni_veta: str = ""
    soud: str = ""
    datum_rozhodnuti: str = ""
    spisova_znacka: str = ""
    ecli: str = ""
    typ_rozhodnuti: str = ""
    heslo: str = ""
    dotcene_predpisy: str = ""
    kategorie_rozhodnuti: str = ""
    zverejneno_na_webu: str = ""
    publikovano_ve_sbirce: str = ""
    anotace: str = ""
    text: str = ""
    source_file: str = ""  # Added field to track source file
    permanent_link: str = ""  # Added field to store the URL

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items()}


def extract_text_from_font_elements(soup, css_class, width_value):
    """Extract text from font elements within specific table cells."""
    font_elements = soup.select(f".{css_class}[width='{width_value}'] font")
    return " ".join([element.get_text(strip=True) for element in font_elements])


def limit_newlines(text: str, maxnl: int) -> str:
    """Limit the number of consecutive newlines in the text."""
    return re.sub(r"\n{2,}", "\n" * maxnl, text).strip()


def clean_newlines(text: str) -> str:
    """
    Removes single newlines while preserving paragraph breaks.
    Single newlines are replaced with spaces, while sequences of two or more
    newlines are reduced to a single newline character.
    """
    # Replace single newlines with spaces
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Replace multiple newlines with a single one
    text = re.sub(r"\n{1,}", "\n", text)
    return text.strip()


def scrape_court_decision(html_content, permanent_link="", source_file=""):
    soup = BeautifulSoup(html_content, "html.parser")
    decision = CourtDecision(permanent_link=permanent_link, source_file=source_file)

    # Extract file ID from the top
    id_text = soup.select_one('.left-part font[face="Arial CE"]')
    if id_text:
        decision.id = id_text.get_text(strip=True)

    # Extract data from the table
    table = soup.find("table", id="tabl")
    if table:
        rows = table.find_all("tr")  # type: ignore
        for row in rows:
            left_part = row.select_one(".left-part")
            right_part = row.select_one(".right-part")

            if not left_part or not right_part:
                continue

            left_text = left_part.get_text(strip=True)
            right_text = right_part.get_text(separator="", strip=False).strip()

            if "Právní věta:" in left_text:
                decision.pravni_veta = clean_newlines(
                    right_part.get_text(separator=" ", strip=False)
                )
            elif "Soud:" in left_text:
                decision.soud = right_text
            elif "Datum rozhodnutí:" in left_text:
                decision.datum_rozhodnuti = right_text
            elif "Spisová značka" in left_text:
                decision.spisova_znacka = right_text
            elif "ECLI:" in left_text:
                decision.ecli = right_text
            elif "Typ rozhodnutí:" in left_text:
                decision.typ_rozhodnuti = right_text
            elif "Heslo:" in left_text:
                decision.heslo = limit_newlines(right_text, 1)
            elif "Dotčené předpisy:" in left_text:
                decision.dotcene_predpisy = limit_newlines(right_text, 1)
            elif "Kategorie rozhodnutí:" in left_text:
                decision.kategorie_rozhodnuti = right_text
            elif "Zveřejněno na webu:" in left_text:
                decision.zverejneno_na_webu = right_text
            elif "Publikováno ve sbírce" in left_text:
                decision.publikovano_ve_sbirce = right_text
            elif "Anotace:" in left_text:
                # For anotace, we need to get the text from the details tag
                details = right_part.find("details")
                if details:
                    summary = details.find("summary")
                    summary_text = (
                        summary.get_text(separator="\n\n", strip=False) if summary else ""
                    )
                    p_text = (
                        details.find("p").get_text(separator="\n\n", strip=False)
                        if details.find("p")
                        else ""
                    )
                    anotace = f"{summary_text} {p_text}".strip()
                    decision.anotace = limit_newlines(anotace, 2)

    # Extract the main text of the decision
    main_text_div = soup.select_one('div[style="text-align:justify;"]')
    if main_text_div:
        text = main_text_div.get_text(separator="\n\n", strip=False)
        decision.text = limit_newlines(text, 2)

    return decision.to_dict()


def load_case_links_from_directory(directory_path: str) -> list[CaseLink]:
    """
    Load all case links from JSON files in the specified directory.
    Returns a list of dictionaries with case information, extended with source_file.
    """
    all_cases: list[CaseLink] = []

    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]

    for file_name in json_files:
        file_path = os.path.join(directory_path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cases = json.load(f)
                # Add source_file information to each case
                for case in cases:
                    case['source_file'] = file_name
                all_cases.extend(cases)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")

    return all_cases


# Create a lock for thread-safe operations
print_lock = threading.Lock()
results_lock = threading.Lock()


def process_case(case: CaseLink) -> dict:
    """
    Process a single case by fetching and scraping the court decision.
    This function is designed to be used with ThreadPoolExecutor.
    """
    permanent_link = case.get('permanent_link', '')
    source_file = case.get('source_file', '')
    case_id = case.get('case_id', '')

    try:
        with print_lock:
            print(f"Processing: {case_id} from {source_file}")

        response = requests.get(permanent_link, timeout=30)
        response.raise_for_status()

        decision_data = scrape_court_decision(
            response.text,
            permanent_link=permanent_link,
            source_file=source_file
        )

        with print_lock:
            print(f"Successfully processed: {case_id}")

        return decision_data

    except Exception as e:
        with print_lock:
            print(f"Error processing {case_id} from {source_file}: {e}")

        # Return a minimal record for failed cases
        return {
            'id': '',
            'spisova_znacka': case_id,
            'permanent_link': permanent_link,
            'source_file': source_file,
            'error': str(e)
        }


def scrape_all_court_decisions(links_directory: str, output_file: str, max_workers: int = 10):
    """
    Scrape all court decisions from links in the specified directory and save to a single JSON file.

    Args:
        links_directory: Directory containing JSON files with case links
        output_file: Path to save the combined results
        max_workers: Maximum number of threads to use
    """
    # Load all case links
    all_cases = load_case_links_from_directory(links_directory)
    print(f"Found {len(all_cases)} cases to process")

    # Store all results
    all_decisions = []

    # Process cases with thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all cases to the executor
        future_to_case = {executor.submit(process_case, case): case for case in all_cases}

        # Process results as they complete
        for future in future_to_case:
            try:
                decision_data = future.result()
                with results_lock:
                    all_decisions.append(decision_data)
            except Exception as e:
                case = future_to_case[future]
                print(f"Exception processing case {case.get('case_id', '')}: {e}")

    # Save all results to a single JSON file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_decisions, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_decisions)} court decisions to {output_file}")


if __name__ == "__main__":
    scrape_all_court_decisions(str(LINKS_DIR), str(OUTPUT_FILE), max_workers=20)
