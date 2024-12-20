import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
from src.vector_math import Vectormath

class FocalMechanism(Vectormath):
    def __init__(self, strike1, dip1, rake1, strike2, dip2, rake2, kinematic_axes):
        super().__init__()
        self.plane_angles1 = [strike1, dip1, rake1]#TODO Consider negative rakes
        self.plane_angles2 = [strike2, dip2, rake2]
        self.kinematic_axes = kinematic_axes
    
    def compute_kinematic_vector(self, axis_name):
        return super().compute_kinematic_vector(self.kinematic_axes, axis_name)
    
    #region Plane1
    def compute_strike_vector1(self):
        return super().compute_strike_vector(self.plane_angles1)
    
    def compute_dip_vector1(self):
        return super().compute_dip_vector(self.plane_angles1)
    
    def compute_normal_vector1(self):
        return super().compute_normal_vector(self.plane_angles1)
    
    def compute_rake_vector1(self):
        return super().compute_rake_vector(self.plane_angles1)
    
    def create_vector_dict1(self):
        strike_vector = self.compute_strike_vector1()
        dip_vector = self.compute_dip_vector1()
        rake_vector = self.compute_rake_vector1()
        normal_vector = self.compute_normal_vector1()
        P_vector = self.compute_kinematic_vector("P")
        T_vector = self.compute_kinematic_vector("T")
        B_vector = self.compute_kinematic_vector("B")
        #Assertion of kinematic vectors
        P_vector2 = normal_vector - rake_vector
        P_vector2 = P_vector2 / np.linalg.norm(P_vector2)
        P_correct = np.isclose(P_vector, P_vector2)
        assert(P_correct.all())
        T_vector2 = normal_vector + rake_vector
        T_vector2 = T_vector2 / np.linalg.norm(T_vector2)
        T_correct = np.isclose(T_vector, T_vector2)
        assert(T_correct.all())
        B_vector2 = np.cross(T_vector, B_vector)
        B_vector2 = P_vector2 / np.linalg.norm(B_vector2)
        B_correct = np.isclose(B_vector, B_vector2)
        assert(B_correct.all())
        vector_dict = {'strike_vec': strike_vector,
                        'dip_vec': dip_vector,
                        'rake_vec':rake_vector,
                        'normal_vec': normal_vector,
                        'p_vec': P_vector,
                        't_vec': T_vector,
                        'b_vec': B_vector}
        return vector_dict
    #endregion
    #region Plane2
    def compute_strike_vector2(self):
        return super().compute_strike_vector(self.plane_angles2)
    
    def compute_dip_vector2(self):
        return super().compute_dip_vector(self.plane_angles2)
    
    def compute_normal_vector2(self):
        return super().compute_normal_vector(self.plane_angles2)
    
    def compute_rake_vector2(self):
        return super().compute_rake_vector(self.plane_angles2)
    
    def create_vector_dict2(self):
        normal_vector = self.compute_normal_vector2()
        strike_vector = self.compute_strike_vector2()
        dip_vector = self.compute_dip_vector2()
        rake_vector = self.compute_rake_vector2()
        P_vector = self.compute_kinematic_vector("P")
        T_vector = self.compute_kinematic_vector("T")
        B_vector = self.compute_kinematic_vector("B")

        vector_dict = {'strike_vec': strike_vector,
                        'dip_vec': dip_vector,
                        'rake_vec':rake_vector,
                        'normal_vec': normal_vector,
                        'p_vec': P_vector,
                        't_vec': T_vector,
                        'b_vec': B_vector}
        return vector_dict
    #endregion
    
    #region Plots
    def plot_focal_mechanism_3d(self, ax, radius = 1, num_pts = 100):
        # Plot a sphere
        phi, theta = np.mgrid[0:np.pi:100j, 0:2*np.pi:100j]
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        ax.plot_surface(x, y, z, color='lightblue', alpha=0.1, edgecolor='k')
        #Plot surface of fault plane
        normal_vec = self.compute_normal_vector1()
        phi = np.linspace(0, 2 * np.pi, num_pts)
        circle = np.array([np.cos(phi), np.sin(phi), np.zeros_like(phi)]) #Unit circle in XY plane
        z_axis = np.array([0, 0, 1])
        rotation, _ = R.align_vectors([normal_vec], [z_axis]) #Rotate circle to align with normal
        rotated_circle = rotation.apply(circle.T).T
        nodal_plane = radius * rotated_circle
        ax.plot_trisurf(nodal_plane[0], nodal_plane[1], nodal_plane[2], alpha=0.5) #Plot nodal fault plane
        #Plot vectors
        vector_dict = self.create_vector_dict1()
        colors = plt.cm.tab10(np.linspace(0, 1, len(vector_dict))) #Generate unique color for each vector
        for (name, vector), color in zip(vector_dict.items(), colors):
            ax.quiver(0, 0, 0, vector[0], vector[1], vector[2], color = color, length = radius, label = name)
        
        #Labels and styling
        ax.set_xlabel("X axis")
        ax.set_ylabel("Y axis")
        ax.set_zlabel("Z axis")
        ax.set_title("3D Focal Mechanism")
        ax.legend(loc = 'upper right')
        ax.set_box_aspect([1, 1, 1])
        

    #endregion
    
    
    