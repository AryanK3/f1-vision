import json

# Function to read and transform the data
def transform_data(input_file, output_file):
    # Open and read the original data file
    with open(input_file, 'r') as infile:
        data = json.load(infile)
    
    # Transform the data
    transformed_data = []
    for entry in data:
        transformed_data.append([entry['type'], round(entry['time'], 3), entry['message']])
    
    # Write the transformed data to the output file
    with open(output_file, 'w') as outfile:
        json.dump(transformed_data, outfile)

# Usage example
input_file = 'events_data.json'  # Change to your input file name
output_file = 'event_data.json'  # Change to your desired output file name
transform_data(input_file, output_file)

