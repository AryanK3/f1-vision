import time
import json

with open('new_events_data.json', 'r') as file:
    events_data = json.load(file)

start_time = time.time()
event_index = 0

while event_index < len(events_data):
    current_time = time.time() - start_time

    if current_time >= events_data[event_index]['time']:
        event = events_data[event_index]
        print(f"{event['type']} : {event['message']} at {event['time']}s")
        event_index += 1

    time.sleep(0.01)
