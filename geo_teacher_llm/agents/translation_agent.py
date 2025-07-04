from langdetect import detect
from transformers import MarianMTModel, MarianTokenizer

# Téléchargement du modèle Helsinki-NLP pour FR -> EN
model_name = "Helsinki-NLP/opus-mt-fr-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MarianMTModel.from_pretrained(model_name).to("cpu")


def maybe_translate_to_english(text):
    if detect(text) == "en":
        return text
    else:
        return translate_to_english(text)


def translate_to_english(text: str) -> str:
    """
    Translate French text to English using Helsinki-NLP model.
    """
    batch = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
    generated_ids = model.generate(**batch)
    translated = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return translated
