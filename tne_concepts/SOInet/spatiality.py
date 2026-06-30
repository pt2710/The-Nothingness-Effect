import os
import sys
import numpy as np

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def spatiality(z):
    
    z_val = np.real(z)

    z_float = float(z_val)

    part1 = (z_float != -z_float) ^ (z_float == -z_float)
    part2 = (-z_float != z_float) ^ (-z_float == z_float)

    z_res = np.cbrt(part1 * part2)
    
    if isinstance(z, bool):
        return z, not z
    elif isinstance(z, int):
        return z, -z
    else:
        return z_res, -z_res


        
