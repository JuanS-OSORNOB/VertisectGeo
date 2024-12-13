import pytest
from src.focal_mechanism import FocalMechanism
import matplotlib.pyplot as plt

def test_focal_mechanism():
    #Plane1
    strike1 = 95
    dip1 = 34
    rake1 = 300
    #Plane2
    strike2 = 208
    dip2 = 75
    rake2 = 59
    #Kinematic axes
    kinematic_axes = {'P':[321, 24], 'T':[83, 50], 'B':[217, 30]}
    
    focal_mechanism = FocalMechanism(strike1, dip1, rake1, strike2, dip2, rake2, kinematic_axes)
    vec_dict = focal_mechanism.create_vector_dict1()
    print(vec_dict)
    #Plot figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    focal_mechanism.plot_focal_mechanism_3d(ax)
    plt.show()

test_focal_mechanism()