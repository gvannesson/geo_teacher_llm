from geo_teacher_llm.agents.graph_orchestration_agent2 import app

async def process_question(question: dict):
    # Passer la question à ton graphe LangGraph
    result = app.invoke(question)

    # Adapter le résultat au format API
    return result