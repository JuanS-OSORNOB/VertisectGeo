import numpy as np
from math import pi, radians, degrees, sin, cos, sqrt
from scipy.spatial.transform import Rotation as R
import matplotlib.path as mpath

class Vectormath:
    def __init__(self, deg =True):
        self.deg = deg

    @staticmethod
    def convert_deg_to_rad(angles, degrees):
        if degrees: #NOTE Is my data in degrees?
            return radians(angles)
        return angles
    
    @staticmethod
    def normalize_vector(vector):
        return vector / np.linalg.norm(vector)
    #region Vectors
    def compute_strike_vector(self, strike_angle):
        strike = self.convert_deg_to_rad(strike_angle, self.deg)
        sx = sin(strike)
        sy = cos(strike)
        sz = 0
        strike_vector = np.array([sx, sy,sz])
        #strike_vector = self.normalize_vector(strike_vector)
        return strike_vector
    
    def compute_dip_vector(self, strike_angle, dip_angle):
        strike = self.convert_deg_to_rad(strike_angle, self.deg)
        dip = self.convert_deg_to_rad(dip_angle, self.deg)
        dx = cos(strike) * cos(dip)
        dy = -sin(strike) * cos(dip) 
        dz = -sin(dip)
        dip_vector = np.array([dx, dy, dz])
        #dip_vector = self.normalize_vector(dip_vector)
        return dip_vector
    
    def compute_rake_vector(self, strike_angle, dip_angle, rake_angle):
        strike_vector = self.compute_strike_vector(strike_angle)
        dip_vector = self.compute_dip_vector(strike_angle, dip_angle)
        rake = self.convert_deg_to_rad(rake_angle, self.deg)
        rake_vector = cos(rake) * strike_vector + sin(rake) * dip_vector
        #rake_vector = self.normalize_vector(rake_vector)
        return rake_vector
    
    def compute_normal_vector(self, strike_angle, dip_angle):
        strike_vector = self.compute_strike_vector(strike_angle)
        dip_vector = self.compute_dip_vector(strike_angle, dip_angle)
        normal_vector = np.cross(dip_vector, strike_vector)
        #normal_vector = self.normalize_vector(normal_vector)
        return normal_vector
    
    def compute_kinematic_vector(self, kinematic_azimuth, kinematic_plunge):
        kinematic_azimuth = self.convert_deg_to_rad(kinematic_azimuth, self.deg)
        kinematic_plunge = self.convert_deg_to_rad(kinematic_plunge, self.deg)
        kx = sin(kinematic_azimuth) * cos(kinematic_plunge)
        ky = cos(kinematic_azimuth) * cos(kinematic_plunge)
        kz = -sin(kinematic_plunge)
        kinematic_vector = np.array([kx, ky, kz])
        #kinematic_vector = self.normalize_vector(kinematic_vector)
        return kinematic_vector
    #endregion
    #region Step 1: Plane circle
    def sort_pts_by_angle(self, points, D, S):
        u = self.normalize_vector(D)
        v = self.normalize_vector(S)
        normal_vec = np.cross(u, v)
        normal_vec = self.normalize_vector(normal_vec)
        #Project onto plane
        coords = points[:3, :] #Only (x, y, z). Shape (3, N).
        flags = points[3, :] #The flag row. Shape (N, ).
        points_proj = coords - np.outer(normal_vec, np.dot(normal_vec, coords))
        #Convert to local x', y' coordinates
        p_u = np.dot(u, points_proj)
        p_v = np.dot(v, points_proj)
        #Compute clockwise angle from v
        theta = np.arctan2(p_u, p_v)

        def normalize_angle(angle):
            tolerance = 1e-10
            angle = angle % (2 * pi)
            angle = np.where(np.isclose(angle, 2 * pi), 0.0, angle) #Leave other values unchanged
            angle = np.where(np.isclose(angle, 0.0), 0.0, angle)
            angle = np.where(np.isclose(angle, pi), pi, angle)
            angle = np.where(np.isclose(angle, pi + tolerance), pi, angle)
            return angle

        normal_theta = normalize_angle(theta)

        sorted_indices = np.argsort(normal_theta)
        #sorted_pts = points[:, sorted_indices]
        sorted_coords = coords[:, sorted_indices]
        sorted_flags = flags[sorted_indices]
        sorted_pts = np.vstack((sorted_coords, sorted_flags))
        return sorted_pts
    
    def point_exists(self, array, point):
        return np.any(np.all(np.isclose(array.T, point.T), axis=1))
    
    def generate_plane_circle(self, strike, dip, B_azimuth, B_plunge, num_pts = 50, radius = 1.0):
        phi = np.linspace(0, 2 * np.pi, num_pts) #Radians
        circle = np.array([np.cos(phi), np.sin(phi), np.zeros_like(phi)])  # Circle in XY plane

        # Align the circle with the fault plane normal
        z_axis = np.array([0, 0, 1])
        normal_vector = self.compute_normal_vector(strike, dip)
        normal_vector = self.normalize_vector(normal_vector)
        rotation, _ = R.align_vectors([normal_vector], [z_axis])
        rotated_circle = rotation.apply(circle.T).T
        nodal_plane = radius * rotated_circle

        #Filter below the equator
        mask = nodal_plane[2] <= 0
        nodal_plane_below_equator = nodal_plane[:, mask]

        #Remove last point as it is the same as first point
        if np.allclose(nodal_plane_below_equator[:, 0], nodal_plane_below_equator[:, -1]):
            nodal_plane_below_equator = nodal_plane_below_equator[:, :-1]

        #Add a flag to the points
        flags = np.zeros((1, nodal_plane_below_equator.shape[1])) #Initialize to 0
        nodal_plane_flags = np.vstack((nodal_plane_below_equator, flags))
        #Add the mandatory points (S and B).
        S = self.compute_strike_vector(strike)
        strike_pt = S[:, np.newaxis]
        strike_pt = np.vstack((strike_pt, [[0]])) #S flag is set to zero
        if not self.point_exists(nodal_plane_flags, strike_pt):
            nodal_plane_flags = np.concatenate((nodal_plane_flags, strike_pt), axis = 1)
        if not self.point_exists(nodal_plane_flags, -strike_pt):
            nodal_plane_flags = np.concatenate((nodal_plane_flags, -strike_pt), axis = 1)
        B = self.compute_kinematic_vector(B_azimuth, B_plunge)
        B_pt = B[:, np.newaxis]
        B_pt = np.vstack((B_pt, [[1]])) #B flag is set to one
        if not self.point_exists(nodal_plane_flags, B_pt):
            nodal_plane_flags = np.concatenate((nodal_plane_flags, B_pt), axis = 1)

        D = self.compute_dip_vector(strike, dip)
        nodal_plane_sorted = self.sort_pts_by_angle(nodal_plane_flags, D, S)

        return nodal_plane_sorted
    #endregion
    #region Step 2: Project
    def lambert_projection(self, x, y, z):
        scaling_factor = np.sqrt(2 / (1 - z))
        x_proj, y_proj = scaling_factor * x, scaling_factor * y
        return x_proj, y_proj
    
    def stereographic_projection(self, x, y, z):
        scaling_factor = 1 / (1 - z)
        x_proj, y_proj = scaling_factor * x, scaling_factor * y
        return x_proj, y_proj
    
    def slice_circle(self, nodal_plane_sorted):
        """Split 3D circle in halves to eventually construct the quadrants in the projected plane.
        """
        b_index = np.where(nodal_plane_sorted[3] == 1)[0][0] #Assumes only one B point exists in the array.
        first_half = nodal_plane_sorted[:, :b_index + 1] #Up to and including B.
        second_half = nodal_plane_sorted[:, b_index:] #From B to the end.
        #Project the sliced halves
        first_half_x, first_half_y, first_half_z = first_half[0], first_half[1], first_half[2]
        first_half_projx, first_half_projy = self.lambert_projection(first_half_x, first_half_y, first_half_z)
        second_half_x, second_half_y, second_half_z = second_half[0], second_half[1], second_half[2]
        second_half_projx, second_half_projy = self.lambert_projection(second_half_x, second_half_y, second_half_z)

        return first_half_projx, first_half_projy, second_half_projx, second_half_projy
    
    def create_arc(self, point1, point2, radius, num_pts = 100):
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        #Define the angle ranges
        theta1 = np.arctan2(y1, x1)
        theta2 = np.arctan2(y2, x2)
        #Normalize angles
        theta1 = theta1 % (2 * pi)
        theta2 = theta2 % (2 * pi)
        delta_theta = abs(theta2 - theta1)
        delta_theta = delta_theta % (2 * pi)
        #Ensure minor arc
        if delta_theta > pi:
            if theta2 > theta1:
                theta_part1 = np.linspace(theta2, 2 * pi, num = num_pts // 2, endpoint = False)
                theta_part2 = np.linspace(0, theta1, num = num_pts // 2 + 1)
                theta_arc = np.concatenate((theta_part1, theta_part2))
            else:
                theta_part1 = np.linspace(theta1, 2 * pi, num = num_pts // 2, endpoint = False)
                theta_part2 = np.linspace(0, theta2, num = num_pts // 2 + 1)
                theta_arc = np.concatenate((theta_part1, theta_part2))
        else:
            theta_arc = np.linspace(theta1, theta2, num = num_pts)
        x = radius * np.cos(theta_arc)
        y = radius * np.sin(theta_arc)
        arc_pts = np.vstack((x, y))
        #Sort clockwise
        angles = np.arctan2(arc_pts[0], arc_pts[1]) % (2 * pi)
        sorted_indices = np.argsort(angles)
        sorted_pts = arc_pts[:, sorted_indices]
        #Check delta between each pair of points
        angular_differences = np.diff(angles)
        angular_differences = np.abs(angular_differences)
        max_diff_index = np.argmax(angular_differences)
        max_diff = angular_differences[max_diff_index]
        index_start = max_diff_index + 1
        #Re-sort if necessary
        if max_diff > pi:
            re_sorted_pts = np.hstack((sorted_pts[:, index_start:], sorted_pts[:, :index_start]))
        else:
            re_sorted_pts = sorted_pts #No re sorting needed
        return re_sorted_pts
    #endregion
    #region Step3: Scale and Trans
    def scale_points(self, points, target_radius):
        original_radius = sqrt(2)
        scaling_factor = target_radius / original_radius
        scaled_pts = scaling_factor * points
        return scaled_pts

    def translate_points(self, points, center):
        """
        Translate points to a new coordinate system.

        Parameters:
            points (ndarray): Array of shape (2, N) where each column is a point (x, y).
            new_origin (tuple): The new origin (x_origin, y_origin).

        Returns:
            ndarray: Translated points in the new coordinate system.
        """
        # Convert new origin to a column vector for broadcasting
        center = np.array(center).reshape(2, 1)
        # Translate points
        translated_points = points + center
        return translated_points
    
    def point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using matplotlib Path."""
        path = mpath.Path(np.column_stack((polygon[0], polygon[1])))
        return path.contains_point(point)
    #endregion