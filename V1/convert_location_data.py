import json

with open('driver_data.json', 'r') as file:
    driver_data = json.load(file)

events = []
for driver in driver_data:
    id = driver['id']
    for pos in driver['positions']:
        events.append({
            "id": id,
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "rel_time": pos[3]
        })

events.sort(key=lambda x: x['rel_time'])

with open("new_location_data.json", "w") as f:
    json.dump(events, f)
