# Caselaw

## Instructions for Running

### Constitutional Court Opinions

1. Go to nalus.usoud.cz and find cases using the following filters:
   - vyhověno, zamítnuto, aditivní, interpretativní
   - vztah k předpisu 89/2012 Sb.
   - datum zpřístupnění 1. 7. 2019 (up until February 28, 2025)

2. Click "Export" and save the exported .csv file as `NALUS.csv` in this directory.

3. Go through each page, click the selector for all cases and then press "stáhnout vybrané".
   Save all downloaded .rtf files to the `data/rtf` directory.

4. Run `python scripts/gather_concourt.py`.

### Supreme Court Opinions

1. Download links by running `scrape_sc_case_links.sh`.

2. Gather the `data/sc_opinions.json` file by running `python scripts/scrape_sc_opinions.py`.
