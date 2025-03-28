# all decisions are filtered for 
#   "Občanskoprávní a obchodní kolegium"
#   ("o. z." OR "občansk* zákon*" OR "89/2012")

# Define scripts directory as a shared variable
SCRIPTS_DIR="scripts"

# A decisions from 1 Jul 2019 to 28 Feb 2025, 416 opinions
python ${SCRIPTS_DIR}/scrape_sc_case_links.py \
    --url 'https://rozhodnuti.nsoud.cz/judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D01%2F07%2F2019%20AND%20%5Bdatum_predani_na_web%5D%3C%3D28%2F02%2F2025%20AND%20(%5BARozhodnutiRT%5D%3D((%22o.%20z.%22%20OR%20%22občansk*%20zákon*%22%20OR%20%2289%2F2012%22)))%20AND%20(%5Bkolegium%5D%3D1%20OR%20%5Bobko%5D%3D1)%20AND%20(%5Bkategorie_rozhodnuti1%5D%3DA)&SearchMax=1000&SearchOrder=4&Start=0&Count=60&pohled=1' \
    --output-file-name sc_case_links/A.json

# B decisions from 1 Jul 2019 to 28 Feb 2022, 858 opinions
python ${SCRIPTS_DIR}/scrape_sc_case_links.py \
    --url 'https://rozhodnuti.nsoud.cz/judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D01%2F07%2F2019%20AND%20%5Bdatum_predani_na_web%5D%3C%3D28%2F02%2F2025%20AND%20(%5BARozhodnutiRT%5D%3D((%22o.%20z.%22%20OR%20%22občansk*%20zákon*%22%20OR%20%2289%2F2012%22)))%20AND%20(%5Bkolegium%5D%3D1%20OR%20%5Bobko%5D%3D1)%20AND%20(%5Bkategorie_rozhodnuti1%5D%3DB)&SearchMax=1000&SearchOrder=4&Start=0&Count=60&pohled=1' \
    --output-file-name sc_case_links/B.json

# C decisions from 1 Jul 2019 to 31 Dec 2020, 642 opinions
python ${SCRIPTS_DIR}/scrape_sc_case_links.py \
    --url 'https://rozhodnuti.nsoud.cz/judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D01%2F07%2F2019%20AND%20%5Bdatum_predani_na_web%5D%3C%3D31%2F12%2F2020%20AND%20(%5BARozhodnutiRT%5D%3D((%22o.%20z.%22%20OR%20%22občansk*%20zákon*%22%20OR%20%2289%2F2012%22)))%20AND%20(%5Bkolegium%5D%3D1%20OR%20%5Bobko%5D%3D1)%20AND%20(%5Bkategorie_rozhodnuti1%5D%3DC)&SearchMax=1000&SearchOrder=4&Start=0&Count=60&pohled=1' \
    --output-file-name sc_case_links/C_2019_2020.json

# C decisions from 1 Jan 2021 to 31 Dec 2022, 814 opinions
python ${SCRIPTS_DIR}/scrape_sc_case_links.py \
    --url 'https://rozhodnuti.nsoud.cz/judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D01%2F01%2F2021%20AND%20%5Bdatum_predani_na_web%5D%3C%3D31%2F12%2F2022%20AND%20(%5BARozhodnutiRT%5D%3D((%22o.%20z.%22%20OR%20%22občansk*%20zákon*%22%20OR%20%2289%2F2012%22)))%20AND%20(%5Bkolegium%5D%3D1%20OR%20%5Bobko%5D%3D1)%20AND%20(%5Bkategorie_rozhodnuti1%5D%3DC)&SearchMax=1000&SearchOrder=4&Start=0&Count=60&pohled=1' \
    --output-file-name sc_case_links/C_2021_2022.json

# C decisions from 1 Jan 2023 to 31 Dec 2024, 869 opinions
python ${SCRIPTS_DIR}/scrape_sc_case_links.py \
    --url 'https://rozhodnuti.nsoud.cz/judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D01%2F01%2F2023%20AND%20%5Bdatum_predani_na_web%5D%3C%3D31%2F12%2F2024%20AND%20(%5BARozhodnutiRT%5D%3D((%22o.%20z.%22%20OR%20%22občansk*%20zákon*%22%20OR%20%2289%2F2012%22)))%20AND%20(%5Bkolegium%5D%3D1%20OR%20%5Bobko%5D%3D1)%20AND%20(%5Bkategorie_rozhodnuti1%5D%3DC)&SearchMax=1000&SearchOrder=4&Start=0&Count=60&pohled=1' \
    --output-file-name sc_case_links/C_2023_2024.json

# C decisions from 1 Jan 2025 to 28 Feb 2025, 83 opinions
python ${SCRIPTS_DIR}/scrape_sc_case_links.py \
    --url 'https://rozhodnuti.nsoud.cz/judikatura/judikatura_ns.nsf/$$WebSearch1?SearchView&Query=%5Bdatum_predani_na_web%5D%3E%3D01%2F01%2F2025%20AND%20%5Bdatum_predani_na_web%5D%3C%3D28%2F02%2F2025%20AND%20(%5BARozhodnutiRT%5D%3D((%22o.%20z.%22%20OR%20%22občansk*%20zákon*%22%20OR%20%2289%2F2012%22)))%20AND%20(%5Bkolegium%5D%3D1%20OR%20%5Bobko%5D%3D1)%20AND%20(%5Bkategorie_rozhodnuti1%5D%3DC)&SearchMax=1000&SearchOrder=4&Start=0&Count=60&pohled=1' \
    --output-file-name sc_case_links/C_2025_Feb.json
