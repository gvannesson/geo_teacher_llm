import pandas as pd
import json

ALIASES = {
    "north_korea": "democratic_people's_republic_of_korea",
    "south_korea": "republic_of_korea",
    "usa": "united_states_of_america",
    "us": "united_states_of_america",
    "uk": "united_kingdom_of_great_britain_and_northern_ireland",
    "ivory_coast": "côte_d'ivoire",
    "russia": "russian_federation",
    "bahamas": "the_bahamas",
    "bolivia": "plurinational_state_of_bolivia",
    "venezuela": "venezuela_(bolivarian_republic_of)",
    "netherlands": "netherlands_(kingdom_of_the)",
    "england": "united_kingdom_of_great_britain_and_northern_ireland",
    "great_britain": "united_kingdom_of_great_britain_and_northern_ireland",
    "micronesia": "micronesia_(federated_states_of)",
    "Congo Kinshasa": "democratic_republic_of_the_congo",
    "tanzania": "united_republic_of_tanzania",
    "syria": "syrian_arab_republic",
    "iran": "iran_(islamic_republic_of)",
    "moldova": "republic_of_moldova",
    "congo brazzaville": "republic_of_the_congo",
    "georgia": "georgia_(the_country)"
}

def excel_to_json(excel_path, json_path):
    df = pd.read_excel(excel_path)

    country_to_capital = {}
    for index, row in df.iterrows():
        country = str(row[0]).strip().lower().replace(" ", "_")
        capital = str(row[1]).strip()

        # Utiliser ALIASES pour mapping correct
        country_standardized = ALIASES.get(country, country)

        country_to_capital[country_standardized] = capital

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(country_to_capital, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported {len(country_to_capital)} entries to {json_path}")

if __name__ == "__main__":
    excel_path = "country_capital_city.xlsx"  # adapte le chemin selon ton projet
    json_path = "country_to_capital.json"
    excel_to_json(excel_path, json_path)
