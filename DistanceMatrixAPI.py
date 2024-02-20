import csv

import requests
import json
import pandas as pd
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

    def import_from_LocationManager(self, location_manager_dict: dict) -> None:
        self.locations = [DistanceMatrixLocation(location_id, location_data[0], location_data[1]) for
                          location_id, location_data in location_manager_dict.items()]

    def build_distance_matrix_request(self):
        request_ready_locations: [str] = [l.to_request_format() for l in self.locations]
        origins_str: str = "|".join(request_ready_locations)
        destinations_str: str = "|".join(request_ready_locations)
        url: str = f"{self.endpoint}origins={origins_str}&destinations={destinations_str}&key={self.API_KEY}"
        self.request_url = url

    def make_request(self):
        try:
            response = requests.get(self.request_url)
            if response.status_code == 200:
                self.json_response = response.json()
            else:
                print(f"[-] ERROR: fetching data issue, status code {response.status_code}")
                return
        except Exception as e:
            print(f"[-] ERROR: an error has occurred. {e}")
            return

    def parse_response(self):

        origins = set()
        destinations = set()

        for row in self.json_response['rows']:
            for element in row['elements']:
                origins.add(element['origin'])
                destinations.add(element['destination'])

        lat_longs = origins.union(destinations)
        print(lat_longs)

        df_response = pd.DataFrame(index=list(lat_longs), columns=list(lat_longs)).fillna(
            'N/A')

        for i, row in enumerate(self.json_response['rows']):
            origin_lat_long = row['elements'][0]['origin']
            for j, element in enumerate(row['elements']):
                destination_lat_long = element['destination']
                df_response.at[origin_lat_long, destination_lat_long] = element['duration']['value']

        return df_response

    def get_travel_time_matrix(self) -> pd.DataFrame:
        self.build_distance_matrix_request()
        self.make_request()
        return self.parse_response()


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

#
# API_KEY = get_DistanceMatrix_credentials()
# handler = DistanceMatrixInterface(API_KEY_=API_KEY)
#
# lm = LocationManager()
#
# matchday_locations = ["St Andrews University Sports Centre", "Peffermill", "Titwood (Clydesdale Home)"]
# matchday_locations_dict = lm.return_matchday_location_subdictionary(matchday_locations)
# handler.import_from_LocationManager(location_manager_dict=matchday_locations_dict)
#
# print(handler.get_travel_time_matrix())
