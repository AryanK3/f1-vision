import json
import matplotlib.pyplot as plt

# Load JSON data from the file
with open("driver_data.json", "r") as file:
    data = json.load(file)

# Assuming the file contains a list with one driver object
driver = data[0]
positions = driver["positions"]

# Create a figure with fixed axis limits
plt.figure(figsize=(10, 6))
plt.xlim(-8000, 8000)
plt.ylim(-8000, 8000)

# Set custom tick marks (optional)
plt.xticks(range(-3000, 8000, 1000))
plt.yticks(range(-6000, 10000, 1000))

# Iterate over each position: each is [x, y, z, t]
for pos in positions:
    x, y, z, t = pos  # unpack the values
    print(x, y, z)  # print the coordinates (ignoring t)
    plt.scatter(x, y)
    plt.pause(0.001)  # brief pause to update the plot

plt.show()
