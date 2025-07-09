import os
import requests
from dotenv import load_dotenv
import json
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
    "UK":"united_kingdom_of_great_britain_and_northern_ireland",
    "micronesia": "micronesia_(federated_states_of)",
    "Congo_Kinshasa": "democratic_republic_of_the_congo",
    "tanzania": "united_republic_of_tanzania",
    "syria": "syrian_arab_republic",
    "iran": "iran_(islamic_republic_of)",
    "moldova": "republic_of_moldova",
    "congo_brazzaville": "republic_of_the_congo",
    "georgia": "georgia_(the_country)"
}


with open("wiki_scraper/clean/country_to_capital.json", "r", encoding="utf-8") as f:
    COUNTRY_TO_CAPITAL = json.load(f)

def get_capital_from_country(country_name):
    country_key = country_name.lower().strip().replace(" ", "_")
    # Appliquer alias si nécessaire
    country_key = ALIASES.get(country_key, country_key)
    return COUNTRY_TO_CAPITAL.get(country_key)

def get_weather(state):
    """
    Retrieve current weather for a capital city using WeatherAPI.
    """
    capital_name="London"
    country="England"
    if not API_KEY:
        raise ValueError("WeatherAPI key not found. Please set WEATHER_API_KEY in your .env file.")
    query = f"{capital_name},{country}" if country else capital_name

    params = {
        "key": API_KEY,
        "q": query,
        "lang": "en"
    }

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
        state['messages']= weather_report
        return state
    
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except KeyError:
        return "Could not retrieve weather data. Please verify the city name."

if __name__ == "__main__":
    country = input("Enter the country: ")
    capital = get_capital_from_country(country)
    if capital:
        print(get_weather(capital, country=country))
    else:
        print("Capital not found for this country.")
