import chainlit as cl
from geo_teacher_llm.agents.graph_orchestration_agent2 import app


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    results = app.invoke(message)
    # Send a response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()