import re
from rapidfuzz import process, fuzz

COUNTRY_LIST_FILE = 'wiki_scraper/country_list.txt'

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

def load_countries():
    countries = []
    with open(COUNTRY_LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines[1:]:  # Ignorer header
        country = line.strip()
        if country:
            countries.append(country)
    return countries

COUNTRIES = load_countries()

def normalize(text: str) -> str:
    return text.lower().strip().replace(' ', '_')

def detect_country_in_question(question: str, threshold=80):
    question_norm = normalize(question)

    # 1. Recherche d'alias dans la question
    for alias, country in ALIASES.items():
        if alias in question_norm:
            return country

    # 2. Recherche exact dans la liste officielle
    for country in COUNTRIES:
        if country in question_norm:
            return country

    # 3. Recherche fuzzy dans la liste officielle
    results = process.extract(question_norm, COUNTRIES, scorer=fuzz.partial_ratio, limit=1)
    if results:
        best_match, score, _ = results[0]
        if score >= threshold:
            return best_match

    # Pas trouvé
    return None

# Exemple d'utilisation
if __name__ == "__main__":
    questions = [
        "Tell me about North Korea",
        "What is the capital of USA?",
        "Info on the Bahamas please",
        "Details about Côte d'Ivoire",
        "South Korea history"
    ]

    for q in questions:
        country = detect_country_in_question(q)
        print(f"Question: {q} -> Country detected: {country}")