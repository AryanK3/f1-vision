import json
from dateutil import parser
'''
with open("intial_positions.json", "r") as file:
    data = json.load(file)
    res = []
    for entry in data:
        res.append({
            int(entry["driver_number"]): {
                "date": (parser.isoparse(entry["date"]) - parser.isoparse("2024-03-02T15:03:42+00:00")).total_seconds(),
                "position": entry["position"],
            }
        })

with open("new_positions.json", "w") as file:
    json.dump(res, file)
'''
with open("new_positions.json", "r") as file:
    data = json.load(file)

positions = {} 
events = []
for i in data:
    for driver_id, entry in i.items():
        position = entry["position"]
        time = entry["date"]
        if driver_id not in positions:
            positions[driver_id] = position
        if positions[driver_id] > position:
            for i in range (20, 0, -1):
                for other_driver, other_position in positions.items():
                    if (other_position == i):
                        if other_driver != driver_id:
                            if other_position >= position and other_position < positions[driver_id]:
                                print(f"Driver {driver_id} overtakes driver {other_driver} to position {other_position}")
                                events.append({
                                    'time': time,
                                    'overtaken': other_driver,
                                    'overtaker': driver_id,
                                })
                                positions[other_driver] = positions[other_driver] + 1
                            break
            positions[driver_id] = position

with open('overtake_data.json', 'w') as file:
    json.dump(events, file)

