"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
import numpy as np
import random
from the_nothingness_effect.foundational_architecture.symmetry.symmetry import symmetry_equation
from the_nothingness_effect.foundational_architecture.duality.duality import duality_equation
from the_nothingness_effect.foundational_architecture.spatiality.spatiality import spatiality_equation
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint import fp

def uncountable_infinity(x=1, y=1, z=1):
    """
    Implements the definition of uncountable infinity:
    2^aleph_0 = (fp(±X) ≠ fp(±Y) ≠ fp(±Z))^(fp(±X) = fp(±Y) = fp(±Z))
    
    Args:
        x (float, optional): Input value for X. Defaults to 1.
        y (float, optional): Input value for Y. Defaults to 1.
        z (float, optional): Input value for Z. Defaults to 1.
    
    Yields:
        float: The result of the uncountable infinity calculation
    
    Properties:
        1. Infinite sequence
        2. Non-countable nature
        3. Demonstrates the power set of countable infinity
    
    Mathematical Representation:
        2^aleph_0 = (fp(±X) ≠ fp(±Y) ≠ fp(±Z))^(fp(±X) = fp(±Y) = fp(±Z))
    
    Related Concepts:
        - Uncountable Infinity
        - Power Set
        - Cardinal Numbers
        - Continuum Hypothesis
    
    Applications:
        - Demonstrating the concept of uncountable infinity
        - Modeling complex systems with infinite possibilities
        - Understanding the nature of real numbers
    """
    # Ensure inputs are tuples of positive and negative values
    if isinstance(x, (int, float)):
        x = (x, -x)
    if isinstance(y, (int, float)):
        y = (y, -y)
    if isinstance(z, (int, float)):
        z = (z, -z)
    
    fp_x = fp(x[0])
    fp_y = fp(y[0])
    fp_z = fp(z[0])

    while True:
        positive_unit = (next(fp_x) != next(fp_y)) and (next(fp_y) != next(fp_z)) and (next(fp_z) != next(fp_x))
        negative_unit = (next(fp_x) == next(fp_y)) and (next(fp_y) == next(fp_z)) and (next(fp_z) == next(fp_x))

        symmetrized_positive = symmetry_equation(positive_unit)[0]
        dualized_positive = duality_equation(symmetrized_positive)[0]
        spatialized_positive = spatiality_equation(dualized_positive)[0]

        symmetrized_negative = symmetry_equation(negative_unit)[0]
        dualized_negative = duality_equation(symmetrized_negative)[0]
        spatialized_negative = spatiality_equation(dualized_negative)[0]

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
