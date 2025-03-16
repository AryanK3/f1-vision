import json

with open('V1/lap_data.json', 'r') as file:
    lap_data = json.load(file)

events = []

for lap in lap_data:
    driver = lap['id']
    for pos in lap['positions']:
        lap = pos[0]
        sector1_time = pos[1]
        sector2_time = pos[2]
        sector3_time = pos[3]
        total_lap_time = pos[4]
        rel_time_at_lap_start = pos[5]

        events.append({
            "type": "lap_start",
            "id": driver,
            "lap": lap,
            "rel_time": rel_time_at_lap_start,
        })
        events.append({
            "type": "sector",
            "id": driver,
            "lap": lap,
            "sector": 1,
            "sector_time": sector1_time,
            "rel_time": round(rel_time_at_lap_start + sector1_time, 3)
        })
        events.append({
            "type": "sector",
            "id": driver,
            "lap": lap,
            "sector": 2,
            "sector_time": sector2_time,
            "rel_time": round(rel_time_at_lap_start + sector1_time + sector2_time, 3)
        })
        events.append({
            "type": "sector",
            "id": driver,
            "lap": lap,
            "sector": 3,
            "sector_time": sector3_time,
            "rel_time": round(rel_time_at_lap_start + sector1_time + sector2_time + sector3_time, 3)
        })
        events.append({
            "type": "lap_end",
            "id": driver,
            "lap": lap,
            "lap_time": total_lap_time,
            "rel_time": round(rel_time_at_lap_start + sector1_time + sector2_time + sector3_time, 3)
        })

events.sort(key=lambda x: x['rel_time'])

with open("new_lap_data.json", "w") as f:
    json.dump(events, f)