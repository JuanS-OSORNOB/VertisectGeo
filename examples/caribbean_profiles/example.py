import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from utils.config import Config
from utils.data_handler import Datahandler
from src.plotter import VerticalSection
from src.height_profile import Heightprofile
cwd = os.getcwd()
def main():
    config_filename = "config_example.json"
    config_path = os.path.join(cwd,"examples/caribbean_profiles/" , config_filename)
    config = Config.load_config(config_path)
    config_data = config["data"]
    #Earthquake Data
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
    print(f"Total events: {len(earthquake_data)}.")
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
    print(f"Total FMS: {len(fms_data)}.")
    #Elevation data
    grd_file = os.path.join(config_data["dem_path"], config_data["dem_file"])
    #Point profiles
    config_point_profiles = config["point_profiles"]
    num_profiles = len(config_point_profiles["profile_start"])
    #Initialize figure and loop through each subplot
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
        print(f"     Total events in bounds of profile {str(profile_name)}: {len(projected_earthquake_data)}")
        #FMS datahandler for this profile
        fms_datahandler = Datahandler(fms_data, profile_start, profile_end) #Instance of focal mechanism datahandler for this profile.
        projected_fms_data = fms_datahandler.project_onto_profile(profile_width, profile_depth)
        print(f"     Total FMS in bounds of profile {str(profile_name)}: {len(projected_fms_data)}")
        #Topography for this profile
        heigth_profile = Heightprofile(grd_file, profile_start, profile_end)
        distances, elevations = heigth_profile.extract_profile()
        #Interpolate topography at Profile_X points and filter earthquakes below
        interp_func = interp1d(distances, elevations, kind='linear', fill_value="extrapolate")
        projected_earthquake_data["Topo_Elevation"] = interp_func(projected_earthquake_data["Profile_X"])
        projected_earthquake_data = projected_earthquake_data[projected_earthquake_data["Depth"] < projected_earthquake_data["Topo_Elevation"]]
        print(f"     Total events (filtered) in bounds of profile {profile_name}: {len(projected_earthquake_data)}\n")
        #Plot on specific subplot
        ax = axes[i] if num_profiles > 1 else axes #Handle single-profile case
        plotter = VerticalSection()
        max_exag_elev = plotter.draw_height_profile(ax, distances, elevations)
        #print(f"Min and max elevations (exaggerated) = {min_exag_elev, max_exag_elev}")
        plotter.draw_earthquakes_section(ax, projected_earthquake_data)
        plotter.draw_fms_section(ax, projected_fms_data)
        #ax.invert_yaxis()
        ax.set_ylim(profile_depth, max_exag_elev)
        ax.set_aspect('equal')
        ax.tick_params(axis='both', labelsize=16)
        ax.set_xlabel("Distance along profile (km)", fontsize = 20)
        ax.set_ylabel("Depth (km)", fontsize = 20)
        ax.set_title(profile_name, fontsize = 25)
        ax.grid(True)
        #ax.legend()
    plt.tight_layout()
    #plt.subplots_adjust(hspace = 0.5)
    config_figure = config["figure_parameters"]
    figure_savepath = os.path.join(config_figure["figure_path"], config_figure["figure_name"])
    plt.savefig(figure_savepath, dpi = 600)
    plt.show()
    print("FINISHED")

if __name__ == "__main__":
    main()