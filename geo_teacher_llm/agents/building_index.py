import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def build_index(data_folder="geo_teacher_llm/wiki_scraper/clean", persist_directory="./chroma_db"):

    documents = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(data_folder, filename)
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()
            documents.extend(docs)

    # Split des documents pour limiter la taille des chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # Embeddings avec UAE-Large-V1
    embeddings = HuggingFaceEmbeddings(model_name="WhereIsAI/UAE-Large-V1")

    # Création de l’index ChromaDB
    vectorstore = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=persist_directory
    )

    # Sauvegarde persistante
    vectorstore.persist()


    print(f"Index construit et sauvegardé dans {persist_directory}")



if __name__ == "__main__":
    build_index()