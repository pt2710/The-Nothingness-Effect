"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""

import os
import numpy as np

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def spatiality_equation(z):
    """
    Implements the spatiality equation for Z:
    ±Z = (z, -z) = ∛((z ≠ -z)^(z = -z) · (-z ≠ z)^(-z = z))
    
    Args:
        z (float or complex): Input value
    
    Returns:
        tuple: A tuple containing the result for z and -z
    """
    # if a complex was passed in, drop its imaginary part
    z_val = np.real(z)

    # now safe to cast
    z_float = float(z_val)

    part1 = (z_float != -z_float) ^ (z_float == -z_float)
    part2 = (-z_float != z_float) ^ (-z_float == z_float)
    
    # cube‐root of the product
    z_res = np.cbrt(part1 * part2)
    
    if isinstance(z, bool):
        return z, not z
    elif isinstance(z, int):
        return z, -z
    else:
        # now always real
        return z_res, -z_res


        
