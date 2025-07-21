import os
import requests
from dotenv import load_dotenv
import json
from geo_teacher_llm.agents.detect_country import detect_country_in_question
from unidecode import unidecode

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.weatherapi.com/v1/current.json"

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
    "UK": "united_kingdom_of_great_britain_and_northern_ireland",
    "micronesia": "micronesia_(federated_states_of)",
    "Congo_Kinshasa": "democratic_republic_of_the_congo",
    "tanzania": "united_republic_of_tanzania",
    "syria": "syrian_arab_republic",
    "iran": "iran_(islamic_republic_of)",
    "moldova": "republic_of_moldova",
    "congo_brazzaville": "republic_of_the_congo",
    "georgia": "georgia_(the_country)",
}


with open("geo_teacher_llm/wiki_scraper/clean/country_to_capital.json", "r", encoding="utf-8") as f:
    COUNTRY_TO_CAPITAL = json.load(f)
    CAPITAL_TO_COUNTRY = {
        capital.lower(): country for country, capital in COUNTRY_TO_CAPITAL.items()
    }


def get_capital_from_country(state):
    if not state.get("country"):
        return state
    country_key = state["country"].lower().strip().replace(" ", "_")
    # Appliquer alias si nécessaire
    country_key = ALIASES.get(country_key, country_key)
    state["capital_city"] = COUNTRY_TO_CAPITAL.get(country_key)
    return state


def detect_country_from_capital_in_question(state):
    """
    Détecte si une capitale est mentionnée dans state['input'].
    Si oui, ajoute state['country'] avec le pays associé.
    """
    question_lower = state["input"].lower()

    if state.get("capital_city") or state.get("country"):
        print("ℹ️ Capital ou pays déjà présent dans le state, pas de détection supplémentaire.")
        return state

    for capital, country in CAPITAL_TO_COUNTRY.items():
        if capital in question_lower:
            state["capital_city"] = capital
            # Appliquer alias si nécessaire
            country_key = country.lower().strip().replace(" ", "_")
            country_key = ALIASES.get(country_key, country_key)
            state["country"] = country_key
            print(
                f"✅ Détection automatique : capitale '{capital}' -> pays '{country_key}'"
            )
            return state

    print("❌ Aucune capitale détectée automatiquement dans la question.")
    return state


def get_weather(state):
    """
    Retrieve current weather for a capital city using WeatherAPI.
    """
    if state.get("city"):
        city = unidecode(state["city"])
        country = state.get("country", "")
        query = f"{city},{country}" if country else city

    else:
        if not state.get("capital_city") and not state.get("country"):
            print("❌ Pas de pays ni capitale détectés, impossible de récupérer la météo.")
            return state

        query = f"{state['capital_city']},{state['country']}"
        print(f"🌦️ Recherche météo sur capitale='{state.get('capital_city')}', pays='{state.get('country')}'")

    if not API_KEY:
        raise ValueError(
            "WeatherAPI key not found. Please set WEATHER_API_KEY in your .env file."
        )

    params = {"key": API_KEY, "q": query, "lang": "en"}

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        location_name = data["location"]["name"]
        region = data["location"]["region"]
        country_name = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        feelslike_c = data["current"]["feelslike_c"]
        humidity = data["current"]["humidity"]

        weather_report = (
            f"Currently in {location_name}, {country_name}, the weather is {condition.lower()} "
            f"with a temperature of {temp_c}°C (feels like {feelslike_c}°C) "
            f"and humidity at {humidity}%."
        )
        state["weather_info"] = weather_report
        return state

    except requests.exceptions.HTTPError as http_err:
        state["weather_info"] = f"HTTP error occurred while retrieving weather: {http_err}"
    except requests.exceptions.RequestException as req_err:
        state["weather_info"] = f"Request error occurred while retrieving weather: {req_err}"
    except KeyError:
        state["weather_info"] = "Could not retrieve weather data. Please verify the city name."

    return state


if __name__ == "__main__":
    state={}
    state['city']= "Grenoble"
    state['capital_city']= "Paris"
    state['country']= "France"
    print(get_weather(state))

