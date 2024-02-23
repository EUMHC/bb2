import math
import random
import subprocess
from datetime import timedelta


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


taglines = [
    "Ted Porter should do a pint",
    "On a warm summers evening, on a train bound for nowhere, I met up with the Gambler",
    "Jack Mead was the Greatest Vice President of All Time",
    "Joe Hutcheson stole your keys last social",
    "Trimble had a dream, to build a hockey team,\nHe didn't have a stick or even a ball,\nHe built from the back "
    "with Sam in attack,\nThey are the 6s, they're on their way back!\nDu Du Du",
    "Stand up if you hate the 1s",
    "Stand up if you hate the 2s",
    "The 2s are in their beds",
    "See it off fresher!",
    "Ritchie can't swim",
    "@Jack Jamieson",
    "Have you tried calling it?",
    "7s on fire, your defence is terrified",
    "I fucking love Bag Carrier. Or is it Carrier Bag?"
]


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
