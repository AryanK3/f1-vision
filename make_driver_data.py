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


def make_driver_data_file(session_key=9472):
    print(f"[INFO] Starting driver data fetch for session {session_key}")
    url = "https://api.openf1.org/v1/position"
    driver_numbers = get_driver_list(session_key)
    start_time = "2024-03-02T15:03:42+00:00"

    params = {
        "session_key": session_key,
        "date>": start_time,
        "date<": "2024-03-02T17:00:00.000",
    }

    driver_data_dict = []

    for driver_number in driver_numbers:
        positions = []
        params["driver_number"] = driver_number
        response = requests.get(url, params=params)

        if response.status_code == 200:
            driver_data = response.json()

            if driver_data and len(driver_data) > 0:
                # Debug output for the first entry
                if driver_number == driver_numbers[0]:
                    print(f"[DEBUG] Sample entry structure: {json.dumps(driver_data[0], indent=2)}")

                for entry in driver_data:
                    position = []
                    # Handle potential missing coordinates
                    # X coordinate (use 0 if missing)
                    position.append(entry.get("x", 0))
                    # Y coordinate (use 0 if missing)
                    position.append(entry.get("y", 0))
                    # Z coordinate (always use 0 if missing)
                    position.append(entry.get("z", 0))
                    # Relative time from start
                    position.append((parser.isoparse(entry["date"]) - parser.isoparse(start_time)).total_seconds())

                    positions.append(position)

        driver_data_dict.append({
            "id": driver_number,
            "positions": positions,
        })
        print(f"[INFO] Driver {driver_number}: Fetched {len(positions)} position records")

    print(f"[INFO] Writing driver data to file...")
    with open('driver_data.json', 'w') as file:
        json.dump(driver_data_dict, file, indent=4)

    print("[SUCCESS] driver_data.json file created successfully")


# Simple execution of the function when the script is run directly
if __name__ == "__main__":
    make_driver_data_file(9472)