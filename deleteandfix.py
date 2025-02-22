import json


def load(filename):
    with open(filename, "r") as file:
        return json.load(file)


data = load("rel_racecontrol_data.json")


# Function to round values to 3 decimal places
def round_values(data):
    for entry in data:
        # Round the duration fields to 3 decimal places
        del entry["date"]
    return data


# Round the values in the data
rounded_data = round_values(data)

# Print the updated data
with open("rel_rc_data.json", "w") as file:
    json.dump(rounded_data, file, indent=4)

# url = "https://api.openf1.org/v1/location?session_key=9496&driver_number=1&date%3E2024-04-07T05:00:00.000&date%3C2024-04-07T07:00:00.000"
