import matplotlib.pyplot as plt
import pandas as pd

class VerticalSection:
    def __init__(self, depth_bins = None, magnitude_bins = None, colors = None, sizes = None):
        self.depth_bins = depth_bins or [0, 30, 70, 120, 180, 250]
        self.magnitude_bins = magnitude_bins or [0, 3, 4, 5, 6, 7]
        self.colors = colors or ["red", "orange", "yellow", "green", "blue"]
        self.sizes = sizes or [20, 50, 100, 200, 300]

    def draw_cross_section(self, projected_data, profile_depth, title):
        projected_data["Color"] = pd.cut(projected_data["Depth"], bins = self.depth_bins, labels = self.colors, include_lowest=True)
        projected_data["Size"] = pd.cut(projected_data["Magnitude"], bins = self.magnitude_bins, labels = self.sizes, include_lowest = True).astype(float)
        plt.figure(figsize=(10, 6))
        plt.scatter(projected_data["Profile_X"], projected_data["Depth"], c = projected_data["Color"], s = projected_data["Size"], edgecolor = "k")
        plt.gca().invert_yaxis()
        plt.ylim(profile_depth, -10)
        plt.gca().set_aspect('equal')
        #plt.colorbar(label = "Depth (km)")
        plt.title(title)
        plt.xlabel("Distance along profile (km)")
        plt.ylabel("Depth (km)")
        plt.grid(True)
        plt.show()