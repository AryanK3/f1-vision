import json
import time
import re

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
                'time': lap_duration,
                'message': f"Driver {driver_id} completed lap {lap_number}"
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

    for i in range(1, len(data)):
        event = data[i]
        prev_event = data[i - 1]
        
        driver_1 = prev_event[0]
        driver_2 = event[0]
        pos_1 = prev_event[2]
        pos_2 = event[2]

        if (pos_1 != pos_2 and driver_1 != driver_2 and event[1] > 0 and prev_event[1] > 0):  
            if (prev_event[2] < event[2]):  
                overtaken_driver = driver_2
                overtaking_driver = driver_1
                events.append({
                    'type': "Overtake",
                    'time': event[1],
                    'message': f"Driver {overtaking_driver} overtakes Driver {overtaken_driver} to position {pos_1}"
                })
            elif (prev_event[2] > event[2]):  
                overtaken_driver = driver_1
                overtaking_driver = driver_2
                events.append({
                    'type': "Overtake",
                    'time': event[1],
                    'message': f"Driver {overtaking_driver} overtakes Driver {overtaken_driver} to position {pos_2}"
                })

    with open('radio_data.json', 'r') as infile:
        data = json.load(infile)
    
    for item in data:
        url = item[2] 
        code = re.search(r'([^/]+)(?=\.mp3)', url)
        if (item[1] > 0):
            events.append({
                'type': "Radio",
                'time': item[1],
                'message': f"Driver {item[0]}: {code.group(0)}"
            })

    events.sort(key=lambda event: event['time'])

    with open('tyre_data.json', 'r') as f:
        tyre_data = json.load(f)
    with open('pit_data.json', 'r') as f:
        pit_data = json.load(f)

    for driver_data in pit_data:
        driver_id = driver_data['id']
        pits = driver_data['positions']

        for pit in pits:
            lap_number = pit[0]  
            pit_duration = pit[1]  
            rel_start = pit[2]  

            driver_tyre_info = next(
                (item for item in tyre_data if item['driver_number'] == driver_id and item['lap_end'] == lap_number),
                None
            )

            if driver_tyre_info:
                tyre_type = driver_tyre_info['compound']  

            events.append({
                'type': "Pits",
                'time': rel_start,
                'message': f"Driver {driver_id} (Tyre: {tyre_type}) enters pit in lap {lap_number}"
            })

            next_tyre_info = next(
                (item for item in tyre_data if item['driver_number'] == driver_id and item['lap_start'] > lap_number),
                None
            )

            if next_tyre_info:
                next_tyre_type = next_tyre_info['compound']
            else:
                next_tyre_type = tyre_type 

            events.append({
                'type': "Pits",
                'time': rel_start + pit_duration,
                'message': f"Driver {driver_id} (Tyre: {next_tyre_type}) exits pit in lap {lap_number}"
            })


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
