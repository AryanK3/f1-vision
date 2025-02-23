import os
import json
from groq import Groq

# Initialize the Groq client with your API key.
client = Groq(api_key='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')


def generate_f1_commentary(event):
    """
    Generate F1 commentary for a given event using the Groq API.
    """
    prompt = (
        f"Generate F1 commentary for the following event:\n"
        f"Event Type: {event['type']}\n"
        f"Description: {event['description']}\n\n"
        "Commentary:"
    )

    try:
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[
                {"role": "system", "content": "You are an expert F1 commentator. Use different ways of exclaiming make it unique and Make it!! dont add much country connections to the drivers. Maybe give it some backstory but only 1/200 times "},
                {"role": "system", "content": (
                    "1 -> Max Verstappen, 16 -> Charles Leclerc, 63 -> George Russell, "
                    "55 -> Carlos Sainz, 11 -> Sergio Perez, 14 -> Fernando Alonso, "
                    "4 -> Lando Norris, 81 -> Oscar Piastri, 44 -> Lewis Hamilton, "
                    "27 -> Nico Hülkenberg, 22 -> Yuki Tsunoda, 18 -> Lance Stroll, "
                    "23 -> Alex Albon, 3 -> Daniel Ricciardo, 20 -> Kevin Magnussen, "
                    "77 -> Valtteri Bottas, 24 -> Zhou Guanyu, 2 -> Logan Sargeant, "
                    "31 -> Esteban Ocon, 10 -> Pierre Gasly"
                )},
                {"role": "user", "content": prompt}
            ],
            max_tokens=180,
        )
        commentary = response.choices[0].message.content.strip()
    except Exception as e:
        commentary = f"Error generating commentary: {e}"

    return commentary


def process_event(event):
    """
    Processes a single event.
    Only events that are considered major (i.e. "carevent", "crash", or "overtake")
    will have commentary generated.
    """
    # Define the set of major event types (in lowercase for comparison).
    major_events = {"carevent", "crash", "overtake"}
    if isinstance(event, dict) and event.get("type", "").lower() in major_events:
        return {
            "event": event,
            "commentary": generate_f1_commentary(event)
        }
    return None


def convert_event_data(raw_event):
    """
    Converts a raw event (which may be in list format) into a dictionary.
    Expected format for a list event: [type, timestamp, description]
    """
    if isinstance(raw_event, list) and len(raw_event) >= 3:
        return {"type": raw_event[0], "timestamp": raw_event[1], "description": raw_event[2]}
    elif isinstance(raw_event, dict):
        return raw_event
    else:
        return None


def main():
    # Load the event data from the JSON file.
    # Make sure your "event_data.json" contains events in the expected format.
    with open("event_data.json", "r") as f:
        data = json.load(f)

    results = []
    for raw_event in data:
        event = convert_event_data(raw_event)
        if event:
            result = process_event(event)
            if result:
                print(result)
                results.append(result)

    # Save the generated commentary to f1_commentary.json.
    with open("f1_commentary2.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

    print("F1 commentary saved to f1_commentary.json")


if __name__ == "__main__":
    main()
