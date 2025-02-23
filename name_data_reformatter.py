import json

# Load the original data from name_data.json
with open("name_data.json", "r") as file:
    data = json.load(file)

# Transform the list into the desired dictionary format
formatted_data = {}
for entry in data:
    key = entry[0]
    formatted_data[key] = {
        "name": entry[1],
        "countrycode": entry[2],
        "team": entry[3],
        "photo": entry[4]
    }

# Write the transformed data to a new JSON file
with open("formatted_data.json", "w") as outfile:
    json.dump(formatted_data, outfile, indent=4)

print("Data has been successfully formatted and saved to formatted_data.json")
