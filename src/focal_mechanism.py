import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from src.vector_math import Vectormath

class FocalMechanism(Vectormath):
    def __init__(self, strike, dip, rake, kinematic_axes):
        super().__init__()
        self.plane_angles = [strike, dip, rake]
        self.kinematic_axes = kinematic_axes
    
    def compute_normal_vector(self):
        return super().compute_normal_vector(self.plane_angles)
    
    def compute_strike_vector(self):
        return super().compute_strike_vector(self.plane_angles)
    
    def compute_dip_vector(self):
        return super().compute_dip_vector()
    
    def compute_rake_vector(self):
        return super().compute_rake_vector(self.plane_angles[2])
    
    def compute_kinematic_vector(self, axis_name):
        return super().compute_kinematic_vector(self.kinematic_axes, axis_name)
    
    def create_vector_dict(self):
        normal_vector = self.compute_normal_vector()
        strike_vector = self.compute_strike_vector()
        dip_vector = self.compute_dip_vector()
        rake_vector = self.compute_rake_vector()
        P_vector = self.compute_kinematic_vector("P")
        T_vector = self.compute_kinematic_vector("T")
        B_vector = self.compute_kinematic_vector("B")

        vector_dict = {'normal_vec': normal_vector,
                        'strike_vec': strike_vector,
                        'dip_vec': dip_vector,
                        'rake_vec':rake_vector,
                        'p_vec': P_vector,
                        't_vec': T_vector,
                        'b_vec': B_vector}
        return vector_dict
    
    #region Plots
    def plot_focal_mechanism_3d(self):
        # Create a sphere
        phi, theta = np.mgrid[0:np.pi:100j, 0:2*np.pi:100j]
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(x, y, z, color='lightblue', alpha=0.2, edgecolor='k')

        def generate_plane(normal, radius=1, num_points=100):
            # Normal vector (assume normalized)
            a, b, c = normal
            phi = np.linspace(0, 2 * np.pi, num_points)
            circle = np.array([np.cos(phi), np.sin(phi), np.zeros_like(phi)])  # Unit circle in XY

            # Rotate circle to align with normal
            from scipy.spatial.transform import Rotation as R
            rotation, _ = R.align_vectors([[0, 0, 1]], [normal])
            rotated_circle = rotation.apply(circle.T).T
            return radius * rotated_circle

        # Example normal vector
        nodal_plane = generate_plane([0.5, 0.5, 0.5])  # Replace with real normal vector
        nodal_plane2 = generate_plane([-0.5, 0.5, 0.5])  # Replace with real normal vector
        ax.plot_trisurf(nodal_plane[0], nodal_plane[1], nodal_plane[2], color='orange')
        ax.plot_trisurf(nodal_plane2[0], nodal_plane2[1], nodal_plane2[2], color='grey')
    
    #endregion
    
    
    