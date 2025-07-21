import requests
from typing import Dict, Any
from collections import defaultdict
import random

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def fetch_location_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    print(state)
    if state.get('lat') or state.get('lon'):
        return state
    
    city = state["capital_city"]
    country = state["country"]
    location_name = f"{city}, {country}"
    headers = {
    "User-Agent": "geo_teacher_llm/1.0 (contact: gauthier@example.com)"
                }

    # 1️⃣ Get lat/lon from Nominatim
    nominatim_url = f"https://nominatim.openstreetmap.org/search"
    params = {"q": location_name, "format": "json", "limit": 1}
    response = requests.get(nominatim_url, params=params, headers=headers)
    print(response)
    data = response.json()
    if not data:
        state["known_places"] = {"error": f"Could not find coordinates for {location_name}"}
        return state

    state["lat"] = data[0]["lat"]
    state["lon"] = data[0]["lon"]
    
    return state


def fetch_places_from_overpass(state, radius=5000):
    
    lat = state['lat']
    lon=state['lon']
    query = f"""
    [out:json][timeout:25];
    (
      node["tourism"="museum"](around:{radius},{lat},{lon});
      way["tourism"="museum"](around:{radius},{lat},{lon});
      relation["tourism"="museum"](around:{radius},{lat},{lon});

      node["leisure"="park"](around:{radius},{lat},{lon});
      way["leisure"="park"](around:{radius},{lat},{lon});
      relation["leisure"="park"](around:{radius},{lat},{lon});

      node["tourism"="zoo"](around:{radius},{lat},{lon});
      way["tourism"="zoo"](around:{radius},{lat},{lon});
      relation["tourism"="zoo"](around:{radius},{lat},{lon});

      node["natural"="beach"](around:{radius},{lat},{lon});
      way["natural"="beach"](around:{radius},{lat},{lon});
      relation["natural"="beach"](around:{radius},{lat},{lon});

      node["amenity"="cafe"](around:{radius},{lat},{lon});
      way["amenity"="cafe"](around:{radius},{lat},{lon});
      relation["amenity"="cafe"](around:{radius},{lat},{lon});
    );
    out center;
    """

    response = requests.post(OVERPASS_URL, data={"data": query})
    if response.status_code != 200:
        print(f"Overpass API error: {response.status_code} {response.text}")
        return state

    results = response.json()
    places_by_category = defaultdict(list)

    tag_to_category = {
        "museum": "museum",
        "park": "park",
        "zoo": "zoo",
        "beach": "beach",
        "cafe": "cafe"
    }

    for element in results.get("elements", []):
        tags = element.get("tags", {})
        lat_val = element.get("lat") or (element.get("center") and element["center"].get("lat"))
        lon_val = element.get("lon") or (element.get("center") and element["center"].get("lon"))

        if not lat_val or not lon_val:
            continue

        name = tags.get("name")
        if not name:
            continue

        # Determine category
        category = None
        if tags.get("tourism") == "museum":
            category = "museum"
        elif tags.get("leisure") == "park":
            category = "park"
        elif tags.get("tourism") == "zoo":
            category = "zoo"
        elif tags.get("natural") == "beach":
            category = "beach"
        elif tags.get("amenity") == "cafe":
            category = "cafe"

        if category:
            places_by_category[category].append({
                "name": name,
                "category": category,
                "latitude": float(lat_val),
                "longitude": float(lon_val)
            })

    # Limit to 3 per category
    limited_places = []
    for category, places in places_by_category.items():
        limited_places.extend(random.sample(places, min(3, len(places))))
    # Inject into state
    state["fetched_places"] = limited_places
    return state

def fetch_places_agent(state):
    fetch_location_agent(state)
    lat = state.get("lat")
    lon = state.get("lon")
    if not lat or not lon:
        print("Latitude and longitude not provided in state.")
        return state

    fetch_places_from_overpass(state)
    return state

if __name__ == "__main__":
    state = {"capital_city": "Lille", "country": "France"}
    state = fetch_places_agent(state)
    print(state["fetched_places"])
