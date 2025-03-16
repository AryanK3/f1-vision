import time
import json

with open('new_location_data.json', 'r') as file:
    location_data = json.load(file)

start_time = time.time()
event_index = 0

while event_index < len(location_data):
    current_time = time.time() - start_time

    if current_time >= location_data[event_index]['rel_time']:
        event = location_data[event_index]
        print(f"Driver {event['id']} at {event['x']} {event['y']} {event['z']} in {event['rel_time']}s")
        event_index += 1

    time.sleep(0.01)
