import os
import requests
from dotenv import load_dotenv
from geo_teacher_llm.agents.detect_country import detect_country_in_question
from geo_teacher_llm.agents.weather_agent import get_capital_from_country,detect_country_from_capital_in_question

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

UNSPLASH_URL = "https://api.unsplash.com/search/photos"


def fetch_country_landscape_images(state, num_images=2):
    if not UNSPLASH_ACCESS_KEY:
        raise ValueError("UNSPLASH_ACCESS_KEY environment variable not set.")

    # Déterminer le terme de recherche priorisé : city > capital_city > country
    search_location = state.get("city") or state.get("country")

    if not search_location:
        print("❌ Aucun 'city', 'capital_city', ni 'country' disponible, skipping fetch.")
        return state

    params = {
        "query": f"{search_location} landscape",
        "per_page": num_images,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape",
    }

    try:
        response = requests.get(UNSPLASH_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération d'images Unsplash: {e}")
        return state

    images = []
    for result in data.get("results", []):
        image_info = {
            "title": result.get("description")
            or result.get("alt_description")
            or "Landscape Image",
            "url": result["urls"]["regular"],
            "photographer": result["user"]["name"],
            "photographer_url": result["user"]["links"]["html"],
        }
        images.append(image_info)

    state["images"] = images
    return state


if __name__ == "__main__":
    country = input("Enter country name: ")
    state={}
    state['input']= country
    images = fetch_country_landscape_images(state)
    for idx, img in enumerate(images, 1):
        print(
            f"Image {idx}: {img['title']} - {img['url']} (by {img['photographer']} - {img['photographer_url']})"
        )
