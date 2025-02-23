import json

# Define the path to your JSON file
file_path = 'name_data.json'

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize an empty list to store the converted data
result = []

# Convert the data
for entry in data:
    print(entry)
    # Assuming entry[0] is the index or identifier, create a dictionary with the corresponding data
    result.append({int(entry[0]): {"name": entry[1], "country": entry[2], "team": entry[3], "img_link": entry[4]}})

# Optionally, write the result back to a new JSON file
with open('new_name_data.json', 'w', encoding='utf-8') as output_file:
    json.dump(result, output_file)
