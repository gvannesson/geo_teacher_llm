import chainlit as cl
from geo_teacher_llm.agents.graph_orchestration_agent2 import app
import asyncio

# @cl.on_message
# async def main(message: cl.Message):
#     state = {
#         "input": message.content
#     }
#     results = app.invoke(state)

#     # 1. Affichage geo_teacher_answer
#     if "geo_teacher_answer" in results:
#         await cl.Message(content=results["geo_teacher_answer"].content).send()

#     # 2. Affichage weather_info
#     if "weather_info" in results:
#         await cl.Message(content=f"**Weather Info:** {results['weather_info']}").send()

#     # 3. Affichage activity_suggestions
#     if "activity_suggestions" in results:
#         suggestions = results["activity_suggestions"]
#         msg = ""
#         if "summary" in suggestions:
#             msg += f"**Activity Summary:** {suggestions['summary']}\n"
#         if "clothing_advice" in suggestions:
#             msg += f"👕 **Clothing Advice:** {suggestions['clothing_advice']}\n"

#         if "locations" in suggestions:
#             loc_text = "\n".join(
#                 [f"- {loc['name']} (Lat: {loc['lat']}, Lon: {loc['lon']})" for loc in suggestions["locations"]]
#             )
#             msg += f"📍 **Suggested Locations:**\n{loc_text}"

#             # Google Maps link
#             base_url = "https://www.google.com/maps/dir/"
#             for loc in suggestions["locations"]:
#                 base_url += f"{loc['lat']},{loc['lon']}/"
#             msg += f"\n\n[🗺️ Open on Google Maps]({base_url})"

#         await cl.Message(content=msg).send()

#     # 4. Affichage images
#     if "images" in results:
#         for img in results["images"]:
#             if "url" in img:
#                 await cl.Message(content=f"![{img.get('title','Image')}]({img['url']})").send()


@cl.on_message
async def main(message: cl.Message):
    state = {
        "input": message.content
    }
    results = app.invoke(state)

    # Utilitaire streaming progressif
    async def stream_text(text: str, prefix: str = ""):
        msg = cl.Message(content=prefix)
        await msg.send()
        for char in text:
            await msg.stream_token(char)
            await asyncio.sleep(0.01)  # Ajuste la vitesse du flux
        return msg

    # 1️⃣ geo_teacher_answer
    if "geo_teacher_answer" in results:
        text = results["geo_teacher_answer"].content
        await stream_text(text)

    # 2️⃣ weather_info
    if "weather_info" in results:
        text = f"**Weather Info:** {results['weather_info']}"
        await stream_text(text)

    # 3️⃣ activity_suggestions
    if "activity_suggestions" in results:
        suggestions = results["activity_suggestions"]
        msg_parts = []

        if "summary" in suggestions:
            msg_parts.append(f"**Activity Summary:** {suggestions['summary']}\n")

        if "clothing_advice" in suggestions:
            msg_parts.append(f"👕 **Clothing Advice:** {suggestions['clothing_advice']}\n")

        if "locations" in suggestions:
            loc_text = "\n".join(
                [f"- {loc['name']} (Lat: {loc['lat']}, Lon: {loc['lon']})" for loc in suggestions["locations"]]
            )
            msg_parts.append(f"📍 **Suggested Locations:**\n{loc_text}")

            # Google Maps link
            base_url = "https://www.google.com/maps/dir/"
            for loc in suggestions["locations"]:
                base_url += f"{loc['lat']},{loc['lon']}/"
            msg_parts.append(f"\n[🗺️ Open on Google Maps]({base_url})")

        combined_msg = "\n".join(msg_parts)
        await stream_text(combined_msg)

    # 4️⃣ images
    if "images" in results:
        for img in results["images"]:
            if "url" in img:
                await cl.Message(content=f"![{img.get('title','Image')}]({img['url']})").send()