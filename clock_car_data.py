import json
import time

driver_id = int(input("Enter driver ID: "))
filename = f"driver_{driver_id}.json"

with open(f'car_data/{filename}', "r") as file:
    driver_data = json.load(file)

positions = driver_data['positions']
positions.sort(key=lambda x: x[0])

start_time = time.time()
event_index = 0

while event_index < len(positions):
    current_time = time.time() - start_time

    if current_time >= positions[event_index][0]:
        pos = positions[event_index]
        print(f"Driver {driver_id} at {pos[1]} rpm, {pos[2]} speed, {pos[3]} gear, {pos[4]} throttle, {pos[5]} drs, {pos[6]} brake in {pos[0]}s")
        event_index += 1

    time.sleep(0.1)  
