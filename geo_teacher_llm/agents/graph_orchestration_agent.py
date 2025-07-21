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

from langsmith import traceable

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "geo_teacher_llm"


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
    description="Get the current weather in a city by providing the capital name.",
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
router_prompt = PromptTemplate.from_template(
    """

You are an intelligent router for a geography assistant.
Analyze the question and answer only with one of these categories:
- 'weather' if the question is about meteorological conditions
- 'images' if the question is about getting pictures
- 'combine' if it's something else
                                             
Question: {input}
"""
)

from langchain_core.messages import HumanMessage, AIMessage


@traceable
def create_tool_call_message(tool_name, content="", tool_args={}):
    """
    Manually create an AIMessage with the structure ToolNode expects.
    """
    return AIMessage(
        content=content,
        additional_kwargs={
            "tool_calls": [
                {
                    "id": "tool_call_id",
                    "function": {"name": tool_name, "arguments": tool_args},
                    "type": "function",
                }
            ]
        },
    )


@traceable
def prepare_toolnode_input(state):
    print("ééééééééééééééé")
    print(state)
    route = state["route"]
    messages = state["messages"]
    print("~~~~~~~~###~~~~~~~~~~", route)
    print("~~~~~~~~###~~~~~~~~~~", messages)
    route_to_tool_name = {
        "weather": "get_weather_from_capital",
        "images": "get_images_of_country",
        "combine": "answer_geography_question",
    }
    tool_name = route_to_tool_name.get(route)
    print(f"🪐 Preparing ToolNode input for tool: {tool_name}")

    ai_message = create_tool_call_message(tool_name=tool_name, content="", tool_args={})
    messages.append(ai_message)
    return {"messages": messages}


llm_router_chain = (
    {"input": RunnablePassthrough()}
    | router_prompt
    | llm
    | StrOutputParser()
    | RunnableLambda(
        lambda output: {
            "route": output.strip().lower(),
            "messages": [HumanMessage(content=output.strip())],
        }
    )
    | RunnableLambda(prepare_toolnode_input)
)


weather_node = ToolNode(tools=[tool_get_weather])
geo_node = ToolNode(tools=[tool_get_answer])
image_node = ToolNode(tools=[tool_get_images])

# 🚩 3) Créer le graph LangGraph avec nœud LLM central
workflow = StateGraph(GeoTeacherState)

workflow.add_node("llm_router", llm_router_chain)
workflow.add_node("weather_node", weather_node)
workflow.add_node("geo_node", geo_node)
workflow.add_node("image_node", image_node)

workflow.set_entry_point("llm_router")


@traceable
def route_decision(state):
    print(f"DEBUG: state keys before routing: {list(state.keys())}")
    print(state["messages"])
    print(state["input"])
    user_input = state["input"]

    if "weather" in user_input.lower() or "umbrella" in user_input.lower():
        # return {"route": "weather_node"}
        print("#########weather")
        return "weather_node"
    elif "images" in user_input.lower() or "population" in user_input.lower():
        # return {"route": "geo_node"}
        print("#########images")
        return "image_node"
    else:
        # return {"route": "default_node"}
        print("#########geo")
        return "geo_node"



workflow.add_conditional_edges(
    "llm_router",
    route_decision,
    {
        "weather_node": "weather_node",
        "image_node": "image_node",
        "geo_node": "geo_node",
        "END": END,
    },
)


# 🚩 Lier les étapes pour "combine"
workflow.add_edge("geo_node", "weather_node")
workflow.add_edge("weather_node", END)
workflow.add_edge("image_node", END)

# 🚩 Terminer le flux après image_node
# workflow.add_edge("image_node", END)

# 🚩 Terminer le flux pour les autres cas non-combinés
workflow.add_edge("weather_node", END)


# Compiler le graphe prêt à l'exécution
app = workflow.compile()
png = app.get_graph().draw_mermaid_png()


# 9️⃣ CLI loop
while True:
    user_input = input("Pose ta question de géographie (ou 'exit') : ")
    # user_input="do i need an umbrella in Lima ?"
    print(user_input)
    if user_input.lower() == "exit":
        break
    response = app.invoke({"input": user_input}, {"recursion_limit": 3})
    if "messages" in response and response["messages"]:
        last_message = response["messages"][-1]
        print("\n🪐 Réponse de l'agent :")
        print(last_message)
    else:
        print("🪐 Pas de message dans la réponse :", response)

    with open("langgrpah.png", "wb") as file:
        file.write(png)
    print("~~~~~~~~~~~~", response)
    print("🪐 Réponse de l'agent :\n")
    print(response)
