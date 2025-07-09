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
from geo_teacher_llm.agents.weather_agent import get_weather
from geo_teacher_llm.agents.image_agent import fetch_country_landscape_images
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from IPython.display import Image, display
from typing import TypedDict, List, Any
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable

os.environ["LANGSMITH_TRACING"]="true"
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"]="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"
os.environ["LANGSMITH_PROJECT"]="geo_teacher_llm2"


class GeoTeacherState(TypedDict):
    input: str
    route: str
    messages: list


# Wrapper Tool 1 : récupérer capitale
tool_get_answer = Tool(
    name="answer_geography_question",
    description="Answer a geography question",
    func=geo_teacher_agent,
)

# Wrapper Tool 2 : récupérer météo
tool_get_weather = Tool(
    name="get_weather_from_capital",
    description="Get the current weather in a country by providing the capital name.",
    func=get_weather,
)

# Wrapper Tool 2 : récupérer météo
tool_get_images = Tool(
    name="get_images_of_country",
    description="Get images of a country.",
    func=fetch_country_landscape_images,
)

# 🚩 2) Instancier le LLM orchestrateur avec function calling
tools = [tool_get_answer, tool_get_weather, tool_get_images]

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
    base_url="http://localhost:11434",
    tools=tools,
)

# 2️⃣ Router prompt
router_prompt = PromptTemplate.from_template("""

You are an intelligent router for a geography assistant.
Analyze the question and answer only with one of these categories:
- 'weather' if the question is about meteorological conditions in a place
- 'images' if the question is about getting pictures of a geographical place
- 'geography' if it's something else

The answer will be one word: weather, images or geography
                                                              
Question: {input}
""")

llm_router_chain = (
    {"input": RunnablePassthrough()}
    | router_prompt
    | llm
    | StrOutputParser()
    | (lambda route: {"route": route.strip(),  "messages": [
        HumanMessage(content="What is the weather in Berlin?"),
        AIMessage(
            content="",
            additional_kwargs={
                "tool_calls": [
                    {
                        "id": "tool_call_id",
                        "function": {
                            "name": "get_weather",
                            "arguments": {"city": "Berlin"}
                        },
                        "type": "function"
                    }
                ]
            }
        )
    ]})
)


weather_node = ToolNode(tools=[tool_get_weather])
geo_node = ToolNode(tools=[tool_get_answer])
image_node = ToolNode(tools=[tool_get_images])
# 🚩 3) Créer le graph LangGraph avec nœud LLM central
workflow = StateGraph(GeoTeacherState)

workflow.add_node("llm_router", llm_router_chain)
workflow.add_node("weather_node", get_weather)
workflow.add_node("geo_node", geo_node)
workflow.add_node("image_node", image_node)

workflow.set_entry_point("llm_router")

@traceable
def router_decision(state):
    route = state["route"].lower()
    print(route)
    if route == "weather":
        print("weather_node")
        return "weather_node"
    elif route == "images":
        print("image_node")
        return "image_node"
    else:
        print("geo_node")
        return "geo_node"

workflow.add_conditional_edges(
    "llm_router",
    router_decision,
    {
        "weather_node": "weather_node",
        "image_node": "image_node",
        "geo_node": "geo_node",
        "END": END
    }
)


# End after execution
workflow.add_edge("geo_node", END)
workflow.add_edge("weather_node", END)
workflow.add_edge("image_node", END)

# Compile
app = workflow.compile()

# =============== CLI LOOP ===============
if __name__ == "__main__":
    while True:
        user_input = input("Pose ta question de géographie (ou 'exit') : ")
        if user_input.lower() == "exit":
            break
        
        response = app.invoke({"input": user_input})
        print("\n🪐 Réponse :")
        print(response['messages'])
        print("\n---\n")