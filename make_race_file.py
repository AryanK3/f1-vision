import os
import requests
import json
import re
from dateutil import parser
import time
import traceback


def get_driver_list(session_key):
    """
    Fetches the list of drivers for the specified session
    """
    print(f"[INFO] Fetching drivers list for session {session_key}...")
    url = "https://api.openf1.org/v1/drivers"
    params = {
        "session_key": session_key
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            drivers_data = response.json()
            driver_numbers = [driver["driver_number"] for driver in drivers_data]

            print(f"[SUCCESS] Found {len(driver_numbers)} drivers in session {session_key}")
            return driver_numbers
        else:
            print(f"[ERROR] Failed to fetch driver list: {response.status_code}")
            # Fallback list
            return [81, 1, 11, 16, 63, 55, 14, 4, 44, 27, 22, 18, 23, 3, 20, 77, 24, 2, 31, 10]
    except Exception as e:
        print(f"[ERROR] Exception while fetching driver list: {str(e)}")
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

    # Sequential processing to avoid rate limiting
    for driver_number in driver_numbers:
        positions = []
        local_params = params.copy()
        local_params["driver_number"] = driver_number

        try:
            response = requests.get(url, params=local_params)

            if response.status_code == 200:
                driver_data = response.json()

                if driver_data and len(driver_data) > 0:
                    # Debug output for the first entry
                    if driver_number == driver_numbers[0]:
                        print(f"[DEBUG] Sample position entry: {json.dumps(driver_data[0], indent=2)}")

                    for entry in driver_data:
                        position = []
                        # Handle potential missing coordinates with safe gets
                        position.append(entry.get("x", 0))
                        position.append(entry.get("y", 0))
                        position.append(entry.get("z", 0))

                        # Safely calculate relative time
                        try:
                            rel_time = (parser.isoparse(entry.get("date", start_time)) - parser.isoparse(
                                start_time)).total_seconds()
                        except (TypeError, ValueError):
                            rel_time = 0
                        position.append(rel_time)

                        positions.append(position)

                print(f"[INFO] Driver {driver_number}: Fetched {len(positions)} position records")
            else:
                print(f"[ERROR] Failed fetching data for driver {driver_number}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Exception while fetching data for driver {driver_number}: {str(e)}")

        driver_data_dict.append({
            "id": driver_number,
            "positions": positions,
        })

        # Add a small delay to avoid rate limiting
        time.sleep(0.2)

    print(f"[INFO] Writing driver data to file...")
    try:
        with open('driver_data.json', 'w') as file:
            json.dump(driver_data_dict, file, separators=(',', ':'))  # Minify JSON

        print("[SUCCESS] driver_data.json file created successfully")
    except Exception as e:
        print(f"[ERROR] Exception while writing driver_data.json: {str(e)}")

    return driver_data_dict


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

    # Sequential processing to avoid rate limiting
    for driver_number in driver_numbers:
        positions = []
        local_params = params.copy()
        local_params["driver_number"] = driver_number

        try:
            response = requests.get(url, params=local_params)

            if response.status_code == 200:
                driver_data = response.json()

                if driver_data and len(driver_data) > 0:
                    # Debug output for the first entry
                    if driver_number == driver_numbers[0]:
                        print(f"[DEBUG] Sample lap entry: {json.dumps(driver_data[0], indent=2)}")

                    for entry in driver_data:
                        lap_data = []
                        # Lap number - ensure it's not None
                        lap_data.append(entry.get("lap_number", 0))
                        # Sector times - ensure they're not None
                        lap_data.append(entry.get("duration_sector_1", 0))
                        lap_data.append(entry.get("duration_sector_2", 0))
                        lap_data.append(entry.get("duration_sector_3", 0))
                        # Total lap time - ensure it's not None
                        lap_data.append(entry.get("lap_duration", 0))

                        # Relative time at lap start - handle safely
                        try:
                            rel_time = (parser.isoparse(entry.get("date_start", start_time)) - parser.isoparse(
                                start_time)).total_seconds()
                        except (KeyError, TypeError, ValueError):
                            rel_time = 0
                        lap_data.append(rel_time)

                        positions.append(lap_data)
                    print(f"[INFO] Driver {driver_number}: Fetched {len(positions)} laps")
                else:
                    print(f"[INFO] Driver {driver_number}: No lap data found")
            else:
                print(f"[ERROR] Failed fetching lap data for driver {driver_number}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Exception while fetching lap data for driver {driver_number}: {str(e)}")

        driver_data_list.append({
            "id": driver_number,
            "positions": positions
        })

        # Add a small delay to avoid rate limiting
        time.sleep(0.2)

    print(f"[INFO] Writing lap data to file...")
    try:
        with open('lap_data.json', 'w') as file:
            json.dump(driver_data_list, file, separators=(',', ':'))  # Minify JSON

        print("[SUCCESS] lap_data.json file created successfully")
    except Exception as e:
        print(f"[ERROR] Exception while writing lap_data.json: {str(e)}")

    return driver_data_list


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

    # Sequential processing to avoid rate limiting
    for driver_number in driver_numbers:
        positions = []
        local_params = params.copy()
        local_params["driver_number"] = driver_number

        try:
            response = requests.get(url, params=local_params)

            if response.status_code == 200:
                car_data = response.json()

                if car_data and len(car_data) > 0:
                    # Debug output for the first entry
                    if driver_number == driver_numbers[0]:
                        print(f"[DEBUG] Sample car data entry: {json.dumps(car_data[0], indent=2)}")

                    for entry in car_data:
                        position = []

                        # Safely calculate relative time
                        try:
                            rel_time = (parser.isoparse(entry.get("date", start_time)) - parser.isoparse(
                                start_time)).total_seconds()
                        except (TypeError, ValueError, KeyError):
                            rel_time = 0

                        # Add data with safe gets
                        position.append(rel_time)
                        position.append(entry.get("rpm", 0))
                        position.append(entry.get("speed", 0))
                        position.append(entry.get("n_gear", 0))
                        position.append(entry.get("throttle", 0))
                        position.append(entry.get("drs", 0))
                        position.append(entry.get("brake", 0))

                        positions.append(position)
                    print(f"[INFO] Driver {driver_number}: Fetched {len(positions)} telemetry points")
                else:
                    print(f"[INFO] Driver {driver_number}: No car data found")
            else:
                print(f"[ERROR] Failed fetching car data for driver {driver_number}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Exception while fetching car data for driver {driver_number}: {str(e)}")

        driver_data_dict.append({
            "id": driver_number,
            "positions": positions,
        })

        # Add a small delay to avoid rate limiting
        time.sleep(0.2)

    print(f"[INFO] Writing car data to file...")
    try:
        with open('car_data.json', 'w') as file:
            json.dump(driver_data_dict, file, separators=(',', ':'))  # Minify JSON

        print("[SUCCESS] car_data.json file created successfully")
    except Exception as e:
        print(f"[ERROR] Exception while writing car_data.json: {str(e)}")

    return driver_data_dict


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
            driver_id = driver_data.get('id', 0)
            laps = driver_data.get('positions', [])

            for lap in laps:
                if len(lap) >= 6:  # Ensure we have all needed elements
                    # Handle None values by defaulting to 0
                    lap_number = lap[0] if lap[0] is not None else 0
                    sector_1_duration = lap[1] if lap[1] is not None else 0
                    sector_2_duration = lap[2] if lap[2] is not None else 0
                    sector_3_duration = lap[3] if lap[3] is not None else 0
                    lap_duration = lap[4] if lap[4] is not None else 0
                    rel_start = lap[5] if lap[5] is not None else 0

                    # Now all values are guaranteed to be numeric, not None
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
    except Exception as e:
        print(f"[ERROR] Exception while processing lap data file: {str(e)}")
        traceback.print_exc()

    # Get pit stop data
    try:
        print(f"[INFO] Fetching pit stop data...")
        url = "https://api.openf1.org/v1/pit"
        params = {
            "session_key": session_key,
        }

        pit_count = 0
        for driver_number in driver_numbers:
            local_params = params.copy()
            local_params["driver_number"] = driver_number

            try:
                response = requests.get(url, params=local_params)

                if response.status_code == 200:
                    pit_data = response.json()

                    if pit_data and len(pit_data) > 0:
                        # Debug output for first pit data
                        if driver_number == driver_numbers[0] and len(pit_data) > 0:
                            print(f"[DEBUG] Sample pit entry: {json.dumps(pit_data[0], indent=2)}")

                        for pit in pit_data:
                            lap_number = pit.get("lap_number", 0)

                            # Calculate relative time safely
                            try:
                                rel_time_in = (parser.isoparse(pit.get("date_of_pit_in", start_time)) - parser.isoparse(
                                    start_time)).total_seconds()
                            except (KeyError, TypeError, ValueError):
                                rel_time_in = 0

                            try:
                                rel_time_out = (
                                        parser.isoparse(pit.get("date_of_pit_out", start_time)) - parser.isoparse(
                                    start_time)).total_seconds()
                            except (KeyError, TypeError, ValueError):
                                rel_time_out = rel_time_in + 20  # Default pit stop of 20s if time out missing

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
                        print(f"[INFO] Driver {driver_number}: Added {len(pit_data)} pit stop events")
                    else:
                        print(f"[INFO] Driver {driver_number}: No pit data found")
                else:
                    print(f"[ERROR] Failed fetching pit data for driver {driver_number}: {response.status_code}")
            except Exception as e:
                print(f"[ERROR] Exception while fetching pit data for driver {driver_number}: {str(e)}")

            # Add a small delay to avoid rate limiting
            time.sleep(0.2)

        print(f"[INFO] Added {pit_count * 2} pit events")
    except Exception as e:
        print(f"[ERROR] Failed fetching pit stop data: {e}")
        traceback.print_exc()

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

            # Debug output for first position change
            if position_changes and len(position_changes) > 0:
                print(f"[DEBUG] Sample position change: {json.dumps(position_changes[0], indent=2)}")

            print(f"[INFO] Processing {len(position_changes)} position changes...")
            overtake_count = 0
            for change in position_changes:
                # Calculate relative time safely
                try:
                    rel_time = (parser.isoparse(change.get("date", start_time)) - parser.isoparse(
                        start_time)).total_seconds()
                except (KeyError, TypeError, ValueError):
                    rel_time = 0

                # Only add valid overtakes (position improvement)
                if change.get("position_change", 0) > 0:
                    events.append({
                        'type': "Overtake",
                        'time': rel_time,
                        'message': f"Driver {change.get('driver_number', 0)} overtakes to position {change.get('position', 0)}"
                    })
                    overtake_count += 1

            print(f"[INFO] Added {overtake_count} overtake events")
        else:
            print(f"[ERROR] Failed fetching position changes: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Failed fetching position changes: {e}")
        traceback.print_exc()

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

            # Debug output for first RC message
            if rc_messages and len(rc_messages) > 0:
                print(f"[DEBUG] Sample race control message: {json.dumps(rc_messages[0], indent=2)}")

            print(f"[INFO] Processing {len(rc_messages)} race control messages...")
            rc_count = 0
            for message in rc_messages:
                # Calculate relative time safely
                try:
                    rel_time = (parser.isoparse(message.get("date", start_time)) - parser.isoparse(
                        start_time)).total_seconds()
                except (KeyError, TypeError, ValueError):
                    rel_time = 0

                category = message.get("category", "Race Control")
                msg_text = message.get("message", "")

                events.append({
                    'type': category,
                    'time': rel_time,
                    'message': msg_text
                })
                rc_count += 1

            print(f"[INFO] Added {rc_count} race control messages")
        else:
            print(f"[ERROR] Failed fetching race control messages: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Failed fetching race control messages: {e}")
        traceback.print_exc()

    # Get radio messages if available
    try:
        print(f"[INFO] Fetching team radio messages...")
        url = "https://api.openf1.org/v1/team_radio"
        params = {
            "session_key": session_key,
        }

        radio_count = 0
        for driver_number in driver_numbers:
            local_params = params.copy()
            local_params["driver_number"] = driver_number

            try:
                response = requests.get(url, params=local_params)

                if response.status_code == 200:
                    radio_data = response.json()

                    if radio_data and len(radio_data) > 0:
                        # Debug output for first radio message
                        if driver_number == driver_numbers[0] and len(radio_data) > 0:
                            print(f"[DEBUG] Sample radio entry: {json.dumps(radio_data[0], indent=2)}")

                        for radio in radio_data:
                            # Calculate relative time safely
                            try:
                                rel_time = (parser.isoparse(radio.get("date", start_time)) - parser.isoparse(
                                    start_time)).total_seconds()
                            except (KeyError, TypeError, ValueError):
                                rel_time = 0

                            # Just include driver number as requested (no "unknown_message")
                            events.append({
                                'type': "Radio",
                                'time': rel_time,
                                'message': f"Driver {driver_number}"
                            })
                            radio_count += 1
                        print(f"[INFO] Driver {driver_number}: Added {len(radio_data)} radio events")
                    else:
                        print(f"[INFO] Driver {driver_number}: No radio data found")
                else:
                    print(f"[ERROR] Failed fetching radio data for driver {driver_number}: {response.status_code}")
            except Exception as e:
                print(f"[ERROR] Exception while fetching radio data for driver {driver_number}: {str(e)}")

            # Add a small delay to avoid rate limiting
            time.sleep(0.2)

        print(f"[INFO] Added {radio_count} radio events")
    except Exception as e:
        print(f"[ERROR] Failed fetching team radio data: {e}")
        traceback.print_exc()

    # Additionally, process any custom overtake data if available
    try:
        if os.path.exists('overtake_data.json'):
            print(f"[INFO] Processing custom overtake data...")
            with open('overtake_data.json', 'r') as f:
                overtake_data = json.load(f)

            custom_overtake_count = 0
            for overtake in overtake_data:
                events.append({
                    'type': "Overtake",
                    'time': overtake.get('time', 0),
                    'message': f"Driver {overtake.get('overtaker')} overtakes Driver {overtake.get('overtaken')}"
                })
                custom_overtake_count += 1

            print(f"[INFO] Added {custom_overtake_count} custom overtake events")
    except Exception as e:
        print(f"[ERROR] Exception while processing custom overtake data: {str(e)}")

    # Sort events by time
    try:
        events.sort(key=lambda event: event.get('time', 0))
    except Exception as e:
        print(f"[ERROR] Exception while sorting events: {str(e)}")

    print(f"[INFO] Writing event data to file...")
    try:
        with open('event_data.json', 'w') as file:
            json.dump(events, file, separators=(',', ':'))  # Minify JSON

        print(f"[SUCCESS] event_data.json file created successfully with {len(events)} total events")
    except Exception as e:
        print(f"[ERROR] Exception while writing event_data.json: {str(e)}")

    return events


def pullData(session_key=9472):
    """
    Fetch all data files sequentially to avoid rate limiting
    """
    print(f"[INFO] Pulling data from OpenF1 API for session {session_key}...")
    start_time = time.time()

    try:
        # Process all data sequentially to avoid rate limiting
        driver_data = make_driver_data_file(session_key)
        lap_data = make_lap_data_file(session_key)
        car_data = make_car_data_file(session_key)
        event_data = make_event_data_file(session_key)

        end_time = time.time()
        print(f"[INFO] Data pull completed in {end_time - start_time:.2f} seconds")

        return {
            "driver_data": driver_data,
            "lap_data": lap_data,
            "car_data": car_data,
            "event_data": event_data
        }
    except Exception as e:
        print(f"[ERROR] Exception during data pull: {str(e)}")
        traceback.print_exc()
        return {}


def compileData(session_key=9472):
    """
    Create all data files at once
    """
    print(f"[INFO] Compiling all F1 data files for session {session_key}...")
    start_time = time.time()

    result = pullData(session_key)

    end_time = time.time()
    print(f"[SUCCESS] All data files created successfully in {end_time - start_time:.2f} seconds!")
    return result


# Simple execution of the function when the script is run directly
if __name__ == "__main__":
    # Default session key
    session_key = 9693
    data = compileData(session_key)