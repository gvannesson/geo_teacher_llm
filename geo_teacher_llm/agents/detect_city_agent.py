from typing import Dict, Any, Optional
import requests

# si tu utilises ollama via LangChain
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from geo_teacher_llm.agents.geo_teacher_agent import llm
# 1️⃣ Définir l'agent
def detect_city_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    user_input = state.get("input")

    # ---- Step 1: Extraction de ville via Ollama ----
    # model = OllamaLLM(model="llama3.2")  # ou mistral, phi, gemma selon ton setup
    model=llm
    prompt = PromptTemplate(
        template=(
            "Extract ONLY the name of the city mentioned in the following text. "
            "If there is no city, respond with 'None'.\n\n"
            "Text: \"{text}\"\n\n"
            "City:"
        ),
        input_variables=["text"],
    )

    chain = prompt | model | StrOutputParser()
    extracted_city = chain.invoke({"text": user_input}).strip()
    print(extracted_city)
    if extracted_city.lower() == "none" or not extracted_city:
        state["city"] = None
        state["country"] = None
        state["lat"] = None
        state["lon"] = None
        state["geo_error"] = "No city detected from user input."
        return state

    # ---- Step 2: Géocodage via Nominatim ----
    headers = {
        "User-Agent": "geo_teacher_llm/1.0 (contact: gauthier@example.com)"
    }
    params = {
        "q": extracted_city,
        "format": "json",
        "limit": 1
    }
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers=headers,
            timeout=30,
            verify=True
        )
        response.raise_for_status()
        results = response.json()
    except Exception as e:
        state["city"] = extracted_city
        state["country"] = None
        state["lat"] = None
        state["lon"] = None
        state["geo_error"] = f"Error during geocoding: {e}"
        return state

    if results:
        geo = results[0]
        lat = float(geo["lat"])
        lon = float(geo["lon"])
        display_name = geo.get("display_name", "")
        # Heuristic to extract country from display_name
        country = display_name.split(",")[-1].strip()

        state["city"] = extracted_city
        state["country"] = country
        state["lat"] = lat
        state["lon"] = lon
        state["geo_error"] = None
    else:
        state["city"] = extracted_city
        state["country"] = None
        state["lat"] = None
        state["lon"] = None
        state["geo_error"] = "City not found in geocoding."
    return state

# 2️⃣ Exemple d'utilisation immédiate
if __name__ == "__main__":
    state = {
        "input": "is it sunny in grenoble ?"
    }
    state = detect_city_agent(state)
    print(state)
