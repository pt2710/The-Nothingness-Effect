import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def symmetry(x):
    x_float = float(x)

    part1 = (x_float != -x_float) ^ (x_float == -x_float)

    part2 = (-x_float != x_float) ^ (-x_float == x_float)

    x_float = part1 * part2

    if isinstance(x, bool):
        return x, not x
    elif isinstance(x, int):
        return x, -x
    else:
        return x_float, -x_float
