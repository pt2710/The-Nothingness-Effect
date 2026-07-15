"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
equations_dir = os.path.join(parent_dir, 'equations')
sys.path.insert(0, equations_dir)

from the_nothingness_effect.foundational_architecture.symmetry.symmetry import symmetry_equation
from the_nothingness_effect.foundational_architecture.duality.duality import duality_equation
from the_nothingness_effect.foundational_architecture.spatiality.spatiality import spatiality_equation

def countable_infinity(x, y, z):
    """
    Generator that yields the countable infinity value based on x, y, and z.

    Parameters
    ----------
    x, y, z : float
        Input numerical values. They will be converted to (value, -value) tuples.

    Yields
    ------
    int
        The computed countable infinity value.
    """
    # Validate inputs
    if x is None or y is None or z is None:
        raise ValueError(f"Invalid input: x={x}, y={y}, z={z}. None values are not allowed.")
    
    # Convert numbers to tuples (positive, negative) if necessary
    if isinstance(x, (int, float)):
        x = (x, -x)
    if isinstance(y, (int, float)):
        y = (y, -y)
    if isinstance(z, (int, float)):
        z = (z, -z)
    
    while True:
        sym = symmetry_equation(x[0])
        dual = duality_equation(y[0])
        spatial = spatiality_equation(z[0])
        
        positive_unit = (sym[0] != dual[0]) and (dual[0] != spatial[0]) and (spatial[0] != sym[0])
        negative_unit = (sym[0] == dual[0]) and (dual[0] == spatial[0]) and (spatial[0] == sym[0])
        
        # The '^' operator is a bitwise XOR. (positive_unit ^ negative_unit) will be 1 if exactly one is True.
        result = (x[0] * y[0] * z[0]) * (positive_unit ^ negative_unit)
        
        yield int(round(result))
        
        # Swap positive and negative states for the next iteration
        x = (x[1], x[0])
        y = (y[1], y[0])
        z = (z[1], z[0])
