import math
import random
from datetime import timedelta


def get_opening_tagline():
    taglines = [
        "Ted Porter should do a pint",
        "On a warm summers evening, on a train bound for nowhere",
        "Jack Mead was the Greatest Vice President of All Time",
        "Joe Hutcheson stole your keys last social",
        "Trimble had a dream, to build a hockey team\nHe didn't have a stick or even a ball\nHe build from the back "
        "with Sam in attack\nThey are the 6s, they're on their way back!\nDu Du Du",
        "Stand up if you hate the 1s",
        "Stand up if you hate the 2s",
        "The 2s are in their beds",
        "See it off fresher!"
    ]
    return random.choice(taglines)


def calculate_confidence(I: timedelta, T: timedelta, sf: float = 0.1) -> float:
    """
    :param I: The interval between fixture A end time and fixture B pushback
    :param T: The proposed travel time to travel from fixture A to fixture B
    :param sf: Scale factor of the sigmoid function
    :return: Confidence metric between 0 and 1 where a high value is higher confidence
    """
    abs_diff = abs((I - T).total_seconds() / 60)
    confidence_metric = 1 / (1 + math.exp(-sf * abs_diff))
    return confidence_metric

#
# I = timedelta(hours=0, minutes=30)
# T = timedelta(hours=0, minutes=30)
# scale_factor = 0.2 # Adjust the scale factor as needed
#
# confidence = calculate_confidence(I, T, scale_factor)
# print("Confidence Metric:", confidence)
