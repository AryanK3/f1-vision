import json

# Load data from the file
with open('rel_driver_data.json', 'r') as file:
    data = json.load(file)

# Function to remove entries with negative rel_start values
def remove_negative_rel_start(data):
    # Loop through each driver in the data
    for driver_id, entries in data.items():
        # Filter out the entries with negative rel_start
        data[driver_id] = [entry for entry in entries if entry.get("rel_start", 0) >= 0]
    
    return data

# Remove the entries with negative rel_start
updated_data = remove_negative_rel_start(data)

# Print or save the updated data
print(json.dumps(updated_data, indent=4))

# Optionally, write the updated data back to a file
with open('filtered_lap_data.json', 'w') as file:
    json.dump(updated_data, file, indent=4)
