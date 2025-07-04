import os
import re


def clean_text(text: str) -> str:
    # Supprime les références [1], [2], [a], etc.
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\[[a-z]+\]", "", text)

    # Supprime les sections indésirables et tout ce qui suit (References, See also, External links, Categories, etc.)
    pattern = re.compile(
        r"(References|See also|External links|Further reading|Notes|Bibliography|Sources|Categories|Navigation menu|This page was last edited).*",
        re.IGNORECASE | re.DOTALL,
    )
    text = re.split(pattern, text)[0]

    # Supprime les lignes vides multiples et espaces en début/fin de ligne
    lines = [line.strip() for line in text.splitlines()]
    # Filtrer lignes vides
    lines = [line for line in lines if line]
    cleaned_text = "\n".join(lines)

    return cleaned_text


def clean_all_files(input_folder="wiki_scraper", output_folder="wiki_scraper/clean"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned = clean_text(raw_text)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            print(f"[+] Cleaned {filename} -> {output_path}")


if __name__ == "__main__":
    clean_all_files()
