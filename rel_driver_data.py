import requests
import json
from dateutil import parser

url = "https://api.openf1.org/v1/car_data"

driver_numbers = [81, 1, 11,  16, 63, 55, 14, 4, 44, 27, 22, 18, 23, 3, 20, 77, 24, 2, 31, 10]

params = { 
    "session_key": 9472,
    "date>": "2024-03-02T15:03:42+00:00",   
    "date<": "2024-03-02T17:00:00.000", 
}

driver_data_dict = {}

for driver_number in driver_numbers:
    params["driver_number"] = driver_number
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        driver_data = response.json()
        
        # Store data by driver number
        if driver_data:
            driver_data_dict[driver_number] = []
            for entry in driver_data:
                driver_data_dict[driver_number].append({
                    "rel_time": (parser.isoparse(entry["date"]) - parser.isoparse("2024-03-02T15:03:42+00:00")).total_seconds(),
                    "rpm": entry["rpm"],
                    "speed": entry["speed"],
                    "n_gear": entry["n_gear"],
                    "throttle": entry["throttle"],
                    "drs": entry["drs"],
                    "brake": entry["brake"]
                })
        print(f"Data fetched for driver {driver_number}")

    else:
        print(f"Error fetching data for driver number {driver_number}: {response.status_code}")

with open('car_data.json', 'w') as file:
    json.dump(driver_data_dict, file, indent=4)
