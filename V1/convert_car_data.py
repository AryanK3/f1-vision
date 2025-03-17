'''
import json

with open('V1/car_data.json', 'r') as file:
    driver_data = json.load(file)

events = []
for driver in driver_data:
    id = driver['id']
    for pos in driver['positions']:
        events.append({
            "id": id,
            "rpm": pos[1],
            "speed": pos[2],
            "n_gear": pos[3],
            "throttle": pos[4],
            "drs": pos[5],
            "brake": pos[6],
            "rel_time": pos[0]
        })

events.sort(key=lambda x: x['rel_time'])

with open("new_car_data.json", "w") as f:
    json.dump(events, f)
'''

import json
import os
with open('car_data.json', 'r') as file:
    driver_data = json.load(file)

if not os.path.exists('new_car_data'):
    os.makedirs('new_car_data')

for driver in driver_data:
    driver_id = driver['id']
    filename = f"driver_{driver_id}.json"
    
    with open(f'new_car_data/{filename}', "w") as f:
        json.dump(driver, f)
    
