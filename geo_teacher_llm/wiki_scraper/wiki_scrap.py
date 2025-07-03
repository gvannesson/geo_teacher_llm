import os
import requests
import time

def get_wikipedia_extract(country_name):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "redirects":1,
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

def save_extract(text, country_name, folder="wiki_scraper"):
    if text is None:
        print(f"Pas de texte à sauvegarder pour {country_name}")
        return
    filename = os.path.join(folder, f"{country_name.replace(' ', '_').lower()}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Fiche sauvegardée : {filename}")

def main():
    folder = "wiki_scraper"
    os.makedirs(folder, exist_ok=True)
    list_path = os.path.join(folder, "country_list.txt")

    with open(list_path, "r", encoding="utf-8") as file:
        countries = [line.strip() for line in file.readlines() if line.strip()]
    
    # Retirer la première ligne "Member state" si présente
    if countries[0].lower().startswith("member"):
        countries = countries[1:]
    
    print(f"Nombre de pays à traiter : {len(countries)}")

    for country in countries:
        print(f"Récupération de la fiche Wikipédia pour : {country}")
        text = get_wikipedia_extract(country)
        save_extract(text, country, folder)
        time.sleep(1)  # pour éviter de spammer l'API trop vite

if __name__ == "__main__":
    main()
