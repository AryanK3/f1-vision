import json

# Load the original data from a file
with open('rel_lapp_data.json', 'r') as file:
    data = json.load(file)

# Initialize an empty list to store the transformed data
transformed_data = []

# Iterate through each item in the original data
for key, laps in data.items():
    transformed_positions = []
    
    for lap in laps:
        # Extract the values you want to store as an array
        lap_number = lap['lap_number']
        duration_sector_1 = lap['duration_sector_1']
        duration_sector_2 = lap['duration_sector_2']
        duration_sector_3 = lap['duration_sector_3']
        lap_duration = lap['lap_duration']
        rel_start = lap['rel_start']
        
        # Add the lap data as an array (without keys) in the desired format
        transformed_positions.append([lap_number, duration_sector_1, duration_sector_2, duration_sector_3, lap_duration, rel_start])

    # Store the transformed data (without keys) in the desired format
    transformed_data.append({
        "id": int(key),
        "positions": transformed_positions
    })

# Output the transformed data to a new file
with open('lap_data.json', 'w') as outfile:
    json.dump(transformed_data, outfile)
