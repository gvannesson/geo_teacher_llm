from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import json
from typing import Dict, Any
from geo_teacher_llm.agents.fetch_places_agent import fetch_places_agent
from geo_teacher_llm.agents.geo_teacher_agent import llm
import re
# Initialize your local Ollama LLM
# llm = OllamaLLM(model="llama3.2")

# Prompt to generate activities, clothing advice, and places with lat/lon
activity_prompt = ChatPromptTemplate.from_template("""
You are a travel activity assistant helping users find suitable activities based on the weather and known places.

Weather:
{weather_data}

Location:
{location}

Known places (with name, category, lat, lon):
{places}

Instructions:
1. Select 3 activities that fit today's weather using only the provided places.
2. For each activity, use the 'category' field to determine the type of activity and return the exact name of the chosen place:
    - 'cafe': suggest enjoying a coffee or a snack inside.
    - 'museum': suggest visiting the museum.
    - 'park': suggest outdoor walks or picnics if the weather allows.
    - 'zoo': suggest visiting the zoo if the weather is suitable.
    - 'beach': suggest beach activities if the weather is suitable.
3. Do not suggest activities unrelated to the provided categories. Do not suggest shopping in cafes.
4. Generate a single clear sentence summarizing the 3 proposed activities for today, in a friendly and encouraging tone.
5. Provide **only ONE clothing advice for the day** based on the weather.


Respond strictly in JSON with double quotes:
                                                   
{{
    "summary": "A single sentence summarizing the 3 proposed activities.",
    "clothing_advice": "A short, practical clothing advice based on today's weather.",
    "locations": [
        {{"name": "Place Name", "lat": 12.345, "lon": 67.890}},
        {{"name": "Place Name", "lat": 12.345, "lon": 67.890}},
        {{"name": "Place Name", "lat": 12.345, "lon": 67.890}}
    ]
}}
""")
def weather_activity_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    fetch_places_agent(state)
    weather_data = state["weather_info"]
    places = json.dumps(state["fetched_places"], ensure_ascii=False)
    if "city" in state:
        location = f"{state['city']}, {state['country']}"
    else:
        location = f"{state['capital_city']}, {state['country']}"


    chain = activity_prompt | llm | StrOutputParser()
    response = chain.invoke({
        "weather_data": weather_data,
        "places": places,
        "location": location,
    })

    json_match = re.search(r"\{.*\}", response, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            parsed = {"error": "Failed to parse JSON", "raw_response": response}
    else:
        parsed = {"error": "No JSON found in LLM response", "raw_response": response}

    state["activity_suggestions"] = parsed
    return state

if __name__ == "__main__":
    state = {
        "weather_info": "Currently in Lille, France, it is sunny with a temperature of 30.4°C (feels like 30.9°C) and humidity at 55%.",
        "country": "France",
        "capital_city": "Lille",
        "fetched_places":[{'name': 'Le Voltaire', 'category': 'cafe', 'latitude': 50.637047, 'longitude': 3.0622839}, {'name': 'Au Point Central', 'category': 'cafe', 'latitude': 50.6393838, 'longitude': 3.0649427}, {'name': 'Parvis Treille', 'category': 'cafe', 'latitude': 50.6396164, 'longitude': 3.0617223}, {'name': "Saint-Sauveur - Salle d'exposition", 'category': 'museum', 'latitude': 50.626861, 'longitude': 3.0717035}, {'name': 'Le Tripostal', 'category': 'museum', 'latitude': 50.6366637, 'longitude': 3.0728035}, {'name': 'Maison Folie Le Colysée', 'category': 'museum', 'latitude': 50.6391909, 'longitude': 3.0352871}, {'name': 'Parc Henri Matisse', 'category': 'park', 'latitude': 50.6405192, 'longitude': 3.0724767}, {'name': 'Square Dutilleul', 'category': 'park', 'latitude': 50.6365068, 'longitude': 3.0556605}, {'name': 'Square Foch', 'category': 'park', 'latitude': 50.635595, 'longitude': 3.0571814}, {'name': 'Zoo de Lille', 'category': 'zoo', 'latitude': 50.637929, 'longitude': 3.045981}, {'name': 'Ferme pédagogique Marcel Dhénin', 'category': 'zoo', 'latitude': 50.6374376, 'longitude': 3.0799349}, {'name': 'Maison Tropicale', 'category': 'zoo', 'latitude': 50.6382506, 'longitude': 3.0455699}]
    }
    result = weather_activity_agent(state)
    print(result)
    print(result["activity_suggestions"])