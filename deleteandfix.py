import json

# Path to your JSON file
file_path = 'intervals_data.json'

# Read the data from the file
with open(file_path, 'r') as file:
    data = json.load(file)

# Loop through the data and remove the second element (id) from each position
for entry in data:
    for pos in entry['positions']:
        # Keep only the 0th and 2nd index of each position, remove the 1st index (driver id)
        pos.pop(1)

# Write the modified data back to a new file or overwrite the old file
with open('cleaned_data.json', 'w') as outfile:
    json.dump(data, outfile)