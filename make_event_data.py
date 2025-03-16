import requests
import json
import re
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


def make_event_data_file(session_key=9472):
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

        print(f"[INFO] Processed pit stop data successfully")
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
    except Exception as e:
        print(f"Warning: Error fetching team radio data: {e}")

    # Sort events by time
    events.sort(key=lambda event: event['time'])

    print(f"[INFO] Writing event data to file...")
    with open('event_data.json', 'w') as file:
        json.dump(events, file, indent=4)

    print(f"[SUCCESS] event_data.json file created successfully with {len(events)} total events")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        session_key = int(sys.argv[1])
        make_event_data_file(session_key)
    else:
        make_event_data_file()