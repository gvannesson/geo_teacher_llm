import os
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate

# 🚩 1) Définir tes outils wrappers (fonctionnels) pour function calling propre
from geo_teacher_llm.agents.geo_teacher_agent import geo_teacher_agent
from geo_teacher_llm.agents.weather_agent import get_weather, get_capital_from_country, detect_country_from_capital_in_question
from geo_teacher_llm.agents.image_agent import fetch_country_landscape_images
from geo_teacher_llm.agents.translation_agent import maybe_translate_to_english
from geo_teacher_llm.agents.detect_city_agent import detect_city_agent
from geo_teacher_llm.agents.detect_country import detect_country_in_question
from geo_teacher_llm.agents.weather_activity_agent import weather_activity_agent
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from IPython.display import Image, display
from typing import TypedDict, List, Any
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable


os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "geo_teacher_llm2"


class GeoTeacherState(TypedDict):
    input: str
    route: str
    messages: list
    country: str
    images: list
    capital_city: str
    geo_teacher_answer: str
    lat: float
    lon:float
    city: str
    weather_info : str
    fetched_places: list
    activity_suggestions: dict
    route: list


llm = ChatOllama(model="llama3.2", temperature=0, base_url="http://localhost:11434")

# 2️⃣ Router prompt
router_prompt = PromptTemplate.from_template(
    """
You are an intelligent router for a geography assistant.

Analyze the question and decide which categories apply, using only:
- 'weather' if the question is about meteorological conditions in a place
- 'images' if the question is about getting pictures of a geographical place
- 'geography' if it's a question about geography

Respond ONLY with the relevant categories, separated by a single space, all in lowercase, with NO explanations or punctuation.

Examples:
- Question: What is the weather in Paris?
  Answer: weather

- Question: Show me images of Japan.
  Answer: images

- Question: Tell me about the rivers in Brazil.
  Answer: geography

- Question: I want to see the weather in Tokyo and pictures.
  Answer: weather images
  

Question: {input}
"""
)


llm_router_chain = (
    {"input": RunnablePassthrough()}
    | router_prompt
    | llm
    | StrOutputParser()
    | (lambda route: {"route": route.strip()})
)

# 🚩 3) Créer le graph LangGraph avec nœud LLM central
workflow = StateGraph(GeoTeacherState)
workflow.add_node("translation_node", maybe_translate_to_english)
workflow.add_node("llm_router", llm_router_chain)
workflow.add_node("weather_node", get_weather)
workflow.add_node("geo_node", geo_teacher_agent)
workflow.add_node("image_node", fetch_country_landscape_images)
workflow.add_node("detect_city_node", detect_city_agent)
workflow.add_node("detect_country_in_question_node", detect_country_in_question)
workflow.add_node("get_capital_node", get_capital_from_country)
workflow.add_node("detect_country_from_capital_node", detect_country_from_capital_in_question)
workflow.add_node("activity_agent", weather_activity_agent)


workflow.set_entry_point("translation_node")
workflow.add_edge("translation_node", "detect_city_node")
workflow.add_edge("detect_city_node", "detect_country_in_question_node")
workflow.add_edge("detect_country_in_question_node", "get_capital_node")
workflow.add_edge("get_capital_node", "detect_country_from_capital_node")
workflow.add_edge("detect_country_from_capital_node", "llm_router")

@traceable
def router_decision_initial(state):
    route = state["route"].lower().strip()
    categories = route.split()
    order = ["geography", "weather", "images"]
    sorted_categories = [cat for cat in order if cat in categories]
    categories= " ".join(sorted_categories)
    if "geography" in categories:
        return "geo_node"
    if "weather" in categories:
        return "weather_node"
    if "images" in categories:
        return "image_node"
    else:
        return "END"
    

def router_decision_after_geo(state):
    route = state["route"].lower().strip()
    categories = route.split()
    order = ["geography", "weather", "images"]
    sorted_categories = [cat for cat in order if cat in categories]
    categories= " ".join(sorted_categories)
    if "weather" in categories:
        return "weather_node"
    if "images" in categories:
        return "image_node"
    else:
        return "END"


def router_decision_after_weather(state):
    route = state["route"].lower().strip()
    categories = route.split()
    order = ["geography", "weather", "images"]
    sorted_categories = [cat for cat in order if cat in categories]
    categories= " ".join(sorted_categories)
    if "images" in categories:
        return "image_node"
    else:
        return "END"
    
    

workflow.add_conditional_edges(
    "llm_router",
    router_decision_initial,
    {
        "geo_node": "geo_node",
        "weather_node": "weather_node",
        "image_node": "image_node",
        "END": END
    },
)


workflow.add_conditional_edges(
    "geo_node",
    router_decision_after_geo,
    {
        "weather_node": "weather_node",
        "image_node": "image_node",
        "END": END
    }
)

workflow.add_edge("weather_node", "activity_agent")


workflow.add_conditional_edges(
    "activity_agent",
    router_decision_after_weather,
    {
        "image_node": "image_node",
        "END": END
    }
)


workflow.add_edge("geo_node", END)
workflow.add_edge("activity_agent", END)
workflow.add_edge("image_node", END)






app = workflow.compile()
png = app.get_graph().draw_mermaid_png()

# =============== CLI LOOP ===============
if __name__ == "__main__":
    while True:
        state={}
        user_input = input("Pose ta question de géographie (ou 'exit') : ")
        state['input']= user_input
        response = app.invoke(state)
        print(response)
        with open("langgraph_corrected.png", "wb") as file:
            file.write(png)
        print("\n---\n")
