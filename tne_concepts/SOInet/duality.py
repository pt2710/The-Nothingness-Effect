import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def duality(y):

    y_float = float(y)

    denominator = (-y_float != y_float) ^ (-y_float == y_float)

    numerator = (y_float != -y_float) ^ (y_float == -y_float)

    if denominator == 0:
        y_float = 0
    else:
        y_float = numerator / denominator

    if isinstance(y, bool):
        return y, not y
    elif isinstance(y, int):
        return y, -y
    else:
        return y_float, -y_float