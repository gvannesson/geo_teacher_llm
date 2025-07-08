import os
import requests
from dotenv import load_dotenv
load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

UNSPLASH_URL = "https://api.unsplash.com/search/photos"

def fetch_country_landscape_images(country_name, num_images=2):
    if not UNSPLASH_ACCESS_KEY:
        raise ValueError("UNSPLASH_ACCESS_KEY environment variable not set.")

    params = {
        "query": f"{country_name} landscape",
        "per_page": num_images,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape",
    }

    response = requests.get(UNSPLASH_URL, params=params)
    response.raise_for_status()
    data = response.json()

    images = []
    for result in data.get("results", []):
        image_info = {
            "title": result.get("description") or result.get("alt_description") or "Landscape Image",
            "url": result["urls"]["regular"],
            "photographer": result["user"]["name"],
            "photographer_url": result["user"]["links"]["html"]
        }
        images.append(image_info)

    return images

if __name__ == "__main__":
    country = input("Enter country name: ")
    images = fetch_country_landscape_images(country)
    for idx, img in enumerate(images, 1):
        print(f"Image {idx}: {img['title']} - {img['url']} (by {img['photographer']} - {img['photographer_url']})")