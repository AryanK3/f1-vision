from pprint import pprint
import matplotlib.pyplot as plt
import json

def load(filename):
    with open(filename, 'r') as file:
        return json.load(file)

for i, j in load("compressed_lap_data.json"):
    for k in range (len(j)):
        plt.scatter(j[k][0], j[k][1])
        plt.pause(j[k][3])
plt.show()