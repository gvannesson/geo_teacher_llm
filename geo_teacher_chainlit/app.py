import chainlit as cl
from geo_teacher_llm.agents.graph_orchestration_agent2 import app
import json

@cl.on_message
async def main(message: cl.Message):
    state = {
        "input": message.content
    }
    results = app.invoke(state)

    # if "geo_teacher_answer" in results and results["geo_teacher_answer"]:
    #     output_text = results['geo_teacher_answer'].content
    # else:
    #     output_text = "ℹ️ No geo_teacher_answer found in results.\n\n"

    # elements = []
    # if "images" in results:
    #     images_list = results.get("images", [])
    #     for img in images_list[:2]:  # Only take up to 2 images
    #         if "url" in img:
    #             elements.append(cl.Image(url=img["url"]))

    
    # if "weather_info" in results and results["weather_info"]:
    #     weather_info = results['weather_info']
    # else:
    #     weather_info = ""

    # if "activity_suggestions" in results and results["activity_suggestions"]:
    #     activity_suggestion = str(results['activity_suggestions'])
    # else:
    #     activity_suggestion=""
    
    # text_content = output_text+weather_info+activity_suggestion
    # print(text_content)
    # # element = [
    # #     cl.Text(name="simple_text", content=text_content, display="inline")
    # # ]

    # await cl.Message(content=text_content, elements=elements).send()


    print(results)
    # 1. Affichage geo_teacher_answer
    if "geo_teacher_answer" in results:
        await cl.Message(content=results["geo_teacher_answer"].content).send()

    # 2. Affichage weather_info
    if "weather_info" in results:
        await cl.Message(content=f"**Weather Info:** {results['weather_info']}").send()

    # 3. Affichage activity_suggestions
    if "activity_suggestions" in results:
        suggestions = results["activity_suggestions"]
        msg = ""
        if "summary" in suggestions:
            msg += f"**Activity Summary:** {suggestions['summary']}\n"
        if "clothing_advice" in suggestions:
            msg += f"👕 **Clothing Advice:** {suggestions['clothing_advice']}\n"

        if "locations" in suggestions:
            loc_text = "\n".join(
                [f"- {loc['name']} (Lat: {loc['lat']}, Lon: {loc['lon']})" for loc in suggestions["locations"]]
            )
            msg += f"📍 **Suggested Locations:**\n{loc_text}"

            # Google Maps link
            base_url = "https://www.google.com/maps/dir/"
            for loc in suggestions["locations"]:
                base_url += f"{loc['lat']},{loc['lon']}/"
            msg += f"\n\n[🗺️ Open on Google Maps]({base_url})"

        await cl.Message(content=msg).send()

    # 4. Affichage images
    if "images" in results:
        for img in results["images"]:
            if "url" in img:
                await cl.Message(content=f"![{img.get('title','Image')}]({img['url']})").send()


