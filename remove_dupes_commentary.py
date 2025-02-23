import json

# Load the JSON data from file
with open("f1_commentary.json", "r") as infile:
    data = json.load(infile)

# Create a dictionary to hold the last occurrence for each timestamp
last_occurrence = {}
for item in data:
    timestamp = item["event"]["timestamp"]
    last_occurrence[timestamp] = item  # Overwrites previous entries with same timestamp

# Convert the dictionary values back into a list
filtered_data = list(last_occurrence.values())

# Write the filtered list to a new JSON file
with open("filtered_f1_commentary.json", "w") as outfile:
    json.dump(filtered_data, outfile, indent=4)
