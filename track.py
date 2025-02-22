import json
import time

with open('lap_data.json', 'r') as f:
    data = json.load(f)

def track_lap_and_sector(data):
    race_timer = 0.0
    
    events = []

    for driver_id, laps in data.items():
        for lap in laps:
            if 'rel_start' in lap:  
                events.append({
                    'time': lap['rel_start'],
                    'message': f"Driver {driver_id} started sector 1 of lap {lap['lap_number']} at {lap['rel_start']} seconds."
                })
            
            for sector_num in range(1, 3):
                sector_key = f'duration_sector_{sector_num}'
                if lap.get(sector_key) is not None and 'rel_start' in lap:
                    sector_end_time = lap['rel_start'] + lap[sector_key]
                    events.append({
                        'time': sector_end_time,
                        'message': f"Driver {driver_id} started sector {sector_num + 1} of lap {lap['lap_number']} at {sector_end_time} seconds."
                    })

    events.sort(key=lambda event: event['time'])
    
    event_index = 0
    while event_index < len(events):
        event = events[event_index]
        
        if race_timer < event['time']:
            race_timer = event['time']  
        
        print(f"Time {race_timer:.3f}s: {event['message']}")
        
        event_index += 1
        
        time.sleep(0.1)

track_lap_and_sector(data)
