import json

# Read data from the file
with open('rel_rc_data.json', 'r') as file:
    data = json.load(file)

# Function to compress the data
def compress_data(data):
    compressed_data = []
    
    for entry in data:
        compressed_entry = {
            "category": entry["category"],
            "message": entry["message"],
            "rel_time": entry["rel_time"]
        }
        compressed_data.append(compressed_entry)
    
    return compressed_data

# Compress the data
compressed_data = compress_data(data)

# Write the compressed data back to a file
with open('compressed_output_file.json', 'w') as file:
    json.dump(compressed_data, file)

