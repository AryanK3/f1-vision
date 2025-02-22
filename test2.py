import json
import matplotlib.pyplot as plt

# Load the saved driver data from the file
with open('new_driver_data.json', 'r') as file:
    driver_data_dict = json.load(file)

# Create a figure for the 2D plot
plt.figure(figsize=(10, 7))

# Define a color map to assign a unique color to each driver
colors = plt.cm.tab20.colors  # You can adjust this color map as needed

# Plot the data for each driver
for idx, (driver_number, driver_data) in enumerate(driver_data_dict.items()):
    # Extract the x and y coordinates for the current driver
    x = [entry['x'] for entry in driver_data]
    y = [entry['y'] for entry in driver_data]

    # Plot the driver's data points in 2D space with a unique color
    plt.plot(x, y, label=f'Driver {driver_number}', color=colors[idx % len(colors)])

# Set labels and title
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.title('2D Trajectories of Drivers')

# Show a legend
plt.legend()

# Display the plot
plt.show()
