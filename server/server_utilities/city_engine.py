import json




class CitySearchEngine:
    def __init__(self):
        return
    
    def open_citieslist(self):
        with open('cities.json', 'r') as cities_file:
            data = json.load(cities_file)
            return data





