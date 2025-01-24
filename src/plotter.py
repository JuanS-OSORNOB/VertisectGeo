import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.focal_mechanism import FocalMechanism

class VerticalSection():
    def __init__(self, depth_bins = None, magnitude_bins = None, colors = None, sizes = None):
        self.depth_bins = depth_bins or [0, 30, 70, 120, 180, 250]
        self.magnitude_bins = magnitude_bins or [0, 3, 4, 5, 6, 7]
        self.colors = colors or ["red", "orange", "yellow", "green", "blue"]
        self.sizes = sizes or [20, 50, 100, 200, 300]
    #region Earthquakes plots
    def draw_earthquakes_section(self, ax, projected_earthquake_data):
        projected_earthquake_data["Color"] = pd.cut(projected_earthquake_data["Depth"], bins = self.depth_bins, labels = self.colors, include_lowest=True)
        projected_earthquake_data["Size"] = pd.cut(projected_earthquake_data["Magnitude"], bins = self.magnitude_bins, labels = self.sizes, include_lowest = True).astype(float)
        ax.scatter(projected_earthquake_data["Profile_X"], projected_earthquake_data["Depth"], c = projected_earthquake_data["Color"], s = projected_earthquake_data["Size"], edgecolor = "k", zorder = 0)
    #endregion
    #region FMS plots
    def draw_fms_section(self, ax, projected_fms_data):
        """Draws the focal mechanisms in a section

        Args:
            ax (_type_): _description_
        """
        #projected_fms_data["radius"] = pd.cut(projected_fms_data["Magnitude"], bins = self.magnitude_bins, labels = self.sizes, include_lowest = True).astype(float)
        for i, focal_mech in projected_fms_data.iterrows():
            #radius = focal_mech["radius"]
            radius = 25
            center = (focal_mech["Profile_X"], focal_mech["Depth"])
            strike1 = focal_mech["Strike_1"]
            dip1 = focal_mech["Dip_1"]
            rake1 = focal_mech["Rake_1"]
            strike2 = focal_mech["Strike_2"]
            dip2 = focal_mech["Dip_2"]
            rake2 = focal_mech["Rake_2"]
            P_Az = focal_mech["P_Az"]
            P_pl = focal_mech["P_pl"]
            T_Az = focal_mech["T_Az"]
            T_pl = focal_mech["T_pl"]
            B_Az = focal_mech["B_Az"]
            B_pl = focal_mech["B_pl"]

            focal_mechanism = FocalMechanism(radius, center, strike1, dip1, rake1, strike2, dip2, rake2, P_Az, P_pl, T_Az, T_pl, B_Az, B_pl)
            focal_mechanism.draw_focal_mechanism_filled(ax)
    #endregion