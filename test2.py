import json

# Load tyre and pit data
with open('tyre_data.json', 'r') as f:
    tyre_data = json.load(f)
with open('pit_data.json', 'r') as f:
    pit_data = json.load(f)

events = []

# Iterate through each driver's pit data
for driver_data in pit_data:
    driver_id = driver_data['id']
    pits = driver_data['positions']

    # Process each pit stop event for this driver
    for pit in pits:
        lap_number = pit[0]  # Lap number when the driver enters the pit
        pit_duration = pit[1]  # Pit duration in seconds
        rel_start = pit[2]  # Relative start time for the pit

        # Retrieve tyre data for the driver at the current lap number (match pit lap with tyre data lap)
        driver_tyre_info = next(
            (item for item in tyre_data if item['driver_number'] == driver_id and item['lap_end'] == lap_number),
            None
        )

        if driver_tyre_info:
            tyre_type = driver_tyre_info['compound']  # Tyre type (compound) at the time of the pit

        # Add the pit entry event with the tyre info at the entry
        events.append({
            'type': "Pits",
            'time': rel_start,
            'message': f"Driver {driver_id} (Tyre: {tyre_type}) enters pit in lap {lap_number} at {rel_start:.3f} seconds."
        })

        # Find the next tyre data for the driver after the pit stop (if applicable)
        next_tyre_info = next(
            (item for item in tyre_data if item['driver_number'] == driver_id and item['lap_start'] > lap_number),
            None
        )

        if next_tyre_info:
            next_tyre_type = next_tyre_info['compound']
        else:
            next_tyre_type = tyre_type  # If no new tyre data found, keep the same tyre type

        # Add the pit exit event with the new tyre info (next tire info after pit)
        events.append({
            'type': "Pits",
            'time': rel_start + pit_duration,
            'message': f"Driver {driver_id} (Tyre: {next_tyre_type}) exits pit in lap {lap_number} at {rel_start + pit_duration:.3f} seconds."
        })

events.sort(key=lambda event: event['time'])

# Optionally, print or save the events
for event in events:
    print(event)
