import json

with open('lb_data.json', 'r') as file:
    data = json.load(file)

events = []

# Loop through events and check for position changes
for i in range(1, len(data)):
    event = data[i]
    prev_event = data[i - 1]
    
    driver_1 = prev_event[0]
    driver_2 = event[0]
    pos_1 = prev_event[2]
    pos_2 = event[2]

    if (pos_1 != pos_2 and event[1] > 0 and prev_event[1] > 0):  
        if (pos_1 > pos_2 and prev_event[2] < event[2]):  
            overtaken_driver = driver_2
            overtaking_driver = driver_1
            events.append({
                'type': "Overtake",
                'time': event[1],
                'message': f"Driver {overtaking_driver} overtakes Driver {overtaken_driver} to position {pos_2} in {event[1]:.3f} seconds."
            })
        elif (pos_2 > pos_1 and prev_event[2] < event[2]):  
            overtaken_driver = driver_1
            overtaking_driver = driver_2
            events.append({
                'type': "Overtake",
                'time': event[1],
                'message': f"Driver {overtaken_driver} overtakes Driver {overtaking_driver} to position {pos_1} in {event[1]:.3f} seconds."
            })
 
for event in events:
    print(event['message'])
