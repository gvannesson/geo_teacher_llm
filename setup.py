from setuptools import setup, find_packages

setup(
    name="geo_teacher_llm",
    version="0.1.0",
    description="Un assistant LLM de géographie pour répondre à des questions, afficher des photos et donner la météo.",
    author="Ton Nom",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "openai",
        "requests",
    ],
    python_requires=">=3.9",
)