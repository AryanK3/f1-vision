import requests
import json
from dateutil import parser
import re


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
    """
    Creates driver_data.json with position data
    """
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

            if driver_data:
                for entry in driver_data:
                    position = []
                    # X coordinate
                    position.append(entry["x"])
                    # Y coordinate
                    position.append(entry["y"])
                    # Z coordinate (if available, otherwise 0)
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
    return driver_data_dict

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
                    # X coordinate
                    position.append(entry["x"])
                    # Y coordinate
                    position.append(entry["y"])
                    # Z coordinate (if available, otherwise 0)
                    position.append(entry.get("z", 0))
                    # Relative time from start
                    position.append((parser.isoparse(entry["date"]) - parser.isoparse(start_time)).total_seconds())

                    positions.append(position)

        driver_data_dict.append({
            "id": driver_number,
            "positions": positions,
        })
        sys.stdout.write(f"\rProcessed driver {driver_number}, got {len(positions)} positions")
        sys.stdout.flush()

    with open('driver_data.json', 'w') as file:
        json.dump(driver_data_dict, file, indent=4)

    print("\ndriver_data.json file created successfully")


def make_lap_data_file(session_key=9472):
    """
    Creates lap_data.json with lap timing data
    """
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
    return driver_data_list

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
            sys.stdout.write(f"\rProcessed driver {driver_number}, got {len(positions)} laps")
            sys.stdout.flush()

    with open('lap_data.json', 'w') as file:
        json.dump(driver_data_list, file, indent=4)

    print("\nlap_data.json file created successfully")


def make_car_data_file(session_key=9472):
    """
    Creates car_data.json with telemetry data
    """
    print(f"[INFO] Starting car data fetch for session {session_key}")
    url = "https://api.openf1.org/v1/car_data"
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
            car_data = response.json()

            if car_data:
                for entry in car_data:
                    position = []
                    # Relative time from start
                    position.append((parser.isoparse(entry["date"]) - parser.isoparse(start_time)).total_seconds())
                    # RPM
                    position.append(entry.get("rpm", 0))
                    # Speed
                    position.append(entry.get("speed", 0))
                    # N gear
                    position.append(entry.get("n_gear", 0))
                    # Throttle
                    position.append(entry.get("throttle", 0))
                    # DRS
                    position.append(entry.get("drs", 0))
                    # Brake
                    position.append(entry.get("brake", 0))

                    positions.append(position)

            driver_data_dict.append({
                "id": driver_number,
                "positions": positions,
            })
            print(f"[INFO] Driver {driver_number}: Fetched {len(positions)} telemetry points")
        else:
            print(f"[ERROR] Failed fetching car data for driver {driver_number}: {response.status_code}")

    print(f"[INFO] Writing car data to file...")
    with open('car_data.json', 'w') as file:
        json.dump(driver_data_dict, file, indent=4)

    print("[SUCCESS] car_data.json file created successfully")
    return driver_data_dict

    driver_data_dict = []

    for driver_number in driver_numbers:
        positions = []
        params["driver_number"] = driver_number
        response = requests.get(url, params=params)

        if response.status_code == 200:
            car_data = response.json()

            if car_data:
                for entry in car_data:
                    position = []
                    # Relative time from start
                    position.append((parser.isoparse(entry["date"]) - parser.isoparse(start_time)).total_seconds())
                    # RPM
                    position.append(entry.get("rpm", 0))
                    # Speed
                    position.append(entry.get("speed", 0))
                    # N gear
                    position.append(entry.get("n_gear", 0))
                    # Throttle
                    position.append(entry.get("throttle", 0))
                    # DRS
                    position.append(entry.get("drs", 0))
                    # Brake
                    position.append(entry.get("brake", 0))

                    positions.append(position)

            driver_data_dict.append({
                "id": driver_number,
                "positions": positions,
            })
            sys.stdout.write(f"\rProcessed driver {driver_number}, got {len(positions)} telemetry points")
            sys.stdout.flush()

    with open('car_data.json', 'w') as file:
        json.dump(driver_data_dict, file, indent=4)

    print("\ncar_data.json file created successfully")


def make_event_data_file(session_key=9472):
    """
    Creates event_data.json with various race events
    """
    print(f"[INFO] Starting event data fetch for session {session_key}")
    start_time = "2024-03-02T15:03:42+00:00"
    driver_numbers = get_driver_list(session_key)
    events = []

    # Get lap data for sector completion events
    try:
        print(f"[INFO] Attempting to read lap_data.json...")
        with open('lap_data.json', 'r') as f:
            lap_data = json.load(f)

        print(f"[INFO] Processing lap data for events...")
        lap_events_count = 0
        for driver_data in lap_data:
            driver_id = driver_data['id']
            laps = driver_data['positions']

            for lap in laps:
                lap_number = lap[0]
                sector_1_duration = lap[1]
                sector_2_duration = lap[2]
                sector_3_duration = lap[3]
                lap_duration = lap[4]
                rel_start = lap[5]

                events.append({
                    'type': "Laps",
                    'time': rel_start + sector_1_duration,
                    'message': f"Driver {driver_id} completed sector 1 of lap {lap_number}"
                })

                events.append({
                    'type': "Laps",
                    'time': rel_start + sector_1_duration + sector_2_duration,
                    'message': f"Driver {driver_id} completed sector 2 of lap {lap_number}"
                })

                events.append({
                    'type': "Laps",
                    'time': rel_start + sector_1_duration + sector_2_duration + sector_3_duration,
                    'message': f"Driver {driver_id} completed sector 3 of lap {lap_number}"
                })

                events.append({
                    'type': "Laps",
                    'time': rel_start + lap_duration,
                    'message': f"Driver {driver_id} completed lap {lap_number}"
                })
                lap_events_count += 4

        print(f"[INFO] Added {lap_events_count} lap events")
    except FileNotFoundError:
        print("[WARNING] lap_data.json not found. Skipping lap events.")

    # Get pit stop data
    try:
        print(f"[INFO] Fetching pit stop data...")
        url = "https://api.openf1.org/v1/pit"
        params = {
            "session_key": session_key,
        }

        pit_count = 0
        for driver_number in driver_numbers:
            params["driver_number"] = driver_number
            response = requests.get(url, params=params)

            if response.status_code == 200:
                pit_data = response.json()

                if pit_data:
                    for pit in pit_data:
                        lap_number = pit.get("lap_number", 0)
                        pit_duration = pit.get("duration", 0)

                        # Calculate relative time
                        try:
                            rel_time_in = (parser.isoparse(pit["date_of_pit_in"]) - parser.isoparse(
                                start_time)).total_seconds()
                            rel_time_out = (parser.isoparse(pit["date_of_pit_out"]) - parser.isoparse(
                                start_time)).total_seconds()
                        except (KeyError, TypeError):
                            rel_time_in = 0
                            rel_time_out = 0

                        events.append({
                            'type': "Pits",
                            'time': rel_time_in,
                            'message': f"Driver {driver_number} enters pit in lap {lap_number}"
                        })

                        events.append({
                            'type': "Pits",
                            'time': rel_time_out,
                            'message': f"Driver {driver_number} exits pit in lap {lap_number}"
                        })
                        pit_count += 1

        print(f"[INFO] Added {pit_count * 2} pit events")
    except Exception as e:
        print(f"[ERROR] Failed fetching pit stop data: {e}")

    # Get overtake events
    try:
        print(f"[INFO] Fetching position changes data...")
        url = "https://api.openf1.org/v1/position_changes"
        params = {
            "session_key": session_key,
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            position_changes = response.json()

            print(f"[INFO] Processing {len(position_changes)} position changes...")
            overtake_count = 0
            for change in position_changes:
                rel_time = (parser.isoparse(change["date"]) - parser.isoparse(start_time)).total_seconds()
                if change["position_change"] > 0:  # Overtaking happened
                    events.append({
                        'type': "Overtake",
                        'time': rel_time,
                        'message': f"Driver {change['driver_number']} overtakes to position {change['position']}"
                    })
                    overtake_count += 1

            print(f"[INFO] Added {overtake_count} overtake events")
    except Exception as e:
        print(f"[ERROR] Failed fetching position changes: {e}")

    # Get race control messages
    try:
        print(f"[INFO] Fetching race control messages...")
        url = "https://api.openf1.org/v1/race_control_messages"
        params = {
            "session_key": session_key,
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            rc_messages = response.json()

            print(f"[INFO] Processing {len(rc_messages)} race control messages...")
            rc_count = 0
            for message in rc_messages:
                rel_time = (parser.isoparse(message["date"]) - parser.isoparse(start_time)).total_seconds()
                category = message.get("category", "Race Control")

                events.append({
                    'type': category,
                    'time': rel_time,
                    'message': message.get("message", "")
                })
                rc_count += 1

            print(f"[INFO] Added {rc_count} race control messages")
    except Exception as e:
        print(f"[ERROR] Failed fetching race control messages: {e}")

    # Get radio messages if available
    try:
        print(f"[INFO] Fetching team radio messages...")
        url = "https://api.openf1.org/v1/team_radio"
        params = {
            "session_key": session_key,
        }

        radio_count = 0
        for driver_number in driver_numbers:
            params["driver_number"] = driver_number
            response = requests.get(url, params=params)

            if response.status_code == 200:
                radio_data = response.json()

                if radio_data:
                    for radio in radio_data:
                        rel_time = (parser.isoparse(radio["date"]) - parser.isoparse(start_time)).total_seconds()
                        audio_url = radio.get("audio_url", "")

                        # Extract code from URL if possible
                        code = ""
                        if audio_url:
                            match = re.search(r'([^/]+)(?=\.mp3)', audio_url)
                            if match:
                                code = match.group(0)

                        events.append({
                            'type': "Radio",
                            'time': rel_time,
                            'message': f"Driver {driver_number}: {code}"
                        })
                        radio_count += 1

        print(f"[INFO] Added {radio_count} radio events")
    except Exception as e:
        print(f"[ERROR] Failed fetching team radio data: {e}")

    # Sort events by time
    events.sort(key=lambda event: event['time'])

    print(f"[INFO] Writing event data to file...")
    with open('event_data.json', 'w') as file:
        json.dump(events, file, indent=4)

    print(f"[SUCCESS] event_data.json file created successfully with {len(events)} total events")
    return events

    # Get lap data for sector completion events
    try:
        with open('lap_data.json', 'r') as f:
            lap_data = json.load(f)

        for driver_data in lap_data:
            driver_id = driver_data['id']
            laps = driver_data['positions']

            for lap in laps:
                lap_number = lap[0]
                sector_1_duration = lap[1]
                sector_2_duration = lap[2]
                sector_3_duration = lap[3]
                lap_duration = lap[4]
                rel_start = lap[5]

                events.append({
                    'type': "Laps",
                    'time': rel_start + sector_1_duration,
                    'message': f"Driver {driver_id} completed sector 1 of lap {lap_number}"
                })

                events.append({
                    'type': "Laps",
                    'time': rel_start + sector_1_duration + sector_2_duration,
                    'message': f"Driver {driver_id} completed sector 2 of lap {lap_number}"
                })

                events.append({
                    'type': "Laps",
                    'time': rel_start + sector_1_duration + sector_2_duration + sector_3_duration,
                    'message': f"Driver {driver_id} completed sector 3 of lap {lap_number}"
                })

                events.append({
                    'type': "Laps",
                    'time': rel_start + lap_duration,
                    'message': f"Driver {driver_id} completed lap {lap_number}"
                })

        print(f"Added {len(events)} lap events")
    except FileNotFoundError:
        print("Warning: lap_data.json not found. Skipping lap events.")

    # Get pit stop data
    try:
        print(f"[INFO] Fetching pit stop data...")
        url = "https://api.openf1.org/v1/pit"
        params = {
            "session_key": session_key,
        }

        pit_count = 0
        for driver_number in driver_numbers:
            params["driver_number"] = driver_number
            response = requests.get(url, params=params)

            if response.status_code == 200:
                pit_data = response.json()

                if pit_data:
                    for pit in pit_data:
                        lap_number = pit.get("lap_number", 0)
                        pit_duration = pit.get("duration", 0)

                        # Calculate relative time
                        try:
                            rel_time_in = (parser.isoparse(pit["date_of_pit_in"]) - parser.isoparse(
                                start_time)).total_seconds()
                            rel_time_out = (parser.isoparse(pit["date_of_pit_out"]) - parser.isoparse(
                                start_time)).total_seconds()
                        except (KeyError, TypeError):
                            rel_time_in = 0
                            rel_time_out = 0

                        events.append({
                            'type': "Pits",
                            'time': rel_time_in,
                            'message': f"Driver {driver_number} enters pit in lap {lap_number}"
                        })

                        events.append({
                            'type': "Pits",
                            'time': rel_time_out,
                            'message': f"Driver {driver_number} exits pit in lap {lap_number}"
                        })
                        pit_count += 1

        print(f"Added {pit_count * 2} pit events")
    except Exception as e:
        print(f"Warning: Error fetching pit stop data: {e}")

    # Get overtake events
    try:
        url = "https://api.openf1.org/v1/position_changes"
        params = {
            "session_key": 9472,
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            position_changes = response.json()

            overtake_count = 0
            for change in position_changes:
                rel_time = (parser.isoparse(change["date"]) - parser.isoparse(start_time)).total_seconds()
                if change["position_change"] > 0:  # Overtaking happened
                    events.append({
                        'type': "Overtake",
                        'time': rel_time,
                        'message': f"Driver {change['driver_number']} overtakes to position {change['position']}"
                    })
                    overtake_count += 1

            print(f"Added {overtake_count} overtake events")
    except Exception as e:
        print(f"Warning: Error fetching position changes: {e}")

    # Get race control messages
    try:
        url = "https://api.openf1.org/v1/race_control_messages"
        params = {
            "session_key": 9472,
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            rc_messages = response.json()

            rc_count = 0
            for message in rc_messages:
                rel_time = (parser.isoparse(message["date"]) - parser.isoparse(start_time)).total_seconds()
                category = message.get("category", "Race Control")

                events.append({
                    'type': category,
                    'time': rel_time,
                    'message': message.get("message", "")
                })
                rc_count += 1

            print(f"Added {rc_count} race control events")
    except Exception as e:
        print(f"Warning: Error fetching race control messages: {e}")

    # Get radio messages if available
    try:
        url = "https://api.openf1.org/v1/team_radio"
        params = {
            "session_key": 9472,
        }

        radio_count = 0
        for driver_number in driver_numbers:
            params["driver_number"] = driver_number
            response = requests.get(url, params=params)

            if response.status_code == 200:
                radio_data = response.json()

                if radio_data:
                    for radio in radio_data:
                        rel_time = (parser.isoparse(radio["date"]) - parser.isoparse(start_time)).total_seconds()
                        audio_url = radio.get("audio_url", "")

                        # Extract code from URL if possible
                        code = ""
                        if audio_url:
                            match = re.search(r'([^/]+)(?=\.mp3)', audio_url)
                            if match:
                                code = match.group(0)

                        events.append({
                            'type': "Radio",
                            'time': rel_time,
                            'message': f"Driver {driver_number}: {code}"
                        })
                        radio_count += 1

        print(f"Added {radio_count} radio events")
    except Exception as e:
        print(f"Warning: Error fetching team radio data: {e}")

    # Sort events by time
    events.sort(key=lambda event: event['time'])

    with open('event_data.json', 'w') as file:
        json.dump(events, file, indent=4)

    print(f"event_data.json file created successfully with {len(events)} total events")


def pullData(session_key=9472):
    """
    Fetch all data files individually
    """
    print(f"[INFO] Pulling data from OpenF1 API for session {session_key}...")
    driver_data = make_driver_data_file(session_key)
    lap_data = make_lap_data_file(session_key)
    car_data = make_car_data_file(session_key)
    event_data = make_event_data_file(session_key)

    return {
        "driver_data": driver_data,
        "lap_data": lap_data,
        "car_data": car_data,
        "event_data": event_data
    }


def compileData(session_key=9472):
    """
    Create all data files at once
    """
    print(f"[INFO] Compiling all F1 data files for session {session_key}...")
    result = pullData(session_key)
    print("[SUCCESS] All data files created successfully!")
    return result


# Simple execution of the function when the script is run directly
if __name__ == "__main__":
    # Default session key
    session_key = 9472
    data = compileData(session_key)