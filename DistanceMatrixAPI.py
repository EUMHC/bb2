import os
import csv
import itertools

import requests
import json
from credentials import get_DistanceMatrix_credentials


class DistanceMatrixLocation:

    def __init__(self, id_: str, lat_: float, long_: float):
        self.id = id_
        self.lat = lat_
        self.long = long_

    def __repr__(self):
        return f"{self.id}: ({self.lat},{self.long})"

    def to_request_format(self) -> str:
        return f"{self.lat},{self.long}"


class DistanceMatrixInterface:

    def __init__(self, API_KEY_: str):
        self.API_KEY: str = API_KEY_
        self.endpoint: str = "https://api.distancematrix.ai/maps/api/distancematrix/json?"
        self.locations: [DistanceMatrixLocation] = []
        self.request_url: str = ""
        self.json_response: dict = {}
        self.number_of_requests = 0
        self.cache_file: str = "distance_matrix_cache.json"
        self.cache: dict = self.load_cache()

    def load_cache(self) -> dict:
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_cache(self) -> None:
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def add_to_cache(self, key: str, time: int) -> None:
        self.cache[key] = time
        self.save_cache()

    def import_from_LocationManager(self, location_manager_dict: dict) -> None:
        self.locations = [DistanceMatrixLocation(location_id, location_data[0], location_data[1]) for
                          location_id, location_data in location_manager_dict.items()]

    def build_distance_matrix_request(self, origin, destination):
        origins_str: str = origin.to_request_format()
        destinations_str: str = destination.to_request_format()
        url: str = f"{self.endpoint}origins={origins_str}&destinations={destinations_str}&key={self.API_KEY}"
        self.request_url = url

    def make_request(self):
        try:
            response = requests.get(self.request_url)
            self.number_of_requests += 1
            if response.status_code == 200:
                self.json_response = response.json()
            else:
                print(f"[-] ERROR: fetching data issue; status code {response.status_code}")
                return None
        except Exception as e:
            print(f"[-] ERROR: an error has occurred. {e}")
            return None

    def parse_response(self):
        try:
            row = self.json_response['rows'][0]
            element = row['elements'][0]
            travel_time = element['duration']['value']
            return travel_time
        except (IndexError, KeyError):
            print("[-] ERROR: Unable to parse response correctly.")
            return None

    def get_travel_time_table(self) -> dict:
        travel_times = {}
        for origin, destination in itertools.combinations(self.locations, 2):
            key = f"{origin.to_request_format()}_{destination.to_request_format()}"
            reverse_key = f"{destination.to_request_format()}_{origin.to_request_format()}"

            if key in self.cache:
                print(f"[+] Using cached value for {key}")
                travel_times[key] = self.cache[key]
            elif reverse_key in self.cache:
                print(f"[+] Using cached value for {reverse_key}")
                travel_times[key] = self.cache[reverse_key]
            else:
                print(f"[*] Handling {origin} and {destination} location request")
                self.build_distance_matrix_request(origin, destination)
                self.make_request()
                travel_time = self.parse_response()
                self.add_to_cache(key, travel_time)
                travel_times[key] = travel_time
        return travel_times


class LocationManager:

    def __init__(self):
        self.locations = {}
        self.SOURCE = "locations.csv"
        self.bootstrap()

    def add_location(self, name_: str, latitude_: float, longitude_: float) -> None:
        self.locations[name_] = (latitude_, longitude_)

    def get_location(self, name: str) -> (float, float):
        return self.locations.get(name)

    def get_all_locations(self) -> dict:
        return self.locations

    def get_all_location_names(self) -> [str]:
        return self.locations.keys()

    def get_all_coords_as_list(self) -> [(float, float)]:
        return self.locations.values()

    def bootstrap(self):
        with open(self.SOURCE, mode='r', encoding='utf-8') as source:
            reader = csv.DictReader(source)
            for row in reader:
                self.add_location(row['LocationName'], float(row['Latitude']), float(row['Longitude']))

    def return_matchday_location_subdictionary(self, locations: [str]) -> dict:
        """
        Returns key value pairs (location, latlongs) of the match day locations only
        :param locations:
        :return:
        """
        return {l: self.get_location(l) for l in locations}

# API_KEY = get_DistanceMatrix_credentials()
# handler = DistanceMatrixInterface(API_KEY_=API_KEY)
#
# lm = LocationManager()
#
# matchday_locations = ["St Andrews University Sports Centre", "Peffermill", "Titwood (Clydesdale Home)"]
# matchday_locations_dict = lm.return_matchday_location_subdictionary(matchday_locations)
# handler.import_from_LocationManager(location_manager_dict=matchday_locations_dict)
#
# print(handler.get_travel_time_table())
