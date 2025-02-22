import json
import matplotlib.pyplot as plt

# Load the saved driver data from the file
with open('new_driver_data.json', 'r') as file:
    data = json.load(file)

# Create a figure for the 2D plot
plt.figure(figsize=(10, 7))

for i in data:
    for j in data[i]:
        plt.plot(j['x'], j['y'])
        plt.pause(0.0050)

# Set labels and title
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.title('2D Trajectories of Drivers')

# Show a legend
plt.legend()

# Display the plot
plt.show()
