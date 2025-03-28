import sys
from pathlib import Path

import dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.apis.common import is_invalid_json, run_inference_parallel_with_retry
from src.apis.google import gemini_infer
from src.filter_references import process_raw_results
from src.supreme_court import get_sc_data
from src.templates import render_template

TEMPLATE_NAME = "extract_acts_03.jinja2"

MAIN_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = MAIN_DIR / ".env"
SC_PATH = MAIN_DIR / "data" / "sc_opinions.json"
OUTPUT_PATH = MAIN_DIR / "data" / "sc_opinions_with_sections.json"
ERR_PATH = MAIN_DIR / "data" / "sc_filtered_errors.txt"


if __name__ == "__main__":
    dotenv.load_dotenv(ENV_PATH)

    sc_df = get_sc_data(SC_PATH)

    texts = sc_df.text.tolist()
    numbers = sc_df.numbers.tolist()

    templatized = [render_template(TEMPLATE_NAME, court_opinion=text) for text in texts]

    results_raw = run_inference_parallel_with_retry(templatized, gemini_infer)

    with open(ERR_PATH, "w", encoding="utf-8") as f:
        for i, p in enumerate(results_raw):
            if is_invalid_json(p):
                f.write(f"{i}\n")

    processed = process_raw_results(results_raw)  # type: ignore

    with open(ERR_PATH, "a", encoding="utf-8") as f:
        for i, (n, p) in enumerate(zip(numbers, processed, strict=True)):
            if set(n) <= set(p):
                continue
            missing = set(n) - set(p)
            if all(str(m) not in sc_df.iloc[i].text for m in missing):
                continue

            f.write(f"\n{i} {n} {p} {missing}\n{sc_df.iloc[i].permanent_link}\n")

    sc_df["extracted_sections"] = processed

    sc_df.to_json(OUTPUT_PATH, orient="records", lines=True, force_ascii=False, indent=4)
