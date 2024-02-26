import csv
import datetime
import math
import random
import subprocess
from datetime import datetime, timedelta
from difflib import SequenceMatcher

import DistanceMatrixAPI
import buzzbot_constants


class ExceptionWithList(Exception):
    def __init__(self, messages, *args):
        if not isinstance(messages, list):
            messages = [messages]
        self.messages = messages
        super().__init__("\n".join(self.messages))

    def __str__(self):
        return "\n".join(self.messages)


def print_ascii_header():
    ascii_art = '''
 _____ _           ______              ______       _   
|_   _| |          | ___ \             | ___ \     | |  
  | | | |__   ___  | |_/ /_   _ _______| |_/ / ___ | |_ 
  | | | '_ \ / _ \ | ___ \ | | |_  /_  / ___ \/ _ \| __|
  | | | | | |  __/ | |_/ / |_| |/ / / /| |_/ / (_) | |_ 
  \_/ |_| |_|\___| \____/ \__,_/___/___\____/ \___/ \__|
A program by Callum Alexander (thecatthatbarks)

`If the EUHC Cinematic Universe allowed myself, Jack Mead, and Ed Bury to do the umpiring assignments 
for EUMHC together at the same time. Then times that by 10 million.`
                                                      
'''
    print(ascii_art)


taglines = buzzbot_constants.get_taglines()


def get_opening_tagline():
    return random.choice(taglines)


def get_opening_tagline_with_cowsay():
    tagline = get_opening_tagline()
    command = ["cowsay", tagline]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    print(result.stdout)


def print_warning(message):
    warning = f'''
  {'*' * (len(message) + 4)}
  * {message} *
  {'*' * (len(message) + 4)}
  '''
    print(warning)


def compute_closest_location_string(target: str, locations: [str]) -> str:
    best_match = None
    highest_similarity = 0.0
    for s in locations:
        similarity = SequenceMatcher(None, target, s).ratio()
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = s
    return best_match


def validate_csv_format(file_path):
    lm = DistanceMatrixAPI.LocationManager()
    correct_locations = lm.get_all_location_names()
    errors = []
    errors_exist = False
    teams = buzzbot_constants.get_uni_teams()
    expected_headers = ['uni_team', 'opposition', 'start_time', 'umpires_needed', 'location']  # Example headers
    expected_num_columns = len(expected_headers)
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        headers = next(reader)
        if headers != expected_headers:
            errors_exist = True
            errors.append(f"Your column names in your input file are incorrect. The program got {headers} from you "
                          f"but expect {expected_headers}. Please go into the file and change the column names")

        for row_number, row in enumerate(reader, start=2):  # Starting from 2 because header is row 1
            if len(row) != expected_num_columns:
                errors_exist = True
                errors.append(
                    f"Row {row_number} - {row} - has incorrect number of columns. Got {len(row)} columns from "
                    f"you in that row but expected {expected_num_columns}")

            if row[0] not in teams:
                errors_exist = True
                errors.append(f"Row {row_number} - {row} - the first column which is meant to represent the uni team "
                              f"is not an actual uni team ({row[0]}). It should be 1s, 2s, 3s, 4s, 5s, 6s, or 7s")

            try:
                datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            except Exception as e:
                errors_exist = True
                errors.append(
                    f"Row {row_number} - {row} - start_time value is not of the correct format. It is {row[2]} and it "
                    f"should be of the format 'YYYY-MM-DD HH:MM:SS'")

            if not row[3].isdigit():
                errors_exist = True
                errors.append(
                    f"Row {row_number} - {row} - the umpires_needed value is not a number. It is instead {row[3]}")

            if int(row[3]) < 0 or int(row[3]) > 2:
                errors_exist = True
                errors.append(f"Row {row_number} - {row} - has an invalid number of umpires. It should either be 0, 1, "
                              f"or 2. It is currently {row[3]}")

            if row[4] not in correct_locations:
                errors_exist = True
                errors.append(
                    f"Row {row_number} - {row} - has an invalid match location. Have you spelt the name '{row[4]}'"
                    f" correctly? Did you possibly mean '{compute_closest_location_string(row[4], correct_locations)}' "
                    f"instead? Please refer to the location table for the correct location names.")

    return errors_exist, errors


def generate_unique_match_times(base_date, num_matches):
    generated_times = set()
    while len(generated_times) < num_matches:
        random_hour = random.normalvariate(14, 2)  # Mean at 14 (2 PM), with some standard deviation
        random_hour = max(11.5, min(random_hour, 20))  # Ensure time is within bounds
        hour = int(random_hour)
        minute = 30 if random.randint(0, 1) == 1 else 0  # Randomly choose between :00 and :30
        match_time = base_date.replace(hour=hour, minute=minute, second=0)
        generated_times.add(match_time)

    return sorted(list(generated_times))


def choose_location(locations):
    # 50% chance for "Peffermill", 50% for any other location
    return \
        random.choices(["Peffermill", random.choice([loc for loc in locations if loc != "Peffermill"])], weights=[1, 1],
                       k=1)[0]


def generate_csv(filename, num_days):
    base_date = datetime(2024, 2, 24)
    teams = ['1s', '2s', '3s', '4s', '5s', '6s', '7s']
    locations = [
        "Peffermill", "Titwood (Clydesdale Home)", "Edinburgh Academy North Pitch",
        "Fettes College - Wetwoods Health Club", "Falkirk High School", "Auchenhowie",
        "Garscube Sports Complex", "Stepps Playing Fields", "St Columbas School Kilmacolm",
        "Meadowmill", "Woodmill High School", "Glasgow Green (Glasgow National Hockey Centre)",
        "Forthbank", "St Andrews University Sports Centre", "Gannochy Sport Centre",
        "Dean's High School Livingston", "Meggetland", "Counteswells School Aberdeen",
        "Goldenacre", "MES (Mary Erskine School)", "Tweedbank Sports Complex", "Uddingston Hockey Club"
    ]
    opposition_names = ["Wildcats", "Clydesdale 2s", "Grange 3s", "Uddingston 2s", "Stirling Wanderers",
                        "Reivers", "Peebles", "St Andrews 1s", "Heriot Watt 1s", "Napier 1s", "Abertay", "Dundee 2s"]

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['uni_team', 'opposition', 'start_time', 'umpires_needed', 'location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for _ in range(num_days):
            day_date = base_date + timedelta(days=random.randint(0, 29))  # Random day within a month
            num_matches = random.randint(3, 7)  # Matches per day
            match_times = generate_unique_match_times(day_date, num_matches)
            used_teams = random.sample(teams, num_matches)  # Ensuring unique teams per day

            for i in range(num_matches):
                writer.writerow({
                    'uni_team': used_teams[i],
                    'opposition': random.choice(opposition_names),
                    'start_time': match_times[i].strftime('%Y-%m-%d %H:%M:%S'),
                    'umpires_needed': random.choices([0, 1, 2], weights=[10, 85, 5], k=1)[0] if used_teams[
                                                                                                    i] != "1s" else 0,
                    'location': choose_location(locations)
                })


def calculate_confidence(I: timedelta, T: timedelta) -> float:
    """
    Logistic function chosen with small value at 0 and a large value at 60
    :param I: The interval between fixture A end time and fixture B pushback
    :param T: The proposed travel time to travel from fixture A to fixture B
    :return: Confidence metric between 0 and 1 where a high value is higher confidence
    """
    abs_diff = abs((I - T).total_seconds() / 60)
    confidence_metric = 1 / (1 + math.exp(-0.1 * (abs_diff - 30)))
    return confidence_metric

# I = timedelta(hours=0, minutes=120)
# T = timedelta(hours=0, minutes=30)
# scale_factor = 0.2 # Adjust the scale factor as needed
#
# confidence = calculate_confidence(I, T)
# print("Confidence Metric:", confidence)
