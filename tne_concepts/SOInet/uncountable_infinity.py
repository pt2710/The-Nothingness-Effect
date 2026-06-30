import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import numpy as np
import random
from symmetry import symmetry
from duality import duality
from spatiality import spatiality

from flowpoint import Flowpoint

def uncountable_infinity(x=1, y=1, z=1):

    if isinstance(x, (int, float)):
        x = (x, -x)
    if isinstance(y, (int, float)):
        y = (y, -y)
    if isinstance(z, (int, float)):
        z = (z, -z)
    
    Flowpoint_x = Flowpoint(x[0])
    Flowpoint_y = Flowpoint(y[0])
    Flowpoint_z = Flowpoint(z[0])

    while True:
        positive_unit = (next(Flowpoint_x) != next(Flowpoint_y)) and (next(Flowpoint_y) != next(Flowpoint_z)) and (next(Flowpoint_z) != next(Flowpoint_x))
        negative_unit = (next(Flowpoint_x) == next(Flowpoint_y)) and (next(Flowpoint_y) == next(Flowpoint_z)) and (next(Flowpoint_z) == next(Flowpoint_x))

        symmetrized_positive = symmetry(positive_unit)[0]
        dualized_positive = duality(symmetrized_positive)[0]
        spatialized_positive = spatiality(dualized_positive)[0]

        symmetrized_negative = symmetry(negative_unit)[0]
        dualized_negative = duality(symmetrized_negative)[0]
        spatialized_negative = spatiality(dualized_negative)[0]

        spatialized_positive = random.uniform(-1.0, 1.0)
        spatialized_negative = random.uniform(-1.0, 1.0)

        result = spatialized_positive ** spatialized_negative

        if result == 0.0:
            result = random.choice([-1.0, 1.0])
        elif abs(result) < 1e-10:
            result = random.uniform(-1e-10, 1e-10)

        yield result
        

        x = (x[1], x[0])
        y = (y[1], y[0])
        z = (z[1], z[0])
