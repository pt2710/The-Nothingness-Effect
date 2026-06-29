"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...
"""

import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def symmetry_equation(x):
    """
    Implements the symmetry equation:
    ±X = (x, -x) = ((x ≠ -x)^(x = -x) × (-x ≠ x)^(-x = x))

    This function calculates the symmetry of a given input by evaluating
    the logical conditions that define the symmetry equation. It returns
    a tuple containing the result for the input and its negative counterpart.

    Parameters
    ----------
    x : int, float, or bool
        The input value for which the symmetry is to be calculated.

    Returns
    -------
    tuple
        A tuple containing the result for x and -x. For boolean inputs,
        it returns (x, not x). For integers, it returns (x, -x). For floats,
        it returns the calculated symmetry values.
    """
    # Convert the input to a float for consistent numerical operations
    x_float = float(x)

    # Calculate the first part of the symmetry equation using XOR
    part1 = (x_float != -x_float) ^ (x_float == -x_float)

    # Calculate the second part of the symmetry equation using XOR
    part2 = (-x_float != x_float) ^ (-x_float == x_float)

    # Compute the final result for the float input
    x_float = part1 * part2

    # Return results based on the type of input
    if isinstance(x, bool):
        # For boolean inputs, return the input and its negation
        return x, not x
    elif isinstance(x, int):
        # For integer inputs, return the input and its negative
        return x, -x
    else:
        # For float inputs, return the computed symmetry values
        return x_float, -x_float
