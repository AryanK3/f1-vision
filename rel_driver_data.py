import requests
import json
from dateutil import parser

url = "https://api.openf1.org/v1/intervals"
driver_numbers = [81, 1, 11,  16, 63, 55, 14, 4, 44, 27, 22, 18, 23, 3, 20, 77, 24, 2, 31, 10]

params = {  
    "session_key": 9472,
    "date>": "2024-03-02T15:03:42+00:00",   
    "date<": "2024-03-02T17:00:00.000", 
}

driver_data_dict = []

for driver_number in driver_numbers:
    positions = []
    params["driver_number"] = driver_number
    response = requests.get(url, params=params)

    if response.status_code == 200:
        driver_data = response.json()
        
        if driver_data:
            for entry in driver_data:
                position = []
                position.append((parser.isoparse(entry["date"]) - parser.isoparse("2024-03-02T15:03:42+00:00")).total_seconds())
                position.append(entry["driver_number"])
                position.append(entry["interval"])
                positions.append(position)
    driver_data_dict.append({
        "id": driver_number, 
        "positions": positions, 
    })

with open('intervals_data.json', 'w') as file:
    json.dump(driver_data_dict, file)
