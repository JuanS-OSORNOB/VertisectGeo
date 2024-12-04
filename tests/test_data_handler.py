import pytest
from utils.data_handler import Datahandler.load_earthquake_data

def test_load_earthquake_data():
    # Test loading valid data
    data = load_earthquake_data("test_data/test_data_handler.csv")
    assert not data.empty
    assert {"X", "Y", "Depth", "Magnitude"}.issubset(data.columns)