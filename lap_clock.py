import time
import json

with open('new_lap_data.json', 'r') as file:
    lap_data = json.load(file)

start_time = time.time()
event_index = 0

while event_index < len(lap_data):
    current_time = time.time() - start_time

    if current_time >= lap_data[event_index]['rel_time']:
        event = lap_data[event_index]
        if event['type'] == 'lap_start':
            print(f"Driver {event['id']}: Lap {event['lap']} started at {event['rel_time']}s")
        elif event['type'] == 'sector':
            print(f"Driver {event['id']}: Lap {event['lap']}, Sector {event['sector']} completed at {event['rel_time']}s: Sector Time = {event['sector_time']}s")
        elif event['type'] == 'lap_end':
            print(f"Driver {event['id']}: Lap {event['lap']} ended at {event['rel_time']}s: Total Lap Time = {event['lap_time']}s")
        event_index += 1

    time.sleep(0.01)
