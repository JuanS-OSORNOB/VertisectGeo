import pytest
from src.focal_mechanism import FocalMechanism

def test_focal_mechanism():
    strike = 95
    dip = 34
    rake = 153
    kinematic_axes = {'P':[321, 24], 'T':[83, 50], 'B':[217, 30]}
    focal_mechanism = FocalMechanism(strike, dip, rake, kinematic_axes)
    vec_dict = focal_mechanism.create_vector_dict()
    print(vec_dict)

test_focal_mechanism()