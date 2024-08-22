import os
import csv
import itertools
import pandas as pd
from tqdm import tqdm

import requests
import json
from buzzbot_constants import buzzbotConfiguration
from models import Fixture


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
        self.endpoint: str = (
            "https://api.distancematrix.ai/maps/api/distancematrix/json?"
        )
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

    def get_cache_size(self) -> int:
        return len(self.cache)

    def import_from_LocationManager(self, location_manager_dict: dict) -> None:
        self.locations = [
            DistanceMatrixLocation(location_id, location_data[0], location_data[1])
            for location_id, location_data in location_manager_dict.items()
        ]

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
                print(
                    f"[-] ERROR: fetching data issue when an API request has been made; status code {response.status_code}"
                )
                return None
        except Exception as e:
            print(
                f"[-] ERROR: an error when making a request to {self.request_url} has occurred. The following exception message has been thrown: {e}"
            )
            return None

    def parse_response(self):
        try:
            row = self.json_response["rows"][0]
            element = row["elements"][0]
            travel_time = element["duration"]["value"]
            return travel_time
        except (IndexError, KeyError):
            print("[-] ERROR: Unable to parse response correctly.")
            return None

    def get_travel_time_table(self) -> dict:
        print(("~" * 20) + " Initialising travel time table " + ("~" * 20))
        travel_times = {}
        for origin, destination in tqdm(itertools.combinations(self.locations, 2)):
            key = f"{origin.to_request_format()}_{destination.to_request_format()}"
            reverse_key = (
                f"{destination.to_request_format()}_{origin.to_request_format()}"
            )

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
        print("~" * 72)
        return travel_times


class LocationManager:
    def __init__(self, df: pd.DataFrame = None):
        """
        Initializes the LocationManager with an optional DataFrame.
        If no DataFrame is provided, the locations will be populated from the 'locations.csv' file.

        :param df: A pandas DataFrame containing location data with columns 'LocationName', 'Latitude', and 'Longitude'.
        """
        self.locations = {}
        self.SOURCE = "locations.csv"
        if df is not None:
            self.populate_from_dataframe(df)
        else:
            self.bootstrap()

    def add_location(self, name_: str, latitude_: float, longitude_: float) -> None:
        self.locations[name_] = (latitude_, longitude_)

    def get_location(self, name: str) -> (float, float):
        location = self.locations.get(name)
        if location is None:
            raise KeyError(
                f"Location with name '{name}' not found in the Location Manager. Have you spelt the "
                f"location correctly? Please refer to locations.csv file for correct locations and "
                f"spellings."
            )
        return location

    def get_all_locations(self) -> dict:
        return self.locations

    def get_all_location_names(self) -> [str]:
        return list(self.locations.keys())

    def get_all_coords_as_list(self) -> [(float, float)]:
        return list(self.locations.values())

    def bootstrap(self):
        """
        Populates the LocationManager from the default CSV file.
        """
        with open(self.SOURCE, mode="r", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            for row in reader:
                self.add_location(
                    row["LocationName"], float(row["Latitude"]), float(row["Longitude"])
                )

    def populate_from_dataframe(self, df: pd.DataFrame):
        """
        Populates the LocationManager with data from a pandas DataFrame.

        :param df: A pandas DataFrame containing location data with columns 'LocationName', 'Latitude', and 'Longitude'.
        """
        for _, row in df.iterrows():
            self.add_location(
                row["LocationName"], float(row["Latitude"]), float(row["Longitude"])
            )

    def return_matchday_location_subdictionary(self, locations: [str]) -> dict:
        """
        Returns key-value pairs (location, latlongs) of the match day locations only.

        :param locations: The list of location names for match day fixtures.
        :return: Dictionary of location names and latlong values.
        """
        return {l: self.get_location(l) for l in locations}
