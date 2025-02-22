import json

with open('compressed_driver_data.json', 'r') as file:
    original_data = json.load(file)

result = []

for key, value in original_data.items():
    result.append({
        "id": int(key),        
        "positions": value      
    })


with open('driver_data.json', 'w') as outfile:
    json.dump(result, outfile)

