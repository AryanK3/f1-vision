import json
from datetime import datetime
from dateutil import parser

# Load data from a file (assuming it's in JSON format)
with open('rel_driver_data.json', 'r') as file:
    data = json.load(file)

# Function to calculate relative start time for each entry
def calculate_relative_start(data):
    # Reference time: 15:00:00 on the same day as the first entry

    # Loop through each driver in the data
    for driver_id, entries in data.items():
        # Loop through each lap entry
        for entry in entries:
            if entry["date"] is not None:

                if "rel_time" in entry:
                    del entry["rel_time"]

    return data

# Calculate relative start times and remove 'rel_time'
updated_data = calculate_relative_start(data)

# Print or save the updated data with the relative start time
print(json.dumps(updated_data, indent=4))

# Optionally, you can write the updated data back to a file
with open('rel_driver_data.json', 'w') as file:
    json.dump(updated_data, file, indent=4)
