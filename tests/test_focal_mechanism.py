import pytest
from src.focal_mechanism import FocalMechanism
import matplotlib.pyplot as plt

def test_focal_mechanism():
    #Plane1
    strike1 = 36
    dip1 = 70
    rake1 = 82
    #Plane2
    strike2 = 237
    dip2 = 22
    rake2 = 110
    #Kinematic axes
    kinematic_axes = {'P':[132, 25], 'T':[293, 64], 'B':[39, 8]}
    
    focal_mechanism = FocalMechanism(strike1, dip1, rake1, strike2, dip2, rake2, kinematic_axes)
    vec_dict = focal_mechanism.create_vector_dict1()
    print(vec_dict)
    #Plot figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    focal_mechanism.plot_focal_mechanism_3d(ax)
    plt.show()

test_focal_mechanism()