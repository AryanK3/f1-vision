import requests
import json
from dateutil import parser


def get_driver_list(session_key):
    """
    Fetches the list of drivers for the specified session
    """
    print(f"[INFO] Fetching drivers list for session {session_key}...")
    url = "https://api.openf1.org/v1/drivers"
    params = {
        "session_key": session_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        drivers_data = response.json()
        driver_numbers = [driver["driver_number"] for driver in drivers_data]

        print(f"[SUCCESS] Found {len(driver_numbers)} drivers in session {session_key}")
        print("Drivers in this session:")
        for driver in drivers_data:
            print(f"  Number: {driver['driver_number']}, Name: {driver.get('full_name', 'Unknown')}")

        return driver_numbers
    else:
        print(f"[ERROR] Failed to fetch driver list: {response.status_code}")
        # Fallback list
        return [81, 1, 11, 16, 63, 55, 14, 4, 44, 27, 22, 18, 23, 3, 20, 77, 24, 2, 31, 10]


def make_lap_data_file(session_key=9472):
    print(f"[INFO] Starting lap data fetch for session {session_key}")
    url = "https://api.openf1.org/v1/laps"
    driver_numbers = get_driver_list(session_key)
    start_time = "2024-03-02T15:03:42+00:00"

    params = {
        "session_key": session_key,
    }

    driver_data_list = []

    for driver_number in driver_numbers:
        params["driver_number"] = driver_number
        response = requests.get(url, params=params)

        if response.status_code == 200:
            driver_data = response.json()
            positions = []

            if driver_data:
                for entry in driver_data:
                    lap_data = []
                    # Lap number
                    lap_data.append(entry["lap_number"])
                    # Sector 1 time
                    lap_data.append(entry.get("duration_sector_1", 0))
                    # Sector 2 time
                    lap_data.append(entry.get("duration_sector_2", 0))
                    # Sector 3 time
                    lap_data.append(entry.get("duration_sector_3", 0))
                    # Total lap time
                    lap_data.append(entry.get("lap_duration", 0))
                    # Relative time at lap start
                    try:
                        rel_time = (parser.isoparse(entry["date_start"]) - parser.isoparse(start_time)).total_seconds()
                    except (KeyError, TypeError):
                        rel_time = 0
                    lap_data.append(rel_time)

                    positions.append(lap_data)

            driver_data_list.append({
                "id": driver_number,
                "positions": positions
            })
            print(f"[INFO] Driver {driver_number}: Fetched {len(positions)} laps")
        else:
            print(f"[ERROR] Failed fetching data for driver {driver_number}: {response.status_code}")

    print(f"[INFO] Writing lap data to file...")
    with open('lap_data.json', 'w') as file:
        json.dump(driver_data_list, file, indent=4)

    print("[SUCCESS] lap_data.json file created successfully")


# Simple execution of the function when the script is run directly
if __name__ == "__main__":
    make_lap_data_file(9472)