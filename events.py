import json
import time

def track():
    race_timer = 0.0
    events = []

    with open('lap_data.json', 'r') as f:
        data = json.load(f)
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
                'type': "Laps",
                'time': rel_start + sector_1_duration,
                'message': f"Driver {driver_id} completed sector 1 of lap {lap_number} in {sector_1_duration:.3f} seconds."
            })


            events.append({
                'type': "Laps",
                'time': rel_start + sector_1_duration + sector_2_duration,
                'message': f"Driver {driver_id} completed sector 2 of lap {lap_number} in {sector_2_duration:.3f} seconds."
            })


            events.append({
                'type': "Laps",
                'time': rel_start + sector_1_duration + sector_2_duration + sector_3_duration,
                'message': f"Driver {driver_id} completed sector 3 of lap {lap_number} in {sector_3_duration:.3f} seconds."
            })

            events.append({
                'type': "Laps",
                'time': lap_duration,
                'message': f"Driver {driver_id} completed lap {lap_number} in {lap_duration:.3f} seconds."
            })

    with open('pit_data.json', 'r') as f:
        data = json.load(f)
    for driver_data in data:
        driver_id = driver_data['id']
        pits = driver_data['positions']

        for pit in pits:
            lap_number = pit[0]
            pit_duration = pit[1]
            rel_start = pit[2]

            events.append({
                'type': "Pits",
                'time': rel_start,
                'message': f"Driver {driver_id} pits in {lap_number} after {rel_start:.3f} seconds."
            })

            events.append({
                'type': "Pits",
                'time': rel_start + pit_duration,
                'message': f"Driver {driver_id} exits pit in {lap_number} in {rel_start + pit_duration:.3f} seconds."
            })

    with open('rc_data.json', 'r') as f:
        data = json.load(f)
    for i in range (len(data)):
        category = data[i][0]
        message = data[i][1]
        rel_time = data[i][2]

        events.append({
            'type': category,
            'time': rel_time,
            'message': message
        })

    with open('lb_data.json', 'r') as file:
        data = json.load(file)
    initial_positions = {}
    current_positions = {}

    for event in data:
        driver = event[0]
        if driver not in initial_positions:
            initial_positions[driver] = event[2]
            current_positions[driver] = event[2]
        new_position = event[2]
        old_position = current_positions[driver]
        if new_position != old_position:
            events.append({
                'type': "Overtake",
                'time': event[1],
                'message': f"Driver {driver} overtakes to {new_position} in {event[1]:.3f} seconds."
            })
            current_positions[driver] = new_position

    events.sort(key=lambda event: event['time'])

    with open('events_data.json', 'w') as file:
        json.dump(events, file)
        '''
        event_index = 0
        while event_index < len(events):
            event = events[event_index]

            if race_timer < event['time']:
                race_timer = event['time']

            print(f"Time {event['time']}s: {event['message']}")

            event_index += 1

            time.sleep(0.1)
        '''
track()
