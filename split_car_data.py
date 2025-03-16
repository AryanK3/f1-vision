import json
import os
with open('V1/car_data.json', 'r') as file:
    driver_data = json.load(file)

if not os.path.exists('car_data'):
    os.makedirs('car_data')

for driver in driver_data:
    driver_id = driver['id']
    filename = f"driver_{driver_id}.json"
    
    with open(f'car_data/{filename}', "w") as f:
        json.dump(driver, f)
    
