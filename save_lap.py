import requests
import json

url = "https://api.openf1.org/v1/laps"

driver_numbers = [81, 1, 11,  16, 63, 55, 14, 4, 44, 27, 22, 18, 23, 3, 20, 77, 24, 2, 31, 10]

params = { 
    "session_key": 9472,
}

driver_data_dict = {}

for driver_number in driver_numbers:
    params["driver_number"] = driver_number
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        driver_data = response.json()
        
        if driver_data:
            driver_data_dict[driver_number] = []
            for entry in driver_data:
                driver_data_dict[driver_number].append({
                    "date": entry["date_start"],
                    "lap_number": entry["lap_number"],
                    "duration_sector_1": entry["duration_sector_1"],
                    "duration_sector_2": entry["duration_sector_2"],
                    "duration_sector_3": entry["duration_sector_3"],
                    "lap_duration": entry["lap_duration"]
                })
        print(f"Data fetched for driver {driver_number}")

    else:
        print(f"Error fetching data for driver number {driver_number}: {response.status_code}")

with open('lap_data.json', 'w') as file:
    json.dump(driver_data_dict, file, indent=4)
