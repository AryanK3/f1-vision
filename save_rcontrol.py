import requests
import json
from dateutil import parser

# Define the URL for the API
url = "https://api.openf1.org/v1/race_control"

# Set the parameters for the request
params = { 
    "session_key": 9472,
}

# Initialize an empty list to store the filtered data
filtered_data = []

# Make the API request
response = requests.get(url, params=params)
    
# Check if the response status code is OK (200)
if response.status_code == 200:
    driver_data = response.json()
        
    # Check if the response contains data
    if driver_data:
        for entry in driver_data:
            # Add filtered data to the list
            filtered_data.append({
                "date": entry["date"],
                "lap_number": entry["lap_number"],
                "category": entry["category"],
                "message": entry["message"],
                "rel_time":  (parser.isoparse(entry["date"]) - parser.isoparse("2024-03-02T15:03:42+00:00")).total_seconds()
            })
else:
    print(f"Error fetching data: {response.status_code}")

with open('rel_racecontrol_data.json', 'w') as file:
    json.dump(filtered_data, file, indent=4)

print("Data saved to racecontrol_data.json")
