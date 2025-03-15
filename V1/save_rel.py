import json
from datetime import datetime
from dateutil import parser

# Load data from a file (assuming it's in JSON format)
with open('rel_driver_data.json', 'r') as file:
    data = json.load(file)

# Function to calculate relative start time for each entry
def calculate_relative_start(data):
    # Reference time: 15:00:00 on the same day as the first entry
    reference_time = parser.isoparse("2024-03-02T15:03:42+00:00")
    
    # Loop through each driver in the data
    for driver_id, entries in data.items():
        # Loop through each lap entry
        for entry in entries:
            if entry["date"] is not None:
                # Parse the actual date-time of the entry
                current_time = parser.isoparse(entry["date"])
                
                # Calculate the relative start time by subtracting reference_time from current_time
                rel_start = (current_time - reference_time).total_seconds()
                
                # Add the relative start time (rel_start) to the entry
                entry["rel_start"] = rel_start

    return data

# Calculate relative start times
updated_data = calculate_relative_start(data)

# Print or save the updated data with the relative start time
print(json.dumps(updated_data, indent=4))

# Optionally, you can write the updated data back to a file
with open('rel_driver_data.json', 'w') as file:
    json.dump(updated_data, file, indent=4)
