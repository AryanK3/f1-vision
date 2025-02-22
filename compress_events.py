import json

# Load data from a file
file_path = 'events_data.json'

with open(file_path, 'r') as file:
    data = json.load(file)

# Convert each item into an array without keys, and round time values
processed_data = [
    [entry['type'], round(entry['time'], 3), entry['message']] for entry in data
]

# Print or save the processed data
print(processed_data)

# Optionally save the result to a new file
with open('event_data.json', 'w') as outfile:
    json.dump(processed_data, outfile)
