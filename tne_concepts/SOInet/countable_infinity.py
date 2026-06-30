import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
equations_dir = os.path.join(parent_dir, 'equations')
sys.path.insert(0, equations_dir)

from symmetry import symmetry
from duality import duality
from spatiality import spatiality

def countable_infinity(x, y, z):
    if x is None or y is None or z is None:
        raise ValueError(f"Invalid input: x={x}, y={y}, z={z}. None values are not allowed.")
    
    if isinstance(x, (int, float)):
        x = (x, -x)
    if isinstance(y, (int, float)):
        y = (y, -y)
    if isinstance(z, (int, float)):
        z = (z, -z)
    
    while True:
        sym = symmetry(x[0])
        dual = duality(y[0])
        spatial = spatiality(z[0])
        
        positive_unit = (sym[0] != dual[0]) and (dual[0] != spatial[0]) and (spatial[0] != sym[0])
        negative_unit = (sym[0] == dual[0]) and (dual[0] == spatial[0]) and (spatial[0] == sym[0])
        
        result = (x[0] * y[0] * z[0]) * (positive_unit ^ negative_unit)
        
        yield int(round(result))
        
        x = (x[1], x[0])
        y = (y[1], y[0])
        z = (z[1], z[0])
