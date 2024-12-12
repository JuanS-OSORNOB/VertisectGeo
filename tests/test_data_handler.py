import pytest
from utils.data_handler import Datahandler
import os, sys

def test_load_earthquake_data():
    cwd = os.getcwd()
    # Test loading valid data
    earthquake_path = os.path.join(cwd, "tests/test_data/")
    earthquake_file = "test_data_handler.csv"
    profile_start = [-73.1, 13.01]
    profile_end = [-71.61, 10.51]
    datahandler = Datahandler(earthquake_path, earthquake_file, profile_start, profile_end)
    assert not datahandler.data.empty
    assert {"X", "Y", "Depth", "Magnitude"}.issubset(datahandler.data.columns)
    print("Finish testing")

test_load_earthquake_data()