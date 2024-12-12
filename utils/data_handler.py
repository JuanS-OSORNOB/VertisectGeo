import pandas as pd
import os
import numpy as np

class Datahandler():
    def __init__(self, path, filename, profile_start, profile_end):
        self.path = path
        self.filename  = filename
        self.data = self.load_earthquake_data()
        #Standardize depth values to positive
        if (self.data["Depth"] < 0).any():
            self.data["Depth"] = -self.data["Depth"]

        self.profile_start_km, self.profile_end_km = self.coordinates_to_km(profile_start, profile_end)

    def load_earthquake_data(self):
        file_path = os.path.join(self.path, self.filename)
        try:
            data = pd.read_csv(file_path, delimiter = ";")
            required_columns = {"X", "Y", "Depth", 'Magnitude'}
            if not required_columns.issubset(data.columns):
                raise ValueError(f"Dataset must contain the columns: {required_columns}")
            return data
        except Exception as e:
            print(f"Error loading earthquake data: {e}")
            return pd.DataFrame()
    
    def coordinates_to_km(self, profile_start, profile_end):
        lon_to_km = 111.0 * np.cos(np.radians(profile_start[1])) #X coordinates, adjusting for variation in latitude
        lat_to_km = 111.0 #Y coordinates
        self.data["X_km"] = self.data["X"] * lon_to_km
        self.data["Y_km"] = self.data["Y"] * lat_to_km
        profile_start_km = np.array(profile_start) * [lon_to_km, lat_to_km]
        profile_end_km = np.array(profile_end) * [lon_to_km, lat_to_km]

        return profile_start_km, profile_end_km

    def filter_earthquakes(self, profile_width, profile_depth):
        #Define profile vectors
        profile_vector = self.profile_end_km - self.profile_start_km
        profile_length = np.linalg.norm(profile_vector)
        profile_vector_unit = profile_vector / profile_length
        perpendicular_vector_unit = np.array([-profile_vector_unit[1], profile_vector_unit[0]])
        #Define profile polygon
        half_width = profile_width / 2
        vertice1 = self.profile_start_km + half_width * perpendicular_vector_unit
        vertice2 = self.profile_start_km - half_width * perpendicular_vector_unit
        vertice3 = self.profile_end_km + half_width * perpendicular_vector_unit
        vertice4 = self.profile_end_km - half_width * perpendicular_vector_unit

        def is_within_polygon(point):
            #NOTE Polygon edge orientation: Clockwise
            vector1 = vertice3 - vertice1
            vector2 = vertice4 - vertice3
            vector3 = vertice2 - vertice4
            vector4 = vertice1 - vertice2
            vector5 = point - vertice1
            vector6 = point - vertice3
            vector7 = point - vertice4
            vector8 = point - vertice2
            vectors = [(vector1, vector5), (vector2, vector6), (vector3, vector7), (vector4, vector8)]
            return all(np.cross(v1, v2) <= 0 for v1, v2 in vectors)

        coords = self.data[["X_km", "Y_km"]].values
        within_polygon = np.array([is_within_polygon(coord) for coord in coords])
        pre_filtered_data = self.data[within_polygon].copy()
        filtered_data = pre_filtered_data[pre_filtered_data["Depth"] <= profile_depth]

        return profile_vector_unit,  filtered_data
    
    def project_onto_profile(self, profile_width, profile_depth):
        profile_vector_unit, filtered_data = self.filter_earthquakes(profile_width, profile_depth)
        projected_data = filtered_data
        #projections = np.dot(filtered_data[["X_km", "Y_km"]].values - self.profile_start_km, profile_vector) / profile_length
        projections = np.dot(filtered_data[["X_km", "Y_km"]].values - self.profile_start_km, profile_vector_unit)
        projected_data["Profile_X"] = projections
        return projected_data