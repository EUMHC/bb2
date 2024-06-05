import random
import yaml

from heuristics import SelectionFunction, GreedyFair
class BuzzBotConfiguration:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BuzzBotConfiguration, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, config_file='configuration.yaml'):
        if self.__initialized:
            return
        self.__initialized = True
        self.config_file = config_file
        self.load()
        self.validate_file()
    def load(self):
        try:
            with open(self.config_file, 'r') as file:
                self.settings = yaml.safe_load(file) or {}
        except FileNotFoundError:
            # TODO - make these the default settings, not an empty dictionary.
            self.settings = {}


    def validate_file(self):
        if len(self.settings['distance_matrix_ai']['api_key']) < 20:
            raise ValueError("DistanceMatrix API not recognised as correct format")

    def save(self):
        with open(self.config_file, 'w') as file:
            yaml.safe_dump(self.settings, file)


# Singleton instantiation
buzzbotConfiguration = BuzzBotConfiguration("configuration.yaml")


def get_selection_criteria() -> SelectionFunction:
    return GreedyFair()
