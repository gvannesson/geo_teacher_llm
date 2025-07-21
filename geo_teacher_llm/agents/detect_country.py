from rapidfuzz import fuzz, process

COUNTRY_LIST_FILE = "geo_teacher_llm/wiki_scraper/country_list.txt"

ALIASES = {
    "north korea": "democratic_people's_republic_of_korea",
    "south korea": "republic_of_korea",
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
    "UK": "united_kingdom_of_great_britain_and_northern_ireland",
    "micronesia": "micronesia_(federated_states_of)",
    "Congo Kinshasa": "democratic_republic_of_the_congo",
    "tanzania": "united_republic_of_tanzania",
    "syria": "syrian_arab_republic",
    "iran": "iran_(islamic_republic_of)",
    "moldova": "republic_of_moldova",
    "congo brazzaville": "republic_of_the_congo",
    "georgia": "georgia_(the_country)",
}


def load_countries():
    countries = []
    with open(COUNTRY_LIST_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[1:]:  # Ignorer header
        country = line.strip()
        if country:
            countries.append(country)
    return countries


COUNTRIES = load_countries()


def normalize(text: str) -> str:
    return text.lower().strip().replace(" ", "_")


def detect_country_in_question(state: str, threshold=80):
    question_norm = normalize(state["input"])

    if "country" in state and state["country"]:
        country_current = state["country"].lower()

        # Vérifier s'il correspond à un alias, et normaliser si besoin
        for alias, country in ALIASES.items():
            if alias.lower() == country_current:
                state["country"] = country  # normalisation
                return state

        # Si le pays actuel est déjà exact, on retourne sans modification
        if state["country"] in COUNTRIES:
            return state
        

    for country in COUNTRIES:
        if country.lower() in question_norm:
            state["country"] = country

            return state
    # 1. Recherche d'alias dans la question
    for alias, country in ALIASES.items():
        if alias in question_norm:
            state["country"] = country
            return state

    # 2. Recherche exact dans la liste officielle

    # 3. Recherche fuzzy dans la liste officielle
    results = process.extract(
        question_norm, COUNTRIES, scorer=fuzz.partial_ratio, limit=1
    )
    if results:
        best_match, score, _ = results[0]
        if score >= threshold:
            state["country"] = best_match
            return state

    # Pas trouvé
    return None


# Exemple d'utilisation
if __name__ == "__main__":
    questions = [
        "Tell me about North Korea",
        "What is the capital of USA?",
        "what is the weather in australia ?" "Info on the Bahamas please",
        "Details about Côte d'Ivoire",
        "South Korea history",
    ]

    for q in questions:
        country = detect_country_in_question(q)
        print(f"Question: {q} -> Country detected: {country}")
