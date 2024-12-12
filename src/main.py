import matplotlib.pyplot as plt
from utils.config import Config
from utils.data_handler import Datahandler
from plotter import VerticalSection
from focal_mechanism import FocalMechanism

def main():
    config_path = "config.json"
    config = Config.load_config(config_path)
    #Data
    config_data = config["data"]
    earthquake_path = config_data["earthquakes_path"]
    earthquake_file = config_data["earthquakes_file"]
    #Point profiles
    config_point_profiles = config["point_profiles"]
    num_profiles = len(config_point_profiles["profile_start"])
    #Initialize figure
    fig, axes = plt.subplots(nrows = num_profiles, ncols = 1, figsize = (15, 9*num_profiles))
    for i in range(num_profiles):
        profile_name = config_point_profiles["profile_name"][i]
        profile_start = config_point_profiles["profile_start"][i]
        profile_end = config_point_profiles["profile_end"][i]
        profile_width = config_point_profiles["profile_width"][i]
        profile_depth = config_point_profiles["profile_depth"][i]
        #Datahandler for this profile
        datahandler = Datahandler(earthquake_path, earthquake_file, profile_start, profile_end) #Instance of datahandler for this profile
        projected_data = datahandler.project_onto_profile(profile_width, profile_depth)
        print(f"Total events: {len(datahandler.data)}. Total events in bounds of profile {i+1}: {len(projected_data)}")
        #Plot on specific subplot
        ax = axes[i] if num_profiles > 1 else axes #Handle single-profile case
        plotter = VerticalSection()
        plotter.draw_cross_section(ax, projected_data, profile_depth, profile_name)
    plt.tight_layout()
    focal_mechanism = FocalMechanism()
    focal_mechanism.plot_focal_mechanism_3d()
    plt.show()
    

if __name__ == "__main__":
    main()