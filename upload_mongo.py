from pymongo import MongoClient
import json 
import os

connection_string = "mongodb+srv://Aryan:D4ThWEpRrHpSMpdx@cluster0.qfjzfgj.mongodb.net/bahrain?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(connection_string)

db = client['bahrain'] 

def upload():
    '''
    folder_path = 'new_car_data'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        collection_name = os.path.splitext(filename)[0] 
        collection = db[collection_name] 
        with open(file_path, "r") as file:
            data = json.load(file)
        collection.insert_many(data)
    '''
    with open('new_lap_data.json', 'r') as file:
        data = json.load(file)
    collection = db['lap_data'] 
    collection.insert_many(data)

    with open('new_location_data.json', 'r') as file:
        data = json.load(file)
    collection = db['location_data'] 
    collection.insert_many(data)

    with open('new_events_data.json', 'r') as file:
        data = json.load(file)
    collection = db['events_data'] 
    collection.insert_many(data)

upload()