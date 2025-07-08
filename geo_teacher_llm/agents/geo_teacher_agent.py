from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from translation_agent import maybe_translate_to_english


def load_vectorstore(persist_directory="./chroma_db"):
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


llm = OllamaLLM(model="llama3.2")


def generate_answer(context, question):
    prompt = ChatPromptTemplate.from_template(
        """
You are a Geoteacher, a kind geography teacher.

    Use the following context extracted from Wikipedia about the country:

    {context}

    Student question: {question}

    Please answer in English in a pedagogical, concise, and clear way, providing relevant information about the country to help the student understand.
    Answer in English in a clear, factual, and concise manner, without greetings or off-topic information.

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


def geo_teacher_agent(question):
    print('hellloooooooooooooooooo')
    question_en = maybe_translate_to_english(question)
    relevant_docs = search_relevant_chunks(question_en, k=5)
    if not relevant_docs:
        return "Sorry, I didn’t find any relevant information to answer this question."

    context = build_context_from_docs(relevant_docs)
    answer = generate_answer(context, question_en)
    return answer


if __name__ == "__main__":
    user_question = input("Ask you geography question : ")
    response = geo_teacher_agent(user_question)
    print("\nAnswer from GeoTeacher LLM :\n")
    print(response)
