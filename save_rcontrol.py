import requests
import json
from dateutil import parser

# Define the URL for the API
url = "https://api.openf1.org/v1/stints"

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
        # Filter the required data or perform any necessary manipulation
        for stint in driver_data:
            filtered_data.append({
                "driver_number": stint["driver_number"],
                "lap_start": stint["lap_start"],
                "lap_end": stint["lap_end"],
                "compound": stint["compound"],
                "tyre_age_at_start": stint["tyre_age_at_start"]
            })
        
        # Store the filtered data into a JSON file
        with open('tyre_data.json', 'w') as outfile:
            json.dump(filtered_data, outfile, indent=4)
else:
    print(f"Error: {response.status_code}. Unable to retrieve data.")
