import requests
import json
from datetime import datetime

# url = "https://api.openf1.org/v1/position?session_key=9472"
# response = requests.get(url)
# data = response.json()

with open('intial_positions.json', 'r') as file:
    data = json.load(file)

data.sort(key=lambda event: datetime.fromisoformat(event["date"]))

initial_positions = {}
current_positions = {}

for event in data:
    driver = event["driver_number"]
    if driver not in initial_positions:
        initial_positions[driver] = event["position"]
        current_positions[driver] = event["position"]

print("Initial Positions (Driver: Position):")
print(json.dumps(initial_positions, indent=2))

print("\nProcessing race updates:")
for event in data:
    driver = event["driver_number"]
    new_position = event["position"]
    old_position = current_positions[driver]
    if new_position != old_position:
        print(f"Driver {driver} changes from {old_position} to {new_position} at {event['date']}")
        current_positions[driver] = new_position

final_positions = {}
for driver, position in current_positions.items():
    final_positions[position] = driver

sorted_final_positions = dict(sorted(final_positions.items(), key=lambda item: item[0]))
final_list = [{"position": pos, "driver_no": driver} for pos, driver in sorted_final_positions.items()]

print("\nFinal Positions (List Format):")
print(json.dumps(final_list, indent=2))

# with open('final_positions.json', 'w') as file:
#     json.dump(final_list, file)