from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
import math
import time

app = Flask(__name__)

# Driver data and mapping to display names
DRIVER_MAPPING = {
    1: {"code": "LEC", "name": "Charles Leclerc", "team": "Ferrari", "color": "#A6051A"},
    2: {"code": "SAI", "name": "Carlos Sainz", "team": "Ferrari", "color": "#A6051A"},
    3: {"code": "VER", "name": "Max Verstappen", "team": "Red Bull Racing", "color": "#3671C6"},
    4: {"code": "PER", "name": "Sergio Perez", "team": "Red Bull Racing", "color": "#3671C6"},
    5: {"code": "HAM", "name": "Lewis Hamilton", "team": "Mercedes", "color": "#27F4D2"},
    6: {"code": "RUS", "name": "George Russell", "team": "Mercedes", "color": "#27F4D2"},
    7: {"code": "GAS", "name": "Pierre Gasly", "team": "Alpine", "color": "#FF87BC"},
    8: {"code": "OCO", "name": "Esteban Ocon", "team": "Alpine", "color": "#FF87BC"},
    9: {"code": "BOT", "name": "Valtteri Bottas", "team": "Kick Sauber", "color": "#52E252"},
    10: {"code": "ZHO", "name": "Zhou Guanyu", "team": "Kick Sauber", "color": "#52E252"},
    11: {"code": "NOR", "name": "Lando Norris", "team": "McLaren", "color": "#FF8000"},
    16: {"code": "PIA", "name": "Oscar Piastri", "team": "McLaren", "color": "#FF8000"},
    18: {"code": "STR", "name": "Lance Stroll", "team": "Aston Martin", "color": "#006F62"},
    14: {"code": "ALO", "name": "Fernando Alonso", "team": "Aston Martin", "color": "#006F62"},
    20: {"code": "MAG", "name": "Kevin Magnussen", "team": "Haas F1 Team", "color": "#B6BABD"},
    27: {"code": "HUL", "name": "Nico Hulkenberg", "team": "Haas F1 Team", "color": "#B6BABD"},
    22: {"code": "TSU", "name": "Yuki Tsunoda", "team": "RB", "color": "#6692FF"},
    23: {"code": "ALB", "name": "Alexander Albon", "team": "Williams", "color": "#64C4FF"},
    24: {"code": "SAR", "name": "Logan Sargeant", "team": "Williams", "color": "#64C4FF"},
    77: {"code": "BOT", "name": "Valtteri Bottas", "team": "Alfa Romeo", "color": "#900000"},
    81: {"code": "LAW", "name": "Liam Lawson", "team": "RB", "color": "#6692FF"},
    31: {"code": "OCO", "name": "Esteban Ocon", "team": "Alpine", "color": "#0090FF"},
    63: {"code": "RUS", "name": "George Russell", "team": "Mercedes", "color": "#00D2BE"},
    55: {"code": "SAI", "name": "Carlos Sainz", "team": "Ferrari", "color": "#DC0000"},
    44: {"code": "HAM", "name": "Lewis Hamilton", "team": "Mercedes", "color": "#00D2BE"}
}

# Tire compounds
TIRE_COMPOUNDS = {
    "SOFT": {"color": "red", "letter": "S"},
    "MEDIUM": {"color": "yellow", "letter": "M"},
    "HARD": {"color": "white", "letter": "H"},
    "INTERMEDIATE": {"color": "green", "letter": "I"},
    "WET": {"color": "blue", "letter": "W"}
}

# Track previous positions to detect overtakes
previous_positions = {}


def load_data_files():
    """Load all data files and return as dict"""
    data = {}
    file_paths = {
        'driver_data': 'data/driver_data.json',
        'lap_data': 'data/lap_data.json',
        'car_data': 'data/car_data.json',
        'event_data': 'data/event_data.json'
    }

    for key, path in file_paths.items():
        try:
            with open(path, 'r') as f:
                data[key] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {path}: {e}")
            data[key] = []

    return data


def process_position_data(driver_data):
    """Process position data for track visualization"""
    global previous_positions

    # Extract the track boundaries by finding the min/max coordinates
    all_positions = []
    for driver in driver_data:
        positions = driver.get("positions", [])
        all_positions.extend(positions)

    # If no positions, return empty data
    if not all_positions:
        return {
            "min_x": 0, "max_x": 1000,
            "min_y": 0, "max_y": 600,
            "drivers": {},
            "overtakes": []
        }

    # Find track boundaries
    min_x = min(pos[0] for pos in all_positions if isinstance(pos[0], (int, float)))
    max_x = max(pos[0] for pos in all_positions if isinstance(pos[0], (int, float)))
    min_y = min(pos[1] for pos in all_positions if isinstance(pos[1], (int, float)))
    max_y = max(pos[1] for pos in all_positions if isinstance(pos[1], (int, float)))

    # Create a dictionary for each driver with their most recent position
    drivers = {}
    for driver in driver_data:
        driver_id = driver.get("id")
        positions = driver.get("positions", [])

        if positions and len(positions[0]) >= 4:
            # Get the most recent position (based on timestamp)
            most_recent = max(positions,
                              key=lambda pos: pos[3] if len(pos) > 3 and isinstance(pos[3], (int, float)) else 0)

            drivers[driver_id] = {
                "x": most_recent[0],
                "y": most_recent[1],
                "time": most_recent[3],
                "info": DRIVER_MAPPING.get(driver_id, {"code": f"D{driver_id}", "color": "#777777"})
            }

    # Detect overtakes (position changes)
    overtakes = []

    # Get current positions from timing data
    current_positions = process_timing_data(load_data_files().get('lap_data', []),
                                            load_data_files().get('car_data', []))

    # Initialize previous positions if first time
    if not previous_positions:
        previous_positions = {
            int(driver_id): {"position": data["position"]}
            for driver_id, data in current_positions.items()
        }
    else:
        # Find position changes
        for driver_id, data in current_positions.items():
            driver_id = int(driver_id)
            if driver_id in previous_positions:
                prev_pos = previous_positions[driver_id]["position"]
                curr_pos = data["position"]

                # If position improved (smaller number is better)
                if curr_pos < prev_pos:
                    # Find who was overtaken
                    for other_id, other_data in previous_positions.items():
                        if other_data["position"] == curr_pos:
                            overtakes.append({
                                "overtaking": driver_id,
                                "overtaken": other_id,
                                "position": curr_pos
                            })
                            break

        # Update previous positions for next time
        previous_positions = {
            int(driver_id): {"position": data["position"]}
            for driver_id, data in current_positions.items()
        }

    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "drivers": drivers,
        "overtakes": overtakes
    }


def process_timing_data(lap_data, car_data):
    """Process timing data for the leaderboard"""
    # Extract the latest lap times and sector times for each driver
    driver_timing = {}

    # Process lap data
    for driver in lap_data:
        driver_id = driver.get("id")
        laps = driver.get("positions", [])

        if not laps:
            continue

        # Find the most recent completed lap
        latest_lap = max(laps, key=lambda lap: lap[5] if len(lap) > 5 and isinstance(lap[5], (int, float)) else 0)

        if driver_id not in driver_timing:
            driver_timing[driver_id] = {
                "info": DRIVER_MAPPING.get(driver_id, {"code": f"D{driver_id}", "color": "#777777"}),
                "position": 0,
                "lap_time": latest_lap[4] if len(latest_lap) > 4 else 0,
                "sector1": latest_lap[1] if len(latest_lap) > 1 else 0,
                "sector2": latest_lap[2] if len(latest_lap) > 2 else 0,
                "sector3": latest_lap[3] if len(latest_lap) > 3 else 0,
                "drs": "OFF",
                "tire": "M",
                "gap": "+0.000"
            }

    # Process car data for DRS status
    for driver in car_data:
        driver_id = driver.get("id")
        telemetry = driver.get("positions", [])

        if not telemetry or driver_id not in driver_timing:
            continue

        # Find most recent telemetry
        latest_telemetry = max(telemetry,
                               key=lambda tel: tel[0] if len(tel) > 0 and isinstance(tel[0], (int, float)) else 0)

        # Update DRS status (index 5 contains DRS data)
        if len(latest_telemetry) > 5:
            drs_value = latest_telemetry[5]
            driver_timing[driver_id]["drs"] = "DRS" if drs_value and drs_value > 0 else "OFF"

    # Sort by lap time and assign positions
    sorted_drivers = sorted(driver_timing.items(),
                            key=lambda x: x[1]["lap_time"] if x[1]["lap_time"] > 0 else float('inf'))

    for position, (driver_id, data) in enumerate(sorted_drivers, 1):
        data["position"] = position

        # Calculate gap to leader
        if position == 1:
            data["gap"] = ""
        else:
            leader_time = sorted_drivers[0][1]["lap_time"]
            if data["lap_time"] > 0 and leader_time > 0:
                gap = data["lap_time"] - leader_time
                data["gap"] = f"+{gap:.3f}" if gap > 0 else "0.000"

    return driver_timing


@app.route('/')
def index():
    """Render the main dashboard template"""
    return render_template('index.html', race_name="Gulf Air Bahrain Grand Prix")


@app.route('/api/data')
def get_data():
    """API endpoint to get all processed data"""
    # Load data files
    data = load_data_files()

    # Process position data for track map
    track_data = process_position_data(data.get('driver_data', []))

    # Process timing data for leaderboard
    timing_data = process_timing_data(data.get('lap_data', []), data.get('car_data', []))

    # Sample event data (most recent events)
    events = data.get('event_data', [])
    recent_events = sorted(events, key=lambda e: e.get('time', 0), reverse=True)[:10]

    return jsonify({
        'track': track_data,
        'timing': timing_data,
        'events': recent_events
    })


@app.route('/api/position')
def get_position_data():
    """API endpoint to get just position data for track map updates"""
    data = load_data_files()
    track_data = process_position_data(data.get('driver_data', []))
    return jsonify(track_data)


@app.route('/api/timing')
def get_timing_data():
    """API endpoint to get just timing data for leaderboard updates"""
    data = load_data_files()
    timing_data = process_timing_data(data.get('lap_data', []), data.get('car_data', []))
    return jsonify(timing_data)


@app.route('/setup')
def setup():
    """Create sample data if no data files exist"""
    from pathlib import Path
    import random

    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)

    # Check if data files exist
    if not Path("data/driver_data.json").exists():
        # Create sample driver data
        driver_data = []
        for driver_id in list(DRIVER_MAPPING.keys())[:20]:  # Limit to 20 drivers
            positions = []
            # Create positions that follow the Bahrain track shape
            # Using a parametric approach to create points along an oval-like shape
            for i in range(50):
                t = i / 50 * 2 * math.pi
                # Adjust these formulas to match the Bahrain track shape
                x = 500 + 250 * math.cos(t) * (1 + 0.2 * math.cos(3 * t))
                y = 300 + 200 * math.sin(t) * (1 + 0.1 * math.sin(2 * t))

                # Add a small offset for each driver to spread them out
                x += driver_id * 2 * math.cos(t)
                y += driver_id * 2 * math.sin(t)

                positions.append([x, y, 0, time.time() - 50 + i])

            driver_data.append({"id": driver_id, "positions": positions})

        # Save to file
        with open("data/driver_data.json", "w") as f:
            json.dump(driver_data, f)

    # Create sample lap data if it doesn't exist
    if not Path("data/lap_data.json").exists():
        lap_data = []
        for driver_id in list(DRIVER_MAPPING.keys())[:20]:  # Limit to 20 drivers
            positions = []
            # Randomize base lap time by driver skill (lower driver ID = faster)
            skill_factor = max(0.8, min(1.2, 1 + (driver_id - 10) / 40))
            base_lap_time = 90 * skill_factor  # Base lap time around 90 seconds

            for i in range(10):
                # Add some randomness to each lap
                lap_variation = random.uniform(0.98, 1.02)

                # Create sector times that sum to the total lap time
                sector1 = base_lap_time * 0.3 * random.uniform(0.98, 1.02)
                sector2 = base_lap_time * 0.4 * random.uniform(0.98, 1.02)
                sector3 = base_lap_time * 0.3 * random.uniform(0.98, 1.02)

                # Adjust to make sure they sum to close to the target lap time
                total = sector1 + sector2 + sector3
                lap_time = total

                positions.append([
                    i + 1,  # Lap number
                    sector1,  # Sector 1 time
                    sector2,  # Sector 2 time
                    sector3,  # Sector 3 time
                    lap_time,  # Total lap time
                    time.time() - (10 - i) * 120  # Timestamp (more recent laps have newer timestamps)
                ])

            lap_data.append({"id": driver_id, "positions": positions})

        # Save to file
        with open("data/lap_data.json", "w") as f:
            json.dump(lap_data, f)

    # Create sample car data if it doesn't exist
    if not Path("data/car_data.json").exists():
        car_data = []
        for driver_id in list(DRIVER_MAPPING.keys())[:20]:  # Limit to 20 drivers
            positions = []
            # Create random car telemetry
            for i in range(50):
                # More randomness for telemetry
                speed = 250 + random.uniform(-30, 30)
                throttle = random.uniform(0.7, 1.0)
                brake = random.uniform(0, 0.3)
                gear = random.randint(6, 8)

                # DRS more likely in straights (approximated by position in sequence)
                drs_probability = 0.3 + 0.4 * math.sin(i / 50 * 2 * math.pi) ** 2
                drs = 1 if random.random() < drs_probability else 0

                positions.append([
                    time.time() - 50 + i,  # Timestamp
                    speed,  # Speed
                    throttle,  # Throttle position
                    brake,  # Brake position
                    gear,  # Gear
                    drs  # DRS status
                ])

            car_data.append({"id": driver_id, "positions": positions})

        # Save to file
        with open("data/car_data.json", "w") as f:
            json.dump(car_data, f)

    # Create sample event data if it doesn't exist
    if not Path("data/event_data.json").exists():
        event_data = [
            {"type": "Race", "time": time.time() - 600, "message": "Race started"},
            {"type": "Pit", "time": time.time() - 500, "message": "VER pits for Medium tires"},
            {"type": "DRS", "time": time.time() - 400, "message": "DRS Enabled"},
            {"type": "Flag", "time": time.time() - 300, "message": "Yellow flag in sector 2"},
            {"type": "Incident", "time": time.time() - 200, "message": "Incident involving HAM noted by stewards"},
            {"type": "Overtake", "time": time.time() - 100, "message": "VER overtakes HAM for P1"}
        ]

        # Save to file
        with open("data/event_data.json", "w") as f:
            json.dump(event_data, f)

    return "Sample data created. <a href='/'>Go to dashboard</a>"


@app.route('/generate_data')
def generate_data():
    """Generate new data for simulation (for testing)"""
    import random
    from pathlib import Path

    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)

    # Get existing data
    data = load_data_files()

    # Update driver positions (simulate movement)
    if 'driver_data' in data:
        for driver in data['driver_data']:
            positions = driver.get('positions', [])
            if positions:
                # Get the latest position
                latest = positions[-1]

                # Calculate driver's current position on a parametric curve
                driver_id = driver.get('id')
                t = (time.time() % 60) / 60 * 2 * math.pi  # Complete a lap every 60 seconds

                # Add a phase offset for each driver to space them apart
                phase_offset = (driver_id % 20) * (2 * math.pi / 20)
                t = (t + phase_offset) % (2 * math.pi)

                # Create a formula for the Bahrain track shape
                x = 500 + 250 * math.cos(t) * (1 + 0.2 * math.cos(3 * t))
                y = 300 + 200 * math.sin(t) * (1 + 0.1 * math.sin(2 * t))

                # Add a small random offset for realism
                x += random.uniform(-5, 5)
                y += random.uniform(-5, 5)

                # Add new position
                positions.append([x, y, 0, time.time()])

                # Keep only the last 50 positions to avoid file growth
                if len(positions) > 50:
                    positions = positions[-50:]

                driver['positions'] = positions

        # Save updated driver data
        with open('data/driver_data.json', 'w') as f:
            json.dump(data['driver_data'], f)

    # Update car data (simulate telemetry changes)
    if 'car_data' in data:
        for driver in data['car_data']:
            telemetry = driver.get('positions', [])
            if telemetry:
                # Get the latest telemetry
                latest = telemetry[-1]

                # Generate new telemetry
                speed = latest[1] + random.uniform(-10, 10)
                speed = max(200, min(350, speed))  # Keep between 200-350

                throttle = max(0, min(1, latest[2] + random.uniform(-0.1, 0.1)))
                brake = max(0, min(1, latest[3] + random.uniform(-0.1, 0.1)))
                gear = max(1, min(8, latest[4] + random.randint(-1, 1)))

                # Randomly toggle DRS (more likely to be on if it was already on)
                drs_probability = 0.9 if latest[5] > 0 else 0.2
                drs = 1 if random.random() < drs_probability else 0

                # Add new telemetry
                telemetry.append([time.time(), speed, throttle, brake, gear, drs])

                # Keep only the last 50 entries
                if len(telemetry) > 50:
                    telemetry = telemetry[-50:]

                driver['positions'] = telemetry

        # Save updated car data
        with open('data/car_data.json', 'w') as f:
            json.dump(data['car_data'], f)

    # Randomly generate an overtake event
    if random.random() > 0.8:  # 20% chance each update
        # Get only driver IDs that are in the data
        available_drivers = [driver.get('id') for driver in data.get('driver_data', [])]
        if len(available_drivers) >= 2:
            overtaker = random.choice(available_drivers)
            overtaken = random.choice([d for d in available_drivers if d != overtaker])

            overtaker_code = DRIVER_MAPPING.get(overtaker, {}).get('code', f'Driver {overtaker}')
            overtaken_code = DRIVER_MAPPING.get(overtaken, {}).get('code', f'Driver {overtaken}')

            event = {
                "type": "Overtake",
                "time": time.time(),
                "message": f"{overtaker_code} overtakes {overtaken_code} for P{random.randint(1, len(available_drivers))}"
            }

            # Add to event data
            if 'event_data' in data:
                data['event_data'].append(event)

                # Keep only the last 20 events
                if len(data['event_data']) > 20:
                    data['event_data'] = data['event_data'][-20:]

                # Save updated event data
                with open('data/event_data.json', 'w') as f:
                    json.dump(data['event_data'], f)

    return "Data updated. <a href='/'>View dashboard</a> or <a href='/generate_data'>Generate more data</a>"


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    app.run(debug=True)