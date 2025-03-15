import os
import json
from groq import Groq

# Initialize the Groq client with your API key.
client = Groq(api_key='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')


def generate_f1_commentary(prompt):
    """
    Generate F1 commentary for a given event using the Groq API.
    """
    try:
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[
                {"role": "system", "content": "You are an expert website builder"},
                {"role": "system", "content": "Bring the sport to you with interactive AR/VR simulations, data-driven dashboards, and AI commentary. ## Inspiration There is a growing frustration about F1, people criticize it for being boring and repetitive. They often feel like they’re missing out on the real excitement and thrill it offers. F1 is not just about cars speeding around a track, it's about strategy, quick decision-making, and minute technical details that make all the difference. At the same time, there is a growing shift in the sports world towards data analytics and immersive technologies. As more teams, analysts, and fans alike rely on detailed statistics to understand games, the demand for a more engaging and analytical experience has risen. ## What it does With F1-Vision, we bridge the gap between live races and data, bringing personalized control to the fingertips of viewers. Watch live location-tracked races and experience interactive maps and dashboards, along with every piece of data you can imagine, from tire wear to sector times to radio messages, live from the race. We also provide exciting and insightful commentary and in-app notifications of race events so that you don’t miss out on anything. ## How we built it We used Python to scrape various kinds of F1 data and stored it in files in the JSON database. These were then developed on VisionOS for the Apple Vision Pro with Swift. The 3D models were created with Blender and various Gen AI models were used to summarize event data and generate commentary audio. ## Challenges we ran into Scraping different types of data with relative times was a challenging task. Graphics with the Vision Pro and interactive 3D models also took quite some time and understanding due to a lack of documentation. ## Accomplishments that we're proud of ## What we learned ## What's next for F1-Vision With F1-Vision we are pushing the boundaries of what it means to watch sports and creating a whole new way for fans to interact with the beautiful game."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8192,
        )
        commentary = response.choices[0].message.content.strip()
    except Exception as e:
        commentary = f"Error generating commentary: {e}"

    return commentary

print(generate_f1_commentary("MAKE A WEBSITE ON F1 VISION PRO MAKE IT A FUKLLY FLEDGED JAVASCRIPT CSS AND HTML WEBSITE WITH SMOOTH SCROLL AND MAKE IT AN AMAZING LANDING PAGE WITH A BLACK BACKGROUND AND REALLY BEAUTIFUL UI ADD THIS CONTENT: Bring the sport to you with interactive AR/VR simulations, data-driven dashboards, and AI commentary. ## Inspiration There is a growing frustration about F1, people criticize it for being boring and repetitive. They often feel like they’re missing out on the real excitement and thrill it offers. F1 is not just about cars speeding around a track, it's about strategy, quick decision-making, and minute technical details that make all the difference. At the same time, there is a growing shift in the sports world towards data analytics and immersive technologies. As more teams, analysts, and fans alike rely on detailed statistics to understand games, the demand for a more engaging and analytical experience has risen. ## What it does With F1-Vision, we bridge the gap between live races and data, bringing personalized control to the fingertips of viewers. Watch live location-tracked races and experience interactive maps and dashboards, along with every piece of data you can imagine, from tire wear to sector times to radio messages, live from the race. We also provide exciting and insightful commentary and in-app notifications of race events so that you don’t miss out on anything. ## How we built it We used Python to scrape various kinds of F1 data and stored it in files in the JSON database. These were then developed on VisionOS for the Apple Vision Pro with Swift. The 3D models were created with Blender and various Gen AI models were used to summarize event data and generate commentary audio. ## Challenges we ran into Scraping different types of data with relative times was a challenging task. Graphics with the Vision Pro and interactive 3D models also took quite some time and understanding due to a lack of documentation. ## Accomplishments that we're proud of ## What we learned ## What's next for F1-Vision With F1-Vision we are pushing the boundaries of what it means to watch sports and creating a whole new way for fans to interact with the beautiful game."))