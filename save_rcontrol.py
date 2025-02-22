import requests
import json
from dateutil import parser

# Define the URL for the API
url = "https://api.openf1.org/v1/team_radio"

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
            driver_num = entry['driver_number']
            rel_time = (parser.isoparse(entry['date']) - parser.isoparse("2024-03-02T15:03:42+00:00")).total_seconds()
            link = entry['recording_url']
            filtered_data.append([driver_num, rel_time, link])


else:
    print(f"Error fetching data: {response.status_code}")

with open('radio_data.json', 'w') as file:
    json.dump(filtered_data, file)


