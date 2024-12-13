import numpy as np
from math import pi, radians, degrees, sin, cos
#NOTE Python math functions automatically return angle directionality COUNTER-CLOCKWISE from +x axis.

class Vectormath:
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
    
    def compute_strike_vector(self, plane_angles):
        strike, _, _ = self.convert_deg_to_rad(plane_angles, self.deg)
        sx = sin(strike) #range between -1 and 1
        sy = cos(strike) #range between -1 and 1
        sz = 0
        strike_vector = np.array([sx, sy,sz])
        strike_vector = self.normalize_vector(strike_vector)
        return strike_vector
    
    def compute_dip_vector(self, plane_angles):
        strike, dip, _ = self.convert_deg_to_rad(plane_angles, self.deg)

        dx = cos(strike) * cos(dip) #range between -1 and 1
        dy = sin(strike) * cos(dip) #range between -1 and 1
        dz = sin(dip) #range between 0 and 1 (always positive)
        dy = -dy #It must always be pointing down and to the right of the strike vector
        dz = -dz #It must always be pointing down and to the right of the strike vector
        dip_vector = np.array([dx, dy, dz])
        dip_vector = self.normalize_vector(dip_vector)
        return dip_vector
    
    def compute_rake_vector(self, plane_angles):
        strike, dip, rake = self.convert_deg_to_rad(plane_angles, self.deg)
        """ rx = cos(rake) * sin(strike) + sin(rake) * cos(strike) * cos(dip) #range between -1 and 1
        ry = cos(rake) * cos(strike) + sin(rake) * sin(strike) * cos(dip) #range between -1 and 1
        rz = sin(rake) * sin(dip) #range between -1 and 1
        rake_vector = np.array([rx, ry, rz])
        rake_vector = self.normalize_vector(rake_vector) """
        #Sanity check: Rake vector should a linear combination of strike and dip vectors.  
        strike_vector = self.compute_strike_vector(plane_angles)
        dip_vector = self.compute_dip_vector(plane_angles)
        rake_vector =  cos(rake) * strike_vector + sin(rake) * dip_vector
        rake_vector = self.normalize_vector(rake_vector)
        #rake_correct = np.isclose(rake_vector, rake_vector2)
        #assert(rake_correct.all())
        return rake_vector
    
    def compute_normal_vector(self, plane_angles):
        strike, dip, rake = self.convert_deg_to_rad(plane_angles, self.deg)
        nx = cos(strike) * sin(dip)
        ny = sin(strike) * sin(dip)
        nz = cos(dip)
        nx = nx
        ny = -ny
        nz = nz
        normal_vector = np.array([nx, ny, nz])
        normal_vector = self.normalize_vector(normal_vector)
        #Sanity check: Normal vector should be cross product of dip and strike vectors.
        strike_vector = self.compute_strike_vector(plane_angles)
        dip_vector = self.compute_dip_vector(plane_angles)
        normal_vector2 = np.cross(dip_vector, strike_vector)
        normal_correct = np.isclose(normal_vector, normal_vector2)
        assert(normal_correct.all())
        return normal_vector
    
    def compute_kinematic_vector(self, kinematic_axes, axis_name):
        azimuth, plunge = self.convert_deg_to_rad(kinematic_axes[axis_name], self.deg)
        kx = sin(azimuth) * cos(plunge)
        ky = cos(azimuth) * cos(plunge)
        kz = sin(plunge)
        kinematic_vector = np.array([kx, ky, kz])
        kinematic_vector = self.normalize_vector(kinematic_vector)
        return kinematic_vector