import sys
import os

# Append project root directory to sys.path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.data_handler import Datahandler
from plotter import VerticalSection

def main():
    config_path = "config.json"
    config = Config.load_config(config_path)
    config_data = config["data"]
    earthquake_path = config_data["earthquakes_path"]
    earthquake_file = config_data["earthquakes_file"]
    config_point_profiles = config["point_profiles"]
    profile_start = config_point_profiles["profile_start"]
    profile_end = config_point_profiles["profile_end"]
    profile_width = config_point_profiles["profile_width"]
    profile_depth = config_point_profiles["profile_depth"]
    datahandler = Datahandler(earthquake_path, earthquake_file, profile_start, profile_end)
    data = datahandler.load_earthquake_data()
    print(data)
    print("All data.")
    _, filtered_data = datahandler.filter_earthquakes(profile_width, profile_depth)
    print(filtered_data)
    print("Filtered data.")

    num_profiles = len(config_point_profiles["profile_start"])

    projected_data = datahandler.project_onto_profile(profile_width, profile_depth)
    plotter = VerticalSection()
    plotter.draw_cross_section(projected_data, profile_depth, "Cross section BB'")

if __name__ == "__main__":
    main()