import os

def slugify_country_name(name):
    """Slugify the country name as in your previous scraping."""
    return name.lower().replace(" ", "_") + ".txt"

def check_country_files(country_list_path, scraper_folder):
    present_non_empty = []
    present_but_empty = []
    missing = []

    with open(country_list_path, "r", encoding="utf-8") as f:
        countries = [line.strip() for line in f.readlines() if line.strip() and not line.strip().lower().startswith("member state")]

    for country in countries:
        filename = slugify_country_name(country)
        file_path = os.path.join(scraper_folder, filename)
        if os.path.isfile(file_path):
            if os.stat(file_path).st_size == 0:
                present_but_empty.append((country, filename))
            else:
                present_non_empty.append((country, filename))
        else:
            missing.append((country, filename))

    return present_non_empty, present_but_empty, missing

if __name__ == "__main__":
    country_list_path = os.path.join(os.path.dirname(__file__), "country_list.txt")
    scraper_folder = os.path.dirname(__file__)

    present_non_empty, present_but_empty, missing = check_country_files(country_list_path, scraper_folder)

    print("✅ Pays avec fichier présent et non vide :", len(present_non_empty))
    for country, file in present_non_empty:
        print(f" - {country} ({file})")

    print("\n⚠️ Pays avec fichier présent mais VIDE :", len(present_but_empty))
    for country, file in present_but_empty:
        print(f" - {country} ({file})")

    print("\n❌ Pays sans fichier :", len(missing))
    for country, file in missing:
        print(f" - {country} ({file})")
