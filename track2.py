import json
import time

# Load the data from the new JSON file
with open('lap_data.json', 'r') as f:
    data = json.load(f)

def track_lap_and_sector(data):
    race_timer = 0.0
    events = []

    for driver_data in data:
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
                'time': sector_1_duration,
                'message': f"Driver {driver_id} completed sector 1 of lap {lap_number} in {sector_1_duration:.3f} seconds."
            })

            sector_1_end_time = sector_1_duration
            sector_2_end_time = sector_1_end_time + sector_2_duration
            events.append({
                'time': sector_2_end_time,
                'message': f"Driver {driver_id} completed sector 2 of lap {lap_number} in {sector_2_duration:.3f} seconds."
            })

            sector_2_end_time = sector_2_end_time or sector_1_end_time + sector_2_duration
            sector_3_end_time = sector_2_end_time + sector_3_duration
            events.append({
                'time': sector_3_end_time,
                'message': f"Driver {driver_id} completed sector 3 of lap {lap_number} in {sector_3_duration:.3f} seconds."
            })

            events.append({
                'time': lap_duration,
                'message': f"Driver {driver_id} completed lap {lap_number} in {lap_duration:.3f} seconds."
            })

    events.sort(key=lambda event: event['time'])

    # Simulate the race by printing events based on the race timer
    event_index = 0
    while event_index < len(events):
        event = events[event_index]

        if race_timer < event['time']:
            race_timer = event['time']

        print(f"Time {race_timer:.3f}s: {event['message']}")

        event_index += 1

        time.sleep(0.1)

track_lap_and_sector(data)
