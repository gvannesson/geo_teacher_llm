import os
from langchain_community.chat_models import ChatOllama
from langchain.agents import Tool, initialize_agent
from dotenv import load_dotenv

from geo_teacher_llm.agents.weather_agent import get_weather, get_capital_from_country
from geo_teacher_llm.agents.image_agent import fetch_country_landscape_images
from geo_teacher_llm.agents.geo_teacher_agent import geo_teacher_agent


load_dotenv()


# Wrapper pour Weather Agent afin de convertir country_name en capital_name proprement
def get_weather_from_country(country_name):
    print('#########', country_name)
    capital_name = get_capital_from_country(country_name)
    print('~~~~~~~~~~~~~~~', capital_name)
    if capital_name:
        return get_weather(capital_name)
    else:
        return f"Could not find the capital for {country_name}. Please check the country name."

# Tool pour GeoTeacherAgent
def geo_teacher_tool(question):
    return geo_teacher_agent(question)

# Définition des tools avec function calling
tools = [
    Tool(
        name="get_weather_from_country",
        description="Use to get the weather of the capital city of a country when a user asks about weather, temperature, climate or related queries for a specific country.",
        func=get_weather_from_country,
    ),
    Tool(
        name="get_images_for_country",
        description="Use to get 2 landscape images of a country when the user asks for images, photos, or landscapes of a specific country.",
        func=fetch_country_landscape_images,
    ),
    Tool(
        name="geo_teacher_tool",
        description="Use for any geography-related educational questions about a country, its history, capital, or if the user asks for general information about a country.",
        func=geo_teacher_tool,
    ),
]

# Modèle Ollama avec function calling
llm = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
)

# Initialisation de l'agent
agent = initialize_agent(
    tools,
    llm,
    agent_type="openai-tools-agent",  # active le function calling automatique
    verbose=True,
)

def main():
    print("🌍 GeoTeacher LLM - Multi-Agent CLI")
    index=0
    while True:
        user_input = input("\nAsk your question about geography (or 'exit') : ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Bye!")
            break

        response = agent.invoke({"input": user_input})
        print("\n🪐 Answer from the agent :\n")
        print(response["output"])
        print(f"index={index}")
        index+=1

if __name__ == "__main__":
    main()