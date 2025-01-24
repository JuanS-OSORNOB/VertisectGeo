import matplotlib.pyplot as plt
from utils.config import Config
from utils.data_handler import Datahandler
from plotter import VerticalSection
from focal_mechanism import FocalMechanism
import pandas as pd
import os

def main():
    config_path = "config.json"
    config = Config.load_config(config_path)
    #Earthquake Data
    config_data = config["data"]
    earthquake_path = config_data["earthquakes_path"]
    earthquake_file = config_data["earthquakes_file"]
    earthquake_file_path = os.path.join(earthquake_path, earthquake_file)
    try:
        earthquake_data = pd.read_csv(earthquake_file_path, delimiter = ";")
        required_columns = {"Lon", "Lat", "Depth", "Magnitude"}
        if not required_columns.issubset(earthquake_data.columns):
            raise ValueError(f"Dataset must contain the columns: {required_columns}")
    except Exception as e:
        print(f"Error loading earthquake data: {e}")
        earthquake_data = pd.DataFrame()
    #Focal mechanism data
    fms_path = config_data["fms_path"]
    fms_file = config_data["fms_file"]
    focal_mech_path = os.path.join(fms_path, fms_file)
    try:
        fms_data = pd.read_csv(focal_mech_path, delimiter = ";")
        required_columns = {"Date", "Time_GMT", "Lat", "Lon", "Depth", "Magnitude", "Strike_1", "Dip_1", "Rake_1", "Strike_2", "Dip_2", "Rake_2", "P_Az", "P_pl", "T_Az", "T_pl", "B_Az", "B_pl"}
    except Exception as e:
        print(f"Error loading focal mechanism data: {e}")
        fms_data = pd.DataFrame()
    #Point profiles
    config_point_profiles = config["point_profiles"]
    num_profiles = len(config_point_profiles["profile_start"])
    #Initialize figure
    fig, axes = plt.subplots(nrows = num_profiles, ncols = 1, figsize = (15, 9 * num_profiles))
    for i in range(num_profiles):
        profile_name = config_point_profiles["profile_name"][i]
        profile_start = config_point_profiles["profile_start"][i]
        profile_end = config_point_profiles["profile_end"][i]
        profile_width = config_point_profiles["profile_width"][i]
        profile_depth = config_point_profiles["profile_depth"][i]
        #Earthquake datahandler for this profile
        earthquake_datahandler = Datahandler(earthquake_data, profile_start, profile_end) #Instance of earthquake_datahandler for this profile
        projected_earthquake_data = earthquake_datahandler.project_onto_profile(profile_width, profile_depth)
        print(f"Total events: {len(earthquake_datahandler.data)}. Total events in bounds of profile {i + 1}: {len(projected_earthquake_data)}")
        #FMS datahandler for this profile
        fms_datahandler = Datahandler(fms_data, profile_start, profile_end) #Instance of focal mechanism datahandler for this profile.
        projected_fms_data = fms_datahandler.project_onto_profile(profile_width, profile_depth)
        print(f"Total FMS: {len(fms_datahandler.data)}. Total FMS in bounds of profile {i + 1}: {len(projected_fms_data)}\n")
        #Plot on specific subplot
        ax = axes[i] if num_profiles > 1 else axes #Handle single-profile case
        plotter = VerticalSection()
        plotter.draw_fms_section(ax, projected_fms_data)
        plotter.draw_earthquakes_section(ax, projected_earthquake_data)
        ax.invert_yaxis()
        ax.set_ylim(profile_depth, -10)
        ax.set_aspect('equal')
        ax.set_title(profile_name)
        ax.set_xlabel("Distance along profile (km)")
        ax.set_ylabel("Depth (km)")
        ax.grid(True)
    #plt.tight_layout()
    #plt.subplots_adjust(hspace = 0.5)
    config_figure = config["figure_parameters"]
    figure_savepath = os.path.join(config_figure["figure_path"], config_figure["figure_name"])
    plt.savefig(figure_savepath, dpi = 600)
    plt.show()
    

if __name__ == "__main__":
    main()