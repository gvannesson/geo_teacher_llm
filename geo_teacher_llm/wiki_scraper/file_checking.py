import os

def find_empty_txt_files(directory):
    empty_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and os.stat(file_path).st_size == 0:
                empty_files.append(filename)
    return empty_files

if __name__ == "__main__":
    directory = os.path.dirname(__file__)  # dossier wiki_scraper
    empty_files = find_empty_txt_files(directory)
    
    if empty_files:
        print("Fichiers .txt vides trouvés :")
        for f in empty_files:
            print(f"- {f}")
    else:
        print("Aucun fichier .txt vide trouvé.")
