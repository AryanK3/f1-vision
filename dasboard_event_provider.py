import requests
import json
from datetime import datetime

# Fetch the data from the API
url = "https://api.openf1.org/v1/position?session_key=9472"
response = requests.get(url)
data = response.json()  # This returns a list of dictionaries

# Sort events by their timestamp to process them chronologically
data.sort(key=lambda event: datetime.fromisoformat(event["date"]))

# Initialize dictionaries for initial and current positions
initial_positions = {}
current_positions = {}

# Record the initial placement for each driver (the first occurrence)
for event in data:
    driver = event["driver_number"]
    if driver not in initial_positions:
        initial_positions[driver] = event["position"]
        current_positions[driver] = event["position"]

print("Initial Positions (Driver: Position):")
print(json.dumps(initial_positions, indent=2))

# Process each event to update the driver's position during the race
print("\nProcessing race updates:")
for event in data:
    driver = event["driver_number"]
    new_position = event["position"]
    old_position = current_positions[driver]
    if new_position != old_position:
        print(f"Driver {driver} changes from {old_position} to {new_position} at {event['date']}")
        current_positions[driver] = new_position

# Invert the mapping so that the key is the final position and the value is the driver number.
final_positions = {}
for driver, position in current_positions.items():
    final_positions[position] = driver

# Sort the final positions by position (the key)
sorted_final_positions = dict(sorted(final_positions.items(), key=lambda item: item[0]))

print("\nFinal Positions (Position: Driver) Sorted:")
print(json.dumps(sorted_final_positions, indent=2))
