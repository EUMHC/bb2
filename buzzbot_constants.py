import random

import yaml

with open('configuration.yaml', 'r') as file:
    config = yaml.safe_load(file)


def get_uni_teams() -> [str]:
    return config['configuration']['teams']


def get_DistanceMatrix_credentials():
    api_key = config['configuration']['distance_matrix_ai']['api_key']
    return api_key


def get_taglines():
    taglines = config['configuration']['taglines']
    random.shuffle(taglines)
    return taglines
