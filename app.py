from flask import Flask, render_template_string, jsonify, send_from_directory
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


def load_data_files():
    """Load all data files and return as dict"""
    data = {}
    file_paths = {
        'driver_data': 'driver_data.json',
        'lap_data': 'lap_data.json',
        'car_data': 'car_data.json',
        'event_data': 'event_data.json'
    }

    for key, path in file_paths.items():
        try:
            with open(path, 'r') as f:
                data[key] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {path}: {e}")
            data[key] = []

    return data


# Track previous positions to detect overtakes
previous_positions = {}


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
            "min_y": 0, "max_y": 1000,
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

    # If first time, initialize previous positions
    if not previous_positions:
        previous_positions = {
            driver_id: {"position": idx + 1}
            for idx, driver_id in enumerate(drivers.keys())
        }

    # Get current positions from timing data
    current_positions = process_timing_data(load_data_files().get('lap_data', []),
                                            load_data_files().get('car_data', []))

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


# HTML template with embedded CSS and JS
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ race_name }} - Live Timing</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        /* Main styles for F1 Dashboard */
        :root {
            /* Color scheme */
            --bg-dark: #0c0c14;
            --bg-medium: #161623;
            --bg-light: #1e1e2f;
            --text-primary: #ffffff;
            --text-secondary: #b0b0c0;
            --text-muted: #6c6c7c;
            --border-color: #33333f;
            --red: #ff0000;
            --yellow: #ffd700;
            --green: #00ff00;
            --purple: #800080;
            --white: #ffffff;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Roboto', 'Arial', sans-serif;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-primary);
            font-size: 14px;
        }

        .dashboard {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 1800px;
            margin: 0 auto;
            padding: 10px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            background-color: var(--bg-medium);
            border-radius: 5px;
            margin-bottom: 10px;
        }

        .race-title {
            display: flex;
            align-items: center;
        }

        .flag-icon {
            height: 20px;
            margin-right: 10px;
        }

        .race-timer {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }

        #race-time {
            font-size: 24px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        }

        .race-info {
            display: flex;
            gap: 15px;
            margin-top: 5px;
            color: var(--text-secondary);
        }

        .content-area {
            display: flex;
            flex: 1;
            gap: 10px;
            overflow: hidden;
        }

        /* Timing Board Styles */
        .timing-board {
            flex: 1;
            overflow-y: auto;
            background-color: var(--bg-medium);
            border-radius: 5px;
            display: flex;
            flex-direction: column;
        }

        .timing-header {
            display: flex;
            background-color: var(--bg-light);
            padding: 8px 5px;
            border-bottom: 1px solid var(--border-color);
            font-weight: bold;
            position: sticky;
            top: 0;
        }

        .pos-header { width: 40px; text-align: center; }
        .driver-header { flex: 1; }
        .drs-header { width: 60px; text-align: center; }
        .tire-header { width: 60px; text-align: center; }
        .gap-header { width: 90px; text-align: right; }
        .times-header { width: 120px; text-align: center; }
        .sections-header { 
            display: flex;
            width: 240px;
            text-align: center;
        }
        .sections-header div {
            flex: 1;
            text-align: center;
        }

        .timing-rows {
            flex: 1;
            overflow-y: auto;
        }

        .timing-row {
            display: flex;
            padding: 8px 5px;
            border-bottom: 1px solid var(--border-color);
            align-items: center;
            transition: all 0.5s ease;
        }

        .timing-row:hover {
            background-color: var(--bg-light);
        }

        .position {
            width: 40px;
            text-align: center;
            font-weight: bold;
        }

        .driver {
            flex: 1;
            display: flex;
            align-items: center;
        }

        .driver-code {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            margin-right: 10px;
            font-weight: bold;
            color: #000;
            text-align: center;
            width: 50px;
        }

        .drs-status {
            width: 60px;
            text-align: center;
            font-weight: bold;
        }

        .drs-on { color: var(--green); }
        .drs-off { color: var(--text-muted); }

        .tire-type {
            width: 60px;
            text-align: center;
        }

        .tire-indicator {
            display: inline-block;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            text-align: center;
            line-height: 25px;
            font-weight: bold;
            color: #000;
        }

        .soft { background-color: var(--red); }
        .medium { background-color: var(--yellow); }
        .hard { background-color: var(--white); }
        .intermediate { background-color: var(--green); }
        .wet { background-color: blue; }

        .gap {
            width: 90px;
            text-align: right;
            font-family: 'Consolas', monospace;
        }

        .lap-time {
            width: 120px;
            text-align: center;
            font-family: 'Consolas', monospace;
        }

        .sectors {
            display: flex;
            width: 240px;
        }

        .sector {
            flex: 1;
            text-align: center;
            font-family: 'Consolas', monospace;
            padding: 0 5px;
        }

        .fastest-overall { color: var(--purple); }
        .fastest-sector { color: var(--green); }
        .personal-best { color: var(--yellow); }

        /* Track Map Styles */
        .track-map-container {
            width: 400px;
            display: flex;
            flex-direction: column;
            background-color: var(--bg-medium);
            border-radius: 5px;
            padding: 10px;
        }

        .track-map-container h2 {
            margin-bottom: 10px;
            text-align: center;
        }

        #track-map {
            position: relative;
            height: 300px;
            margin-bottom: 20px;
            background-color: var(--bg-light);
            border-radius: 5px;
            overflow: hidden;
        }

        .event-feed {
            flex: 1;
            overflow-y: auto;
            background-color: var(--bg-light);
            border-radius: 5px;
            padding: 10px;
        }

        .event-feed h3 {
            margin-bottom: 10px;
            text-align: center;
        }

        #event-list {
            list-style: none;
            max-height: 300px;
            overflow-y: auto;
        }

        #event-list li {
            padding: 8px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
        }

        #event-list .event-time {
            font-family: 'Consolas', monospace;
            color: var(--text-secondary);
            margin-right: 10px;
        }

        #event-list .event-message {
            flex: 1;
        }

        /* SVG Track Map */
        .track-path {
            fill: none;
            stroke: var(--text-muted);
            stroke-width: 2;
        }

        .driver-marker {
            cursor: pointer;
            transition: transform 0.5s ease;
        }

        .driver-code-label {
            font-size: 10px;
            font-weight: bold;
            text-anchor: middle;
            dominant-baseline: central;
            pointer-events: none;
        }

        /* Car animation */
        @keyframes pulse {
            0% { opacity: 0.7; }
            50% { opacity: 1; }
            100% { opacity: 0.7; }
        }

        .driver-marker circle {
            animation: pulse 2s infinite;
        }

        /* Overtake flash animation */
        @keyframes overtake-flash {
            0% { background-color: var(--bg-medium); }
            25% { background-color: #2a2a40; }
            50% { background-color: var(--bg-medium); }
            75% { background-color: #2a2a40; }
            100% { background-color: var(--bg-medium); }
        }

        .overtaking {
            animation: overtake-flash 1s ease;
        }

        /* Position animations */
        .position-up {
            background-color: rgba(0, 255, 0, 0.2);
            transition: background-color 3s ease;
        }

        .position-down {
            background-color: rgba(255, 0, 0, 0.2);
            transition: background-color 3s ease;
        }

        /* Driver swap animation */
        .driver-swap {
            animation: swap 0.5s ease-in-out;
        }

        @keyframes swap {
            0% { transform: translateY(0); }
            50% { transform: translateY(20px); }
            100% { transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <header>
            <div class="race-title">
                <img src="/static/img/Flag-Bahrain.jpg" alt="Flag" class="flag-icon">
                <h1>{{ race_name }}</h1>
            </div>
            <div class="race-timer">
                <span id="race-time">00:00:00.000</span>
                <div class="race-info">
                    <span class="lap-info">100%</span>
                    <span class="weather-info">
                        <img src="/static/img/Wind.png" alt="Weather" class="weather-icon">
                        1.2m/s
                    </span>
                    <span class="temp-info">
                        <img src="/static/img/Air.png" alt="Air Temp" class="temp-icon">
                        28°C
                    </span>
                    <span class="track-info">
                        <img src="/static/img/TRC.png" alt="Track Temp" class="track-icon">
                        42°C
                    </span>
                </div>
            </div>
        </header>

        <div class="content-area">
            <div class="timing-board">
                <div class="timing-header">
                    <div class="pos-header">P</div>
                    <div class="driver-header">Driver</div>
                    <div class="drs-header">DRS</div>
                    <div class="tire-header">Tires</div>
                    <div class="gap-header">Gap</div>
                    <div class="times-header">Times</div>
                    <div class="sections-header">
                        <div>1</div>
                        <div>2</div>
                        <div>3</div>
                    </div>
                </div>

                <div id="driver-rows" class="timing-rows">
                    <!-- Rows will be populated by JavaScript -->
                </div>
            </div>

            <div class="track-map-container">
                <h2>Track Position</h2>
                <div id="track-map">
                    <!-- SVG will be inserted here by JavaScript -->
                </div>
                <div class="event-feed">
                    <h3>Event Feed</h3>
                    <ul id="event-list">
                        <!-- Events will be populated by JavaScript -->
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Main JavaScript for F1 Dashboard
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize
            initDashboard();

            // Update every 1 second
            setInterval(updateDashboard, 1000);
        });

        // Global storage for data
        let dashboardData = {
            track: null,
            timing: null,
            events: []
        };

        // Store previous positions to animate changes
        let previousPositions = {};

        // Race timer
        let raceStartTime = new Date();
        let raceTimer = document.getElementById('race-time');

        // Initialize the dashboard
        function initDashboard() {
            // Initialize SVG for track map
            const trackMap = d3.select('#track-map')
                .append('svg')
                .attr('width', '100%')
                .attr('height', '100%')
                .attr('viewBox', '0 0 1000 800')
                .attr('preserveAspectRatio', 'xMidYMid meet');

            // Add group for track path
            trackMap.append('g')
                .attr('class', 'track-group');

            // Add group for driver markers
            trackMap.append('g')
                .attr('class', 'drivers-group');

            // Initial data load
            fetchAllData();

            // Start the race timer
            updateRaceTimer();
            setInterval(updateRaceTimer, 100);
        }

        // Update race timer
        function updateRaceTimer() {
            const now = new Date();
            const elapsed = now - raceStartTime;

            // Format as 00:00:00.000
            let hours = Math.floor(elapsed / 3600000).toString().padStart(2, '0');
            let minutes = Math.floor((elapsed % 3600000) / 60000).toString().padStart(2, '0');
            let seconds = Math.floor((elapsed % 60000) / 1000).toString().padStart(2, '0');
            let milliseconds = Math.floor(elapsed % 1000).toString().padStart(3, '0');

            raceTimer.textContent = `${hours}:${minutes}:${seconds}.${milliseconds}`;
        }

        // Fetch all dashboard data
        function fetchAllData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    dashboardData = data;
                    renderDashboard();
                })
                .catch(error => console.error('Error fetching data:', error));
        }

        // Update dashboard with latest data
        function updateDashboard() {
            // Update position data
            fetch('/api/position')
                .then(response => response.json())
                .then(data => {
                    dashboardData.track = data;
                    updateTrackMap();

                    // Process overtakes
                    processOvertakes(data.overtakes);
                })
                .catch(error => console.error('Error fetching position data:', error));

            // Update timing data
            fetch('/api/timing')
                .then(response => response.json())
                .then(data => {
                    // Store previous positions for animation
                    previousPositions = {};
                    const rows = document.querySelectorAll('.timing-row');
                    rows.forEach(row => {
                        const id = row.id.replace('driver-row-', '');
                        const pos = row.querySelector('.position').textContent;
                        previousPositions[id] = parseInt(pos);
                    });

                    dashboardData.timing = data;
                    updateTimingBoard();
                })
                .catch(error => console.error('Error fetching timing data:', error));
        }

        // Process overtakes and animate them
        function processOvertakes(overtakes) {
            if (!overtakes || overtakes.length === 0) return;

            // Process each overtake
            overtakes.forEach(overtake => {
                // Get the row elements
                const overtakingRow = document.getElementById(`driver-row-${overtake.overtaking}`);
                const overtakenRow = document.getElementById(`driver-row-${overtake.overtaken}`);

                if (overtakingRow && overtakenRow) {
                    // Add classes for animation
                    overtakingRow.classList.add('position-up');
                    overtakenRow.classList.add('position-down');
                    overtakingRow.classList.add('driver-swap');
                    overtakenRow.classList.add('driver-swap');

                    // Add overtaking flash
                    overtakingRow.classList.add('overtaking');

                    // Remove classes after animation completes
                    setTimeout(() => {
                        overtakingRow.classList.remove('position-up', 'driver-swap', 'overtaking');
                        overtakenRow.classList.remove('position-down', 'driver-swap');
                    }, 3000);

                    // Add to event feed
                    const overtakingDriver = dashboardData.timing[overtake.overtaking]?.info?.code || `Driver ${overtake.overtaking}`;
                    const overtakenDriver = dashboardData.timing[overtake.overtaken]?.info?.code || `Driver ${overtake.overtaken}`;

                    addEventToFeed({
                        type: 'Overtake',
                        time: Date.now() / 1000,
                        message: `${overtakingDriver} overtakes ${overtakenDriver} for P${overtake.position}`
                    });
                }
            });
        }

        // Add an event to the feed
        function addEventToFeed(event) {
            const eventList = document.getElementById('event-list');

            const li = document.createElement('li');

            const timeSpan = document.createElement('span');
            timeSpan.className = 'event-time';
            timeSpan.textContent = formatEventTime(event.time);

            const messageSpan = document.createElement('span');
            messageSpan.className = 'event-message';
            messageSpan.textContent = event.message;

            // Add class for event type
            li.classList.add(`event-${event.type.toLowerCase()}`);

            li.appendChild(timeSpan);
            li.appendChild(messageSpan);

            // Add to the top of the list
            if (eventList.firstChild) {
                eventList.insertBefore(li, eventList.firstChild);
            } else {
                eventList.appendChild(li);
            }

            // Limit to 10 events
            while (eventList.children.length > 10) {
                eventList.removeChild(eventList.lastChild);
            }
        }

        // Render the entire dashboard
        function renderDashboard() {
            renderTrackMap();
            renderTimingBoard();
            renderEventFeed();
        }

        // Render track map
        function renderTrackMap() {
            if (!dashboardData.track) return;

            const trackData = dashboardData.track;
            const svgContainer = d3.select('#track-map svg');
            const width = 1000;
            const height = 800;
            const padding = 50;

            // Scale functions to map data coordinates to SVG coordinates
            const xScale = d3.scaleLinear()
                .domain([trackData.min_x, trackData.max_x])
                .range([padding, width - padding]);

            const yScale = d3.scaleLinear()
                .domain([trackData.min_y, trackData.max_y])
                .range([padding, height - padding]);

            // Add driver markers
            const driversGroup = svgContainer.select('.drivers-group');

            // Clear existing markers
            driversGroup.selectAll('*').remove();

            // Add driver markers
            Object.keys(trackData.drivers).forEach(driverId => {
                const driver = trackData.drivers[driverId];
                const driverGroup = driversGroup.append('g')
                    .attr('class', 'driver-marker')
                    .attr('id', `driver-${driverId}`)
                    .attr('transform', `translate(${xScale(driver.x)}, ${yScale(driver.y)})`);

                // Add circle for driver
                driverGroup.append('circle')
                    .attr('r', 10)
                    .attr('fill', driver.info.color || '#FFFFFF');

                // Add driver code label
                driverGroup.append('text')
                    .attr('class', 'driver-code-label')
                    .attr('fill', getContrastColor(driver.info.color || '#FFFFFF'))
                    .text(driver.info.code);

                // Add tooltip on hover
                driverGroup.append('title')
                    .text(driver.info.name);
            });
        }

        // Update the track map with new positions
        function updateTrackMap() {
            if (!dashboardData.track) return;

            const trackData = dashboardData.track;
            const svgContainer = d3.select('#track-map svg');
            const width = 1000;
            const height = 800;
            const padding = 50;

            // Scale functions to map data coordinates to SVG coordinates
            const xScale = d3.scaleLinear()
                .domain([trackData.min_x, trackData.max_x])
                .range([padding, width - padding]);

            const yScale = d3.scaleLinear()
                .domain([trackData.min_y, trackData.max_y])
                .range([padding, height - padding]);

            // Update driver positions
            Object.keys(trackData.drivers).forEach(driverId => {
                const driver = trackData.drivers[driverId];
                const driverGroup = d3.select(`#driver-${driverId}`);

                if (!driverGroup.empty()) {
                    driverGroup.transition()
                        .duration(500)
                        .attr('transform', `translate(${xScale(driver.x)}, ${yScale(driver.y)})`);
                }
            });
        }

        // Render timing board
        function renderTimingBoard() {
            if (!dashboardData.timing) return;

            const driverRows = document.getElementById('driver-rows');
            driverRows.innerHTML = '';

            // Sort drivers by position
            const sortedDrivers = Object.entries(dashboardData.timing)
                .sort((a, b) => a[1].position - b[1].position);

            // Create rows for each driver
            sortedDrivers.forEach(([driverId, data]) => {
                const row = document.createElement('div');
                row.className = 'timing-row';
                row.id = `driver-row-${driverId}`;

                // Position
                const position = document.createElement('div');
                position.className = 'position';
                position.textContent = data.position;

                // Driver
                const driver = document.createElement('div');
                driver.className = 'driver';

                const driverCode = document.createElement('div');
                driverCode.className = 'driver-code';
                driverCode.textContent = data.info.code;
                driverCode.style.backgroundColor = data.info.color || '#777777';
                driverCode.style.color = getContrastColor(data.info.color || '#777777');

                driver.appendChild(driverCode);

                // DRS status
                const drs = document.createElement('div');
                drs.className = 'drs-status';
                if (data.drs === 'DRS') {
                    drs.classList.add('drs-on');
                    drs.textContent = 'DRS';
                } else {
                    drs.classList.add('drs-off');
                    drs.textContent = 'OFF';
                }

                // Tire type
                const tire = document.createElement('div');
                tire.className = 'tire-type';

                const tireImg = document.createElement('img');
                tireImg.src = `/static/img/${data.tire}.svg`;
                tireImg.alt = data.tire;
                tireImg.width = 25;
                tireImg.height = 25;

                tire.appendChild(tireImg);

                // Gap
                const gap = document.createElement('div');
                gap.className = 'gap';
                gap.textContent = data.gap;

                // Lap time
                const lapTime = document.createElement('div');
                lapTime.className = 'lap-time';
                lapTime.textContent = formatTime(data.lap_time);

                // Sectors
                const sectors = document.createElement('div');
                sectors.className = 'sectors';

                const sector1 = document.createElement('div');
                sector1.className = 'sector';
                sector1.textContent = formatTime(data.sector1);

                const sector2 = document.createElement('div');
                sector2.className = 'sector';
                sector2.textContent = formatTime(data.sector2);

                const sector3 = document.createElement('div');
                sector3.className = 'sector';
                sector3.textContent = formatTime(data.sector3);

                sectors.appendChild(sector1);
                sectors.appendChild(sector2);
                sectors.appendChild(sector3);

                // Add all elements to the row
                row.appendChild(position);
                row.appendChild(driver);
                row.appendChild(drs);
                row.appendChild(tire);
                row.appendChild(gap);
                row.appendChild(lapTime);
                row.appendChild(sectors);

                // Add the row to the timing board
                driverRows.appendChild(row);
            });
        }

        // Update timing board
        function updateTimingBoard() {
            if (!dashboardData.timing) return;

            // Sort drivers by position
            const sortedDrivers = Object.entries(dashboardData.timing)
                .sort((a, b) => a[1].position - b[1].position);

            // Update or create rows for each driver
            sortedDrivers.forEach(([driverId, data]) => {
                let row = document.getElementById(`driver-row-${driverId}`);

                // If row exists, update it
                if (row) {
                    // Check if position changed
                    const previousPosition = previousPositions[driverId];
                    if (previousPosition && previousPosition !== data.position) {
                        // Position improved (smaller number is better)
                        if (data.position < previousPosition) {
                            row.classList.add('position-up');
                        }
                        // Position worsened
                        else if (data.position > previousPosition) {
                            row.classList.add('position-down');
                        }

                        // Remove classes after animation completes
                        setTimeout(() => {
                            row.classList.remove('position-up', 'position-down');
                        }, 3000);
                    }

                    // Update position
                    row.querySelector('.position').textContent = data.position;

                    // Update DRS status
                    const drs = row.querySelector('.drs-status');
                    drs.textContent = data.drs === 'DRS' ? 'DRS' : 'OFF';
                    drs.className = data.drs === 'DRS' ? 'drs-status drs-on' : 'drs-status drs-off';

                    // Update gap
                    row.querySelector('.gap').textContent = data.gap;

                    // Update lap time
                    row.querySelector('.lap-time').textContent = formatTime(data.lap_time);

                    // Update sectors
                    const sectors = row.querySelectorAll('.sector');
                    sectors[0].textContent = formatTime(data.sector1);
                    sectors[1].textContent = formatTime(data.sector2);
                    sectors[2].textContent = formatTime(data.sector3);

                    // Move row to correct position in list
                    const parent = row.parentNode;
                    const targetIndex = data.position - 1;

                    if (parent.children[targetIndex] !== row) {
                        // Add animation class
                        row.classList.add('driver-swap');

                        // Remove animation class after it completes
                        setTimeout(() => {
                            row.classList.remove('driver-swap');
                        }, 500);

                        // Move row to correct position
                        if (targetIndex < parent.children.length) {
                            parent.insertBefore(row, parent.children[targetIndex]);
                        } else {
                            parent.appendChild(row);
                        }
                    }
                } 
                // Otherwise create a new row
                else {
                    renderTimingBoard();
                }
            });
        }

        // Render event feed
        function renderEventFeed() {
            if (!dashboardData.events || dashboardData.events.length === 0) return;

            const eventList = document.getElementById('event-list');
            eventList.innerHTML = '';

            // Add the most recent events (limited to 10)
            dashboardData.events.slice(0, 10).forEach(event => {
                const li = document.createElement('li');

                const timeSpan = document.createElement('span');
                timeSpan.className = 'event-time';
                timeSpan.textContent = formatEventTime(event.time);

                const messageSpan = document.createElement('span');
                messageSpan.className = 'event-message';
                messageSpan.textContent = event.message;

                // Add class for event type
                li.classList.add(`event-${event.type.toLowerCase()}`);

                li.appendChild(timeSpan);
                li.appendChild(messageSpan);

                eventList.appendChild(li);
            });
        }

        // Helper function to format time in MM:SS.mmm
        function formatTime(timeInSeconds) {
            if (!timeInSeconds || timeInSeconds <= 0) {
                return '00:00.000';
            }

            const minutes = Math.floor(timeInSeconds / 60).toString().padStart(2, '0');
            const seconds = Math.floor(timeInSeconds % 60).toString().padStart(2, '0');
            const milliseconds = Math.floor((timeInSeconds % 1) * 1000).toString().padStart(3, '0');

            return `${minutes}:${seconds}.${milliseconds}`;
        }

        // Helper function to format event time in HH:MM:SS
        function formatEventTime(timeInSeconds) {
            if (!timeInSeconds || timeInSeconds < 0) {
                return '00:00:00';
            }

            const hours = Math.floor(timeInSeconds / 3600).toString().padStart(2, '0');
            const minutes = Math.floor((timeInSeconds % 3600) / 60).toString().padStart(2, '0');
            const seconds = Math.floor(timeInSeconds % 60).toString().padStart(2, '0');

            return `${hours}:${minutes}:${seconds}`;
        }

        // Helper function to determine text color based on background
        function getContrastColor(hexColor) {
            // If no color or invalid format, return white
            if (!hexColor || !hexColor.match(/^#[0-9A-F]{6}$/i)) {
                return '#FFFFFF';
            }

            // Convert hex to RGB
            const r = parseInt(hexColor.slice(1, 3), 16);
            const g = parseInt(hexColor.slice(3, 5), 16);
            const b = parseInt(hexColor.slice(5, 7), 16);

            // Calculate luminance
            const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

            // Return black for light colors, white for dark
            return luminance > 0.5 ? '#000000' : '#FFFFFF';
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, race_name="Gulf Air Bahrain Grand Prix")


@app.route('/static/img/<path:filename>')
def serve_static(filename):
    return send_from_directory('static/img', filename)


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


if __name__ == '__main__':
    app.run(debug=True)