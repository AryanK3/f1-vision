import threading
import time
import json
import os

def clock_events_data():
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


def clock_location_data():
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


def clock_lap_data():
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

thread1 = threading.Thread(target=clock_events_data)
thread2 = threading.Thread(target=clock_location_data)
thread3 = threading.Thread(target=clock_lap_data)

thread1.start()
thread2.start()
thread3.start()

thread1.join()
thread2.join()
thread3.join()

print("All threads have finished execution.")
