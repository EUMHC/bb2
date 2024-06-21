import pytest
import yaml
from unittest.mock import mock_open, patch

from buzzbot_constants import BuzzBotConfiguration, get_selection_criteria
from heuristics import GreedyFair

mock_config = """
distance_matrix_ai:
  api_key: "12345678901234567890"
"""

config_path = "../configuration.yaml"

def test_singleton_instance():
    instance1 = BuzzBotConfiguration(config_path)
    instance2 = BuzzBotConfiguration(config_path)
    assert instance1 is instance2

@patch("builtins.open", new_callable=mock_open, read_data=mock_config)
def test_load_configuration(mock_file):
    config = BuzzBotConfiguration("configuration.yaml")
    assert config.settings['distance_matrix_ai']['api_key'] == "12345678901234567890"

@patch("builtins.open", new_callable=mock_open, read_data=mock_config)
def test_validate_file_success(mock_file):
    config = BuzzBotConfiguration("configuration.yaml")
    assert config.settings['distance_matrix_ai']['api_key'] == "12345678901234567890"
