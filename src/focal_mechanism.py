import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from math import sqrt
from src.vector_math import Vectormath

class FocalMechanism(Vectormath):
    def __init__(self, radius, center, strike1, dip1, rake1, strike2, dip2, rake2, P_Az, P_pl, T_Az, T_pl, B_Az, B_pl):
        super().__init__()
        self.radius = radius
        self.center = center
        self.strike1 = strike1
        self.dip1 = dip1
        self.rake1 = rake1
        self.strike2 = strike2
        self.dip2 = dip2
        self.rake2 = rake2
        self.P_Az = P_Az
        self.P_pl = P_pl
        self.T_Az = T_Az
        self.T_pl = T_pl
        self.B_Az = B_Az
        self.B_pl = B_pl
    #region Construc quadrants
    
    def construct_quadrants(self, nodal_plane_sorted1, nodal_plane_sorted2):
        first_half_projx1, first_half_projy1, second_half_projx1, second_half_projy1 = super().slice_circle(nodal_plane_sorted1)
        first_half_projx2, first_half_projy2, second_half_projx2, second_half_projy2 = super().slice_circle(nodal_plane_sorted2)
        #Points on the circle
        S1_proj = np.array([first_half_projx1[0], first_half_projy1[0]])
        neg_S1_proj = np.array([second_half_projx1[-1], second_half_projy1[-1]])
        S2_proj = np.array([first_half_projx2[0], first_half_projy2[0]])
        neg_S2_proj = np.array([second_half_projx2[-1], second_half_projy2[-1]])
        #Verify the radius
        radius_S1 = np.linalg.norm(S1_proj)
        radius_neg_S1 = np.linalg.norm(neg_S1_proj)
        radius_S2 = np.linalg.norm(S2_proj)
        radius_neg_S2 = np.linalg.norm(neg_S2_proj)
        radius = sqrt(2)
        assert np.isclose(radius_S1, radius_S2, radius_neg_S1, radius_neg_S2, radius), "Points are not on the same circle."
        #Create 4 arcs
        arc1 = super().create_arc(S1_proj, S2_proj, radius)
        arc2 = super().create_arc(S2_proj, neg_S1_proj, radius)
        arc3 = super().create_arc(neg_S2_proj, neg_S1_proj, radius)
        arc4 = super().create_arc(neg_S2_proj, S1_proj, radius)
        #Create sides (in projected coordinates)
        side_pts_first_half1 = np.vstack((first_half_projx1, first_half_projy1))
        side_pts_second_half1 = np.vstack((second_half_projx1, second_half_projy1))
        side_pts_first_half2 = np.vstack((first_half_projx2, first_half_projy2))
        side_pts_second_half2 = np.vstack((second_half_projx2, second_half_projy2))
        #Create polygons
        polygon1 = arc1
        if np.allclose(polygon1[:, -1], side_pts_first_half2[:, 0]):
            polygon1 = np.hstack((polygon1, side_pts_first_half2[:, 1:], side_pts_first_half1[:, ::-1][:, 1:]))
        else:
            polygon1 = np.hstack((polygon1, side_pts_first_half1[:, 1:], side_pts_first_half2[:, ::-1][:, 1:]))

        polygon2 = arc2
        if np.allclose(polygon2[:, -1], side_pts_second_half1[:, -1]):
            polygon2 = np.hstack((polygon2, side_pts_second_half1[:, ::-1][:, 1:-1], side_pts_first_half2[:, ::-1]))
        else:
            polygon2 = np.hstack((polygon2, side_pts_first_half2[:, 1:], side_pts_second_half1[:, 1:]))

        polygon3 = arc3
        if np.allclose(polygon3[:, -1], side_pts_second_half2[:, -1]):
            polygon3 = np.hstack((polygon3, side_pts_second_half2[:, ::-1][:, 1:-1], side_pts_second_half1))
        else:
            polygon1 = np.hstack((polygon1, side_pts_second_half1[:, ::-1][:, 1:-1], side_pts_second_half2))

        polygon4 = arc4
        if np.allclose(polygon4[:, -1], side_pts_first_half1[:, 0]):
            polygon4 = np.hstack((polygon4, side_pts_first_half1[:, 1:-1], side_pts_second_half2))
        else:
            polygon4 = np.hstack((polygon4, side_pts_second_half2[:, ::-1][:, 1:-1], side_pts_first_half1[:, ::-1]))

        return polygon1, polygon2, polygon3, polygon4
    #endregion
    #region Draw a single FM
    def draw_rake(self, ax, axis, axis_name):
        x, y, z = axis[0], axis[1], axis[2]
        X, Y = super().lambert_projection(x, y, z)
        projected_points = np.array([[X], [Y]])
        #Scale and translate
        scaled_pts = super().scale_points(projected_points, self.radius)
        translated_pts = super().translate_points(scaled_pts, self.center)
        ax.scatter(translated_pts[0], translated_pts[1], label = f"{axis_name}")
        
    def draw_kinematic_axis(self, ax, axis, axis_name):
        x, y, z = axis[0], axis[1], axis[2]
        X, Y = super().lambert_projection(x, y, z)
        projected_points = np.array([[X], [Y]])
        #Scale and translate
        scaled_pts = super().scale_points(projected_points, self.radius)
        translated_pts = super().translate_points(scaled_pts, self.center)
        ax.scatter(translated_pts[0], translated_pts[1], label = f"{axis_name}", marker = 's')
    
    def draw_focal_mechanism_filled(self, ax):
        #fig = plt.figure(figsize=(8, 8))
        #ax = fig.add_subplot(111)
        #ax.scatter(0, 0)
        #Plot origin
        origin = np.array(self.center).reshape(2, 1)
        ax.scatter(origin[0], origin[1], color = 'k')
        #Fill up the polygons according to T location
        T_vec = super().compute_kinematic_vector(self.T_Az, self.T_pl)
        T_proj_x, T_proj_y = super().lambert_projection(T_vec[0], T_vec[1], T_vec[2])
        T_proj = np.array([[T_proj_x], [T_proj_y]])
        T_proj = super().scale_points(T_proj, self.radius)
        T_proj = super().translate_points(T_proj, self.center)

        nodal_plane1 = super().generate_plane_circle(self.strike1, self.dip1, self.B_Az, self.B_pl)
        nodal_plane2 = super().generate_plane_circle(self.strike2, self.dip2, self.B_Az, self.B_pl)
        polygon1, polygon2, polygon3, polygon4 = self.construct_quadrants(nodal_plane1, nodal_plane2)
        #Scale and translate
        polygon1, polygon2, polygon3, polygon4 = super().scale_points(polygon1, self.radius), super().scale_points(polygon2, self.radius), super().scale_points(polygon3, self.radius), super().scale_points(polygon4, self.radius)
        polygon1, polygon2, polygon3, polygon4 = super().translate_points(polygon1, self.center), super().translate_points(polygon2, self.center), super().translate_points(polygon3, self.center), super().translate_points(polygon4, self.center)
        polygons = [polygon1, polygon2, polygon3, polygon4]

        containing_index = None
        for i, polygon in enumerate(polygons):
            if super().point_in_polygon(T_proj, polygon):
                containing_index = i
                break
        if containing_index is not None:
            second_index = (containing_index + 2) % len(polygons)
            for i, polygon in enumerate(polygons):
                if i == containing_index or i == second_index:
                    ax.fill(polygon[0], polygon[1], color = f"black", zorder = 5)
                else:
                    ax.fill(polygon[0], polygon[1], color = f"white", edgecolor = f"black", zorder = 5)
        #Draw the rake and kinematic axes
        #self.draw_kinematic_axis(ax, T_vec,  "T")
        #rake_vec1 = super().compute_rake_vector(self.strike1, self.dip1, self.rake1)
        #self.draw_rake(ax, rake_vec1,  "Rake 1")
        #rake_vec2 = super().compute_rake_vector(self.strike2, self.dip2, self.rake2)
        #self.draw_rake(ax, rake_vec2,  "Rake 2")
        #P_vec = super().compute_kinematic_vector(self.P_Az, self.P_pl)
        #self.draw_kinematic_axis(ax, P_vec,  "P")
        #B_vec = super().compute_kinematic_vector(self.B_Az, self.B_pl)
        #self.draw_kinematic_axis(ax, B_vec,  "B")
        #Add stereonet boundary
        circle = plt.Circle(self.center, self.radius, color='black', fill=False, linewidth=1)
        ax.add_artist(circle)
        #Figure optionals
        #ax.set_xlim(-self.radius, self.radius)
        #ax.set_ylim(-self.radius, self.radius)
        #ax.set_aspect('equal')
        #ax.set_xlabel('x')
        #ax.set_ylabel('y')
        #ax.legend()
        #plt.show()
    #endregion