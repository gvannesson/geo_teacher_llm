from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from geo_teacher_llm.agents.translation_agent import maybe_translate_to_english
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def load_vectorstore(persist_directory="chroma_db"):
    embeddings = HuggingFaceEmbeddings(
        model_name="WhereIsAI/UAE-Large-V1", model_kwargs={"device": "cpu"}
    )
    vectorstore = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )
    return vectorstore


def search_relevant_chunks(question, k=5):
    vectorstore = load_vectorstore()
    relevant_docs = vectorstore.similarity_search(query=question, k=k)
    return relevant_docs


def build_context_from_docs(relevant_docs):
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    return context


# llm = OllamaLLM(model="llama3.2")
llm = ChatGroq(
    api_key=os.getenv("GROQ_KEY"),
    model_name="llama3-8b-8192"  # ou "mixtral-8x7b-32768", selon ce que tu veux

)


def generate_answer(context, question):
    prompt = ChatPromptTemplate.from_template(
        """
You are Geoteacher, a kind geography teacher.

You can use the following context extracted from Wikipedia about countries if it is relevant to answer the question. If it is not relevant, you can answer using your own knowledge.

Context:
{context}

Student question: {question}

Please answer in English in a pedagogical, clear, and concise way, providing relevant geographical facts to help the student understand.

Do not add greetings, off-topic information
Under no circumstances should you mention images, pictures, photos, or your inability to provide images, even if the student requests them.
Focus only on answering the geographical aspects of the question.
Limit your answer to 5 sentences maximum.
"""
    )
    chain = prompt | llm
    response = chain.invoke(
        {"context": context, "question": question},
        temperature=0.2,
        top_p=0.9,
        max_tokens=256,
    )
    return response


def geo_teacher_agent(state):
    question_en = state['input']
    relevant_docs = search_relevant_chunks(question_en, k=5)
    if not relevant_docs:
        state["geo_teacher_answer"] = (
            "Sorry, I didn’t find any relevant information to answer this question."
        )
        return state

    context = build_context_from_docs(relevant_docs)
    answer = generate_answer(context, question_en)
    state["geo_teacher_answer"] = answer
    return state


if __name__ == "__main__":
    user_question = {}
    user_question["input"] = input("Ask you geography question : ")
    response = geo_teacher_agent(user_question)
    print("\nAnswer from GeoTeacher LLM :\n")
    print(response)
