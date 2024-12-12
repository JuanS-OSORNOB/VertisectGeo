import numpy as np
from math import pi, radians, degrees, sin, cos

class Vectormath:
    #region Methods
    def __init__(self, deg =True):
        self.deg = deg

    @staticmethod
    def convert_deg_to_rad(angles, degrees):
        if degrees: #NOTE Is my data in degrees?
            return [radians(x) for x in angles]
        return angles
    
    @staticmethod
    def normalize_vector(vector):
        return vector / np.linalg.norm(vector)
    
    @staticmethod
    def angle_between_vectors(vector1, vector2):
        dot_product = np.dot(vector1, vector2)
        magnitude_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        angle_rad = np.arccos(dot_product / magnitude_product)

        cross_product = np.cross(vector1, vector2)
        if cross_product[2] < 0: #If the z component of the cross product is negative it means the rotation is clockwise
            #Since its being measured from vector1 we need to subtract from 360 to make it counter-clockwise
            angle_rad = (2 * pi - angle_rad) % (2 * pi)
        angle_deg = degrees(angle_rad)
        return angle_deg
    
    def compute_normal_vector(self, plane_angles):
        strike, dip, rake = self.convert_deg_to_rad(plane_angles, self.deg)
        normal_vector = np.array([cos(strike)*sin(dip), sin(strike)*sin(dip), cos(dip)])
        normal_vector = self.normalize_vector(normal_vector)
        return normal_vector
    
    def compute_strike_vector(self, plane_angles):
        strike, _, _ = self.convert_deg_to_rad(plane_angles, self.deg)
        strike_vector = np.array([sin(strike), cos(strike), 0])
        strike_vector = self.normalize_vector(strike_vector)
        return strike_vector
    
    def compute_dip_vector(self):
        normal_vector = self.compute_normal_vector()
        strike_vector = self.compute_strike_vector()
        dip_vector = np.cross(strike_vector, normal_vector)
        dip_vector = self.normalize_vector(dip_vector)
        return dip_vector
    
    def compute_rake_vector(self, rake):
        strike_vector = self.compute_strike_vector()
        dip_vector = self.compute_dip_vector()
        if self.deg:
            rake_angle = radians(rake)
        rake_vector =  cos(rake_angle) * strike_vector + sin(rake_angle) * dip_vector
        return rake_vector
    
    def compute_kinematic_vector(self, kinematic_axes, axis_name):
        azimuth, plunge = self.convert_deg_to_rad(kinematic_axes[axis_name], self.deg)
        kinematic_vector = np.array([sin(azimuth)*cos(plunge), cos(azimuth)*cos(plunge), sin(plunge)])
        kinematic_vector = self.normalize_vector(kinematic_vector)
        return kinematic_vector
    #endregion