import sys
import os

# Append project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.data_handler import Datahandler

def main():
    print("Starting")
    config_path = "config.json"
    config = Config.load_config(config_path)
    config_data = config["data"]
    earthquake_path = config_data["earthquake_path"]
    earthquake_file = config_data["earthquake_file"]
    data = Datahandler.load_earthquake_data(earthquake_path, earthquake_file)
    print(data)
    print("Finishing")
if __name__ == "main":
    main()