import fastf1
import fastf1.plotting
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib import gridspec
import time

# Enable the plotting functionality from fastf1
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)

# Load a session - change these parameters as needed
year = 2023
gp = 'Monaco'  # Monaco is great for close racing
session_type = 'R'  # 'R' for Race

# Simulation settings
LIVE_MODE = True           # True for live simulation; set to False to save frames instead
OUTPUT_DIR = "race_frames"  # Directory to save frames if LIVE_MODE is False
ZOOM_MODE = "dynamic"        # Options: "full_track", "dynamic", "focus_driver"
FOCUS_DRIVER = "1"           # Driver number to focus on if ZOOM_MODE is "focus_driver"
ZOOM_LEVEL = 400             # Size of zoom window in meters
FIXED_HEIGHT = 800           # Plot height in pixels
FIXED_WIDTH = 1200           # Plot width in pixels
SKIP_FRAMES = 5              # Skip frames to speed up simulation (higher = faster but less smooth)
SHOW_LATERAL = True          # Display lateral distances between cars

print(f"Loading {gp} {year} {session_type} session data...")
session = fastf1.get_session(year, gp, session_type)
session.load(telemetry=True, laps=True, weather=True, messages=True)

print("Processing driver position data...")
# Get position data for all drivers
drivers = session.drivers
position_data = {}
driver_info = {}

for driver in drivers:
    try:
        position_data[driver] = session.pos_data[driver]
        driver_info[driver] = session.get_driver(driver)
    except Exception as e:
        print(f"Could not get position data for driver {driver}: {e}")

# Get circuit info for proper orientation
circuit_info = session.get_circuit_info()
rotation = circuit_info.rotation if circuit_info else 0

# Get track status data
track_status = session.track_status

# If saving frames, create output directory
if not LIVE_MODE and not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


# Function to calculate direction vectors for each car
def calculate_direction(pos_df):
    pos_df = pos_df.copy()
    pos_df['dx'] = pos_df['X'].diff().fillna(0)
    pos_df['dy'] = pos_df['Y'].diff().fillna(0)
    # Smooth the vectors with a rolling window
    window = 5
    pos_df['dx'] = pos_df['dx'].rolling(window=window, center=True).mean().fillna(pos_df['dx'])
    pos_df['dy'] = pos_df['dy'].rolling(window=window, center=True).mean().fillna(pos_df['dy'])
    # Normalize vectors
    magnitude = np.sqrt(pos_df['dx'] ** 2 + pos_df['dy'] ** 2).replace(0, 1)
    pos_df['dx'] /= magnitude
    pos_df['dy'] /= magnitude
    return pos_df

# Process position data to add direction vectors
for driver in position_data:
    if not position_data[driver].empty:
        position_data[driver] = calculate_direction(position_data[driver])

# Function to calculate lateral distance between two cars
def calculate_lateral_distance(x1, y1, dx1, dy1, x2, y2):
    vx, vy = x2 - x1, y2 - y1
    perp_dx, perp_dy = -dy1, dx1
    lateral_dist = abs(vx * perp_dx + vy * perp_dy)
    return lateral_dist

# Determine track boundaries
def determine_track_boundaries():
    all_x, all_y = [], []
    for pos in position_data.values():
        if not pos.empty:
            all_x.extend(pos['X'].values / 10)  # Convert to meters
            all_y.extend(pos['Y'].values / 10)
    if all_x and all_y:
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        padding = 0.1
        x_range, y_range = max(x_max - x_min, 100), max(y_max - y_min, 100)
        if rotation:
            rad = np.radians(rotation)
            corners = np.array([[x_min, y_min],
                                [x_min, y_max],
                                [x_max, y_min],
                                [x_max, y_max]])
            rot_matrix = np.array([[np.cos(rad), -np.sin(rad)],
                                   [np.sin(rad),  np.cos(rad)]])
            rotated = np.dot(corners, rot_matrix.T)
            x_min, x_max = rotated[:, 0].min(), rotated[:, 0].max()
            y_min, y_max = rotated[:, 1].min(), rotated[:, 1].max()
            x_range, y_range = max(x_max - x_min, 100), max(y_max - y_min, 100)
        return x_min - x_range * padding, x_max + x_range * padding, y_min - y_range * padding, y_max + y_range * padding
    return -1000, 1000, -1000, 1000

track_x_min, track_x_max, track_y_min, track_y_max = determine_track_boundaries()
print(f"Track boundaries: X [{track_x_min:.1f}, {track_x_max:.1f}], Y [{track_y_min:.1f}, {track_y_max:.1f}]")

# Prepare position chart data
def prepare_position_data():
    all_laps = session.laps.copy()
    if 'Position' in all_laps.columns:
        position_by_lap = {}
        for driver in drivers:
            driver_laps = all_laps[all_laps['Driver'] == driver]
            if not driver_laps.empty:
                positions = driver_laps[['LapNumber', 'Position']].set_index('LapNumber')['Position']
                position_by_lap[driver] = positions
        return position_by_lap
    else:
        print("No position data available. Position chart will not show accurate data.")
        return {}

position_by_lap = prepare_position_data()

# Get track status at a given time with error checking
def get_track_status_at_time(current_time):
    if track_status.empty:
        return "1"  # Default green flag
    time_col = 'SessionTime' if 'SessionTime' in track_status.columns else 'Time' if 'Time' in track_status.columns else None
    if time_col is None:
        return "1"
    status_before = track_status[track_status[time_col] <= current_time]
    if status_before.empty:
        return "1"
    return status_before.iloc[-1]['Status']

# Mapping from status to color
status_colors = {
    "1": "green",     # Green flag
    "2": "yellow",    # Yellow flag
    "3": "red",       # Red flag
    "4": "white",     # Virtual Safety Car
    "5": "yellow",    # Safety Car
    "6": "black"      # Black flag
}

# Get pit stop data
def get_pit_stops():
    pit_stops = []
    for driver in drivers:
        driver_laps = session.laps[session.laps['Driver'] == driver]
        in_pit_laps = driver_laps[~pd.isnull(driver_laps['PitInTime'])]
        for _, lap in in_pit_laps.iterrows():
            if not pd.isnull(lap['PitInTime']) and not pd.isnull(lap['PitOutTime']):
                pit_stops.append({'driver': driver,
                                  'in_time': lap['PitInTime'],
                                  'out_time': lap['PitOutTime']})
    return pit_stops

pit_stops = get_pit_stops()

# Determine race start and end times
race_start = session.laps['LapStartTime'].min()
race_end = session.laps.dropna(subset=['Time']).apply(
    lambda x: x['LapStartTime'] + x['LapTime'] if not pd.isnull(x['LapTime']) else pd.NaT, axis=1
).max()

if pd.isnull(race_start) or pd.isnull(race_end):
    print("Could not determine race start/end times; using approximate values.")
    race_start = pd.Timedelta(seconds=0)
    sample_lap = session.laps.dropna(subset=['Time']).iloc[0] if not session.laps.empty else None
    race_end = race_start + sample_lap['Time'] * session.total_laps if sample_lap is not None else race_start + pd.Timedelta(hours=2)

print(f"Race duration: {race_end - race_start}")

start_time_sec = race_start.total_seconds()
end_time_sec = race_end.total_seconds()
speed_factor = 20
time_steps_full = np.linspace(start_time_sec, end_time_sec, int((end_time_sec - start_time_sec) / speed_factor * 10))
time_steps = time_steps_full[::SKIP_FRAMES]

print(f"Starting live simulation with {len(time_steps)} frames...")

# Enable interactive mode for live updates
plt.ion()
fig = plt.figure(figsize=(FIXED_WIDTH / 100, FIXED_HEIGHT / 100), dpi=100)

# Main simulation loop (live update)
for frame_idx, time_sec in enumerate(time_steps):
    # Clear figure for new frame
    fig.clf()
    gs = gridspec.GridSpec(2, 2, height_ratios=[4, 1], width_ratios=[4, 1], hspace=0.3, wspace=0.3)
    ax_track = fig.add_subplot(gs[0, 0])
    ax_position = fig.add_subplot(gs[1, 0])
    ax_info = fig.add_subplot(gs[0, 1])
    ax_legend = fig.add_subplot(gs[1, 1])

    current_time = pd.Timedelta(seconds=time_sec)

    # Determine current lap for each driver
    current_lap = {}
    for driver in drivers:
        driver_laps = session.laps[session.laps['Driver'] == driver]
        if not driver_laps.empty:
            for _, lap in driver_laps.iterrows():
                lap_start = lap['LapStartTime']
                lap_end = lap_start + lap['LapTime'] if not pd.isnull(lap['LapTime']) else None
                if lap_start <= current_time and (lap_end is None or current_time <= lap_end):
                    current_lap[driver] = lap['LapNumber']
                    break

    car_positions = []
    for driver, pos in position_data.items():
        if driver not in driver_info or pos.empty:
            continue
        # Get closest telemetry point to current time
        idx = pos['SessionTime'].searchsorted(current_time)
        if 0 <= idx < len(pos):
            x = pos['X'].iloc[idx] / 10  # Convert to meters
            y = pos['Y'].iloc[idx] / 10
            dx = pos['dx'].iloc[idx]
            dy = pos['dy'].iloc[idx]
            if rotation:
                rad = np.radians(rotation)
                rot_matrix = np.array([[np.cos(rad), -np.sin(rad)],
                                       [np.sin(rad),  np.cos(rad)]])
                x, y = np.dot(rot_matrix, np.array([x, y]))
                dx, dy = np.dot(rot_matrix, np.array([dx, dy]))
            team_color = driver_info[driver]['TeamColor']
            in_pit = any(pit_stop['driver'] == driver and pit_stop['in_time'] <= current_time <= pit_stop['out_time'] for pit_stop in pit_stops)
            size = 80 if not in_pit else 30
            alpha = 1.0 if not in_pit else 0.5

            car_positions.append({'driver': driver, 'x': x, 'y': y,
                                  'dx': dx, 'dy': dy, 'color': f"#{team_color}",
                                  'in_pit': in_pit, 'lap': current_lap.get(driver, 0)})
            ax_track.scatter(x, y, s=size, color=f"#{team_color}", alpha=alpha, zorder=10)
            if not in_pit:
                ax_track.text(x, y, driver, fontsize=8, ha='center', va='center',
                              color='white', fontweight='bold', zorder=11)

    # Display lateral distances between cars if enabled
    if SHOW_LATERAL:
        for i in range(len(car_positions)):
            for j in range(i + 1, len(car_positions)):
                car1, car2 = car_positions[i], car_positions[j]
                if car1['in_pit'] or car2['in_pit'] or abs(car1['lap'] - car2['lap']) > 1:
                    continue
                distance = np.hypot(car2['x'] - car1['x'], car2['y'] - car1['y'])
                if distance < 20:
                    lateral_dist1 = calculate_lateral_distance(car1['x'], car1['y'], car1['dx'], car1['dy'],
                                                               car2['x'], car2['y'])
                    lateral_dist2 = calculate_lateral_distance(car2['x'], car2['y'], car2['dx'], car2['dy'],
                                                               car1['x'], car1['y'])
                    lateral_dist = (lateral_dist1 + lateral_dist2) / 2
                    if lateral_dist > 0.5 and distance < 10:
                        mid_x, mid_y = (car1['x'] + car2['x']) / 2, (car1['y'] + car2['y']) / 2
                        ax_track.text(mid_x, mid_y, f"{lateral_dist:.1f}m", fontsize=7,
                                      bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.1'),
                                      ha='center', va='center', zorder=5)

    # Apply zoom settings
    if ZOOM_MODE == "full_track":
        ax_track.set_xlim(track_x_min, track_x_max)
        ax_track.set_ylim(track_y_min, track_y_max)
    elif ZOOM_MODE == "focus_driver" and FOCUS_DRIVER in [car['driver'] for car in car_positions if not car['in_pit']]:
        focus_car = next((car for car in car_positions if car['driver'] == FOCUS_DRIVER and not car['in_pit']), None)
        if focus_car:
            half_zoom = ZOOM_LEVEL / 2
            ax_track.set_xlim(focus_car['x'] - half_zoom, focus_car['x'] + half_zoom)
            ax_track.set_ylim(focus_car['y'] - half_zoom, focus_car['y'] + half_zoom)
        else:
            ax_track.set_xlim(track_x_min, track_x_max)
            ax_track.set_ylim(track_y_min, track_y_max)
    elif ZOOM_MODE == "dynamic":
        if car_positions:
            x_vals = [car['x'] for car in car_positions if not car['in_pit']]
            y_vals = [car['y'] for car in car_positions if not car['in_pit']]
            if x_vals and y_vals:
                x_center = sum(x_vals) / len(x_vals)
                y_center = sum(y_vals) / len(y_vals)
                max_x = max(abs(x - x_center) for x in x_vals) * 2.5
                max_y = max(abs(y - y_center) for y in y_vals) * 2.5
                window_size = max(max_x, max_y, ZOOM_LEVEL)
                ax_track.set_xlim(max(x_center - window_size, track_x_min), min(x_center + window_size, track_x_max))
                ax_track.set_ylim(max(y_center - window_size, track_y_min), min(y_center + window_size, track_y_max))
            else:
                ax_track.set_xlim(track_x_min, track_x_max)
                ax_track.set_ylim(track_y_min, track_y_max)
    ax_track.set_aspect('equal')

    # Get track status and update title
    status = get_track_status_at_time(current_time)
    status_color = status_colors.get(status, "green")
    race_time = current_time - race_start
    status_name = {
        "1": "GREEN FLAG", "2": "YELLOW FLAG", "3": "RED FLAG",
        "4": "VIRTUAL SAFETY CAR", "5": "SAFETY CAR", "6": "BLACK FLAG"
    }.get(status, "UNKNOWN")
    ax_track.set_title(f"{gp} {year} - Race Simulation\nTime: {race_time} - {status_name}",
                       color=status_color, fontweight='bold')

    # Plot position chart
    if position_by_lap:
        leader_lap = max(current_lap.values()) if current_lap else 1
        positions = {}
        for driver in drivers:
            if driver in position_by_lap and leader_lap in position_by_lap[driver].index:
                positions[driver] = position_by_lap[driver][leader_lap]
        sorted_drivers = sorted(positions.items(), key=lambda x: x[1])
        total_drivers = len(drivers)
        y_spacing = 1.0 / (total_drivers + 1)
        for i, (driver, _) in enumerate(sorted_drivers):
            if driver in driver_info:
                y_pos = 1.0 - (i + 1) * y_spacing
                team_color = f"#{driver_info[driver]['TeamColor']}"
                ax_position.barh(y_pos, 1, height=y_spacing * 0.8, color=team_color)
                ax_position.text(1.05, y_pos, f"{driver} - {driver_info[driver]['Abbreviation']}",
                                 va='center', fontsize=8)
        ax_position.set_yticks([])
        ax_position.set_xticks([])
        ax_position.set_xlim(0, 1.5)
        ax_position.set_ylim(0, 1)
        ax_position.set_title(f"Race Positions - Lap {leader_lap}", fontsize=10)

    # Race info panel
    ax_info.set_axis_off()
    ax_info.text(0.5, 0.95, f"{gp} GRAND PRIX {year}", fontsize=12, fontweight='bold',
                 ha='center', va='center')
    hrs, rem = divmod(race_time.total_seconds(), 3600)
    mins, secs = divmod(rem, 60)
    ax_info.text(0.5, 0.88, f"Race Time: {int(hrs):02d}:{int(mins):02d}:{int(secs):02d}",
                 fontsize=10, ha='center')
    ax_info.text(0.5, 0.82, status_name, fontsize=12, color=status_color,
                 fontweight='bold', ha='center')
    if car_positions:
        on_track = sum(1 for car in car_positions if not car['in_pit'])
        in_pit = sum(1 for car in car_positions if car['in_pit'])
        ax_info.text(0.5, 0.75, f"Cars on track: {on_track}", fontsize=9, ha='center')
        ax_info.text(0.5, 0.70, f"Cars in pit: {in_pit}", fontsize=9, ha='center')
    # Legend panel
    ax_legend.clear()
    ax_legend.set_axis_off()
    teams = {}
    for driver, info in driver_info.items():
        team = info['TeamName']
        teams.setdefault(team, []).append((driver, info['Abbreviation']))
    y_pos = 0.95
    for team, team_drivers in teams.items():
        color = f"#{driver_info[team_drivers[0][0]]['TeamColor']}"
        ax_legend.text(0.05, y_pos, team, fontsize=10, color=color, fontweight='bold')
        y_pos -= 0.05
        for driver, abbr in team_drivers:
            ax_legend.text(0.15, y_pos, f"{driver} - {abbr}", fontsize=9)
            y_pos -= 0.04
        y_pos -= 0.02
    ax_legend.set_title("Teams & Drivers", fontsize=12, fontweight='bold')
    print(lateral_dist, lateral_dist2, lateral_dist1)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    # Draw updated frame
    fig.canvas.draw()
    fig.canvas.flush_events()

    # If in live mode, pause briefly to simulate animation speed; otherwise, save the frame
    if LIVE_MODE:
        time.sleep(0.01)  # adjust sleep time as needed
    else:
        frame_filename = os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.png")
        plt.savefig(frame_filename)

print("\nSimulation complete!")
if not LIVE_MODE:
    print(f"Frames saved to {OUTPUT_DIR}/")
    print(f"To create a video, try: ffmpeg -framerate 10 -i {OUTPUT_DIR}/frame_%04d.png -c:v libx264 -pix_fmt yuv420p race_simulation.mp4")
