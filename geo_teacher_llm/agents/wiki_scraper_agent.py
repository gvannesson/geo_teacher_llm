import requests

def get_wikipedia_extract(country_name):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "redirects": 1,
        "titles": country_name
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Erreur HTTP pour {country_name}: {response.status_code}")
        return None
    data = response.json()
    pages = data.get('query', {}).get('pages', {})
    if not pages:
        print(f"Aucune page trouvée pour {country_name}")
        return None
    page = next(iter(pages.values()))
    return page.get('extract', None)