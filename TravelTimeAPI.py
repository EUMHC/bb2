import requests
import json
from credentials import get_TravelTime_credentials
from DistanceMatrixAPI import LocationManager


class TravelTimeLocation:

    def __init__(self, id_: str, lat_: float, long_: float):
        self.id = id_
        self.lat = lat_
        self.long = long_

    def __repr__(self):
        return f"{self.id}: ({self.lat},{self.long})"


class TravelTimeHandler:

    def __init__(self, API_KEY_: str, APP_ID_: str):
        self.API_KEY = API_KEY_
        self.APP_ID = APP_ID_
        self.locations_json = []
        self.location_objects = []

    def import_from_LocationManager(self, location_manager_dict: dict):
        self.locations_json = [
            {
                "id": location_id,
                "coords": {
                    "lat": location_data[0],
                    "lng": location_data[1]
                }
            }
            for location_id, location_data in location_manager_dict.items()
        ]

        self.location_objects = [TravelTimeLocation(id_=location_id, lat_=location_data[0], long_=location_data[1]) for
                                 location_id, location_data in location_manager_dict.items()]

    def get_travel_time_matrix(self):
        for location in self.location_objects:
            url, headers, data = self.build_request_string(location)
            self.make_single_api_request(url, headers, data)

    def make_single_api_request(self, url, headers, data):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                json_response = response.json()
                print(json_response)
            else:
                print(f"[-] ERROR: HTTP status code {response.status_code}")
                print(response.text)
        except Exception as e:
            print("[-] ERROR:", str(e))

    def parse_response_json(self, response):
        parsed_response = json.loads(response)

    def build_request_string(self, location: TravelTimeLocation):
        req = ""
        url = "https://api.traveltimeapp.com/v4/time-filter"
        headers = {
            "Content-Type": "application/json",
            "X-Application-Id": f"{self.APP_ID}",
            "X-Api-Key": f"{self.API_KEY}"
        }
        data = {
            "locations": self.locations_json,
            "departure_searches": [
                {
                    "id": "One-to-many Matrix",
                    "departure_location_id": location.id,
                    "arrival_location_ids": [l.id for l in self.location_objects],
                    "departure_time": "2024-01-18T08:00:00Z",
                    "travel_time": 3600,
                    "properties": [
                        "travel_time",
                        "distance"
                    ],
                    "transportation": {
                        "type": "driving"
                    }
                }
            ]
        }

        return url, headers, data


app_id, api_key = get_TravelTime_credentials()
handler = TravelTimeHandler(api_key, app_id)
lm = LocationManager()
matchday_locations = ["St Andrews University Sports Centre", "Peffermill", "Titwood (Clydesdale Home)"]
matchday_locations_dict = lm.return_matchday_location_subdictionary(matchday_locations)
handler.import_from_LocationManager(location_manager_dict=matchday_locations_dict)

print(handler.location_objects, sep='\n')
print(handler.locations_json)
print(handler.build_request_string(location=handler.location_objects[0]))

url, headers, data = handler.build_request_string(handler.location_objects[0])
handler.make_single_api_request(url, headers, data)
