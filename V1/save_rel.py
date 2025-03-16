import json
from datetime import datetime
from dateutil import parser

with open('rel_driver_data.json', 'r') as file:
    data = json.load(file)

def calculate_relative_start(data):
    reference_time = parser.isoparse("2024-03-02T15:03:42+00:00")
    
    for driver_id, entries in data.items():
        for entry in entries:
            if entry["date"] is not None:
                current_time = parser.isoparse(entry["date"])
                
                rel_start = (current_time - reference_time).total_seconds()
                
                entry["rel_start"] = rel_start

    return data

updated_data = calculate_relative_start(data)

print(json.dumps(updated_data, indent=4))

with open('rel_driver_data.json', 'w') as file:
    json.dump(updated_data, file, indent=4)
