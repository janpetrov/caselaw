import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://rozhodnuti.nsoud.cz"
SUBDIR = Path(__file__).parent / "sc_case_links"


def fetch_page(url):
    """Fetch and return the BeautifulSoup object for a given URL."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_opinion_links(soup, base_url, entry_id):
    """Extract opinion links from the page and return results and updated entry_id."""
    results = []
    opinion_links = soup.find_all("a", class_="odk")

    for link_tag in opinion_links:
        case_id_text = link_tag.get_text(strip=True)

        # if we have matched the button for a particular page, we skip it
        if case_id_text.isdigit():
            continue

        relative_url = link_tag.get("href", "")
        full_url = urljoin(base_url, relative_url)

        results.append({"id": entry_id, "case_id": case_id_text, "permanent_link": full_url})
        entry_id += 1

    return results, entry_id


def find_next_page_url(soup, base_url):
    """Find and return the next page URL if available, otherwise None."""
    # Look for an "a" element that contains "Další" text anywhere inside it
    next_link = soup.find(
        lambda tag: tag.name == "a"
        and tag.find(string=re.compile(r"Dal\u0161\u00ed")) is not None
        or (tag.name == "a" and re.compile(r"Dal\u0161\u00ed").search(tag.text) is not None)
    )
    if not next_link:
        return None
    next_link_text = next_link.get("href", "")
    if next_link_text:
        return urljoin(base_url, next_link_text)
    return None


def save_results_to_json(results, filepath: Path):
    """Save results to a JSON file with an automatic numeric suffix.
    If filename is "court_opinions.json", it will attempt to save to "court_opinions_00.json",
    then "court_opinions_01.json", etc. until an unused filename is found.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Scraping complete. {len(results)} records saved to {filepath}.")


def scrape_opinions(start_url, base_url, sleep_time=12):
    """Main scraping function that fetches and processes all pages."""
    results = []
    entry_id = 1
    next_page_url = start_url

    while next_page_url:
        soup = fetch_page(next_page_url)
        if not soup:
            break

        page_results, entry_id = extract_opinion_links(soup, start_url, entry_id)
        if not page_results:
            print(f"No court opinion links found on {next_page_url}. Stopping scraping.")
            break

        results.extend(page_results)
        next_page_url = find_next_page_url(soup, base_url)

        if next_page_url:
            # Wait before fetching the next page to respect rate limit
            time.sleep(sleep_time)

    return results


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Scrape court opinions from a website.")

    parser.add_argument(
        "--url",
        type=str,
        default="https://rozhodnuti.nsoud.cz/judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D24%2F02%2F2025&SearchMax=1000&SearchOrder=4&Start=0&Count=20&pohled=1",
        help="The starting URL for scraping court opinions",
    )

    parser.add_argument(
        "--output-file-name",
        type=str,
        default="court_opinions.json",
        help="Filename to save the scraped results",
    )

    parser.add_argument(
        "--rate-limit", type=float, default=3, help="Sleep time between requests in seconds"
    )

    return parser.parse_args()


if __name__ == "__main__":
    SUBDIR.mkdir(exist_ok=True, parents=True)

    args = parse_arguments()
    results = scrape_opinions(start_url=args.url, base_url=BASE_URL, sleep_time=args.rate_limit)
    save_results_to_json(results, filepath=SUBDIR / args.output_file_name)
