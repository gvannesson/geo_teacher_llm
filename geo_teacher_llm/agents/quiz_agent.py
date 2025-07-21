from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

llm = OllamaLLM(model="llama3.2")

parser = JsonOutputParser()

quiz_prompt = ChatPromptTemplate.from_template(
    """
You are GeoQuiz, a geography teacher assistant that creates short quizzes.

Generate a quiz with 3 multiple-choice questions (A, B, C, D) about {topic}.
Return ONLY in the following JSON format:
[
  {{
    "question": "Question text",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "answer": "Correct option letter"
  }},
  ...
]
"""
)

chain = quiz_prompt | llm | parser

def quiz_agent(state):
    topic = state["input"]
    quiz = chain.invoke({"topic": topic})
    state["quiz"] = quiz
    return state

question={}
question['input']="what is the capital city of Germany?"
quiz_agent(question)
print(question['quiz'])