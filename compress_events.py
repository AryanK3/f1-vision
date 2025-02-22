import json

with open('car_data.json', 'r') as file:
    data = json.load(file)

transformed_data = []

for driver_number, driver_positions in data.items():
    positions = []
    for entry in driver_positions:
        # Append only the values (not the keys)
        positions.append(list(entry.values()))

    driver_entry = {"id": int(driver_number), "positions": positions}
    transformed_data.append(driver_entry)

# Save the transformed data to a new file
with open('car_dataa.json', 'w') as output_file:
    json.dump(transformed_data, output_file)

