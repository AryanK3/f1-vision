import json

with open('rel_driver_data.json', 'r') as file:
    data = json.load(file)

compressed_data = {}
for key, value in data.items():
    compressed_data[key] = [list(entry.values()) for entry in value]

with open('compressed_lap_data.json', 'w') as file:
    json.dump(compressed_data, file)
