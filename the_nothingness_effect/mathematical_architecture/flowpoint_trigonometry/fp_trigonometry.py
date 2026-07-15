"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import os
import sys
import math

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint import fp
from the_nothingness_effect.mathematical_architecture.flowpoint_pi_approximation.fp_pi_approximation import fp_pi

class FlowpointTrigonometry:
    """
    A class that implements trigonometric functions using the Flowpoint function.

    This class uses the Flowpoint function to model cos(θ), sin(θ), and tan(θ).
    It also encapsulates the logic for generating oscillatory values.

    Attributes:
        generators (dict): A dictionary to keep track of generators for different input values

    Methods:
        fp_value(f): Generates oscillatory values for input f
        fp_cos(x, h): Models cos(θ) using the Flowpoint function
        fp_sin(y, h): Models sin(θ) using the Flowpoint function
        fp_tan(y, x): Models tan(θ) using the Flowpoint function
        cos(theta): Calculates cosine using Flowpoint-based methods
        sin(theta): Calculates sine using Flowpoint-based methods
        tan(theta): Calculates tangent using Flowpoint-based methods
    """

    def __init__(self, smoothing_window=10):
        """
        Initializes the FlowpointTrigonometry class.

        Creates an empty dictionary to keep track of generators for different input values.
        """
        self.generators = {}
        self.smoothing_window = smoothing_window

    def fp_value(self, f):
        """
        Generates oscillatory values for input f using the Flowpoint function.

        Args:
            f (float): Input value for the Flowpoint function

        Returns:
            float: The next value in the oscillation for input f
        """
        gen = fp(f)
        return next(gen)

    def fp_cos(self, x, h):
        """
        Models cos(θ) using the Flowpoint function.

        Args:
            x (float): The adjacent side in a right-angled triangle
            h (float): The hypotenuse in a right-angled triangle

        Returns:
            float: The Flowpoint-based value of cos(θ)
        """
        return self.fp_value(x) / self.fp_value(h)

    def fp_sin(self, y, h):
        """
        Models sin(θ) using the Flowpoint function.

        Args:
            y (float): The opposite side in a right-angled triangle
            h (float): The hypotenuse in a right-angled triangle

        Returns:
            float: The Flowpoint-based value of sin(θ)
        """
        return self.fp_value(y) / self.fp_value(h)

    def fp_tan(self, y, x):
        """
        Models tan(θ) using the Flowpoint function.

        Args:
            y (float): The opposite side in a right-angled triangle
            x (float): The adjacent side in a right-angled triangle

        Returns:
            float: The Flowpoint-based value of tan(θ)
        """
        return self.fp_value(y) / self.fp_value(x)

    def cos(self, theta):
        """
        Calculates cosine using Flowpoint-based methods.

        Args:
            theta (float): Angle in radians.

        Returns:
            float: Approximated cosine value.
        """
        h = 1.0  # Hypotenuse
        x = math.cos(theta) * h  # Adjacent side
        return self.fp_cos(x, h)

    def sin(self, theta):
        """
        Calculates sine using Flowpoint-based methods.

        Args:
            theta (float): Angle in radians.

        Returns:
            float: Approximated sine value.
        """
        h = 1.0 
        y = math.sin(theta) * h 
        return self.fp_sin(y, h)

    def tan(self, theta):
        """
        Calculates tangent using Flowpoint-based methods.

        Args:
            theta (float): Angle in radians.

        Returns:
            float: Approximated tangent value.
        """
        x = math.cos(theta)
        y = math.sin(theta)
        return self.fp_tan(y, x)

    def cos_sin(self, theta):
        """
        Calculates the sum of cosine and sine using Flowpoint-based methods.

        Args:
            theta (float): Angle in radians.

        Returns:
            float: Sum of cosine and sine values, constrained to [-2, 2].
        """
        cos_val = self.cos(theta)
        sin_val = self.sin(theta)
        return max(-2, min(2, cos_val + sin_val)) 

    def pi(self, precision=1e-4, max_iterations=100000):
        """
        Calculate an approximation of pi using the Flowpoint function.

        Args:
            precision (float): Desired precision for the approximation.
            max_iterations (int): Maximum number of iterations.

        Returns:
            float: An approximation of pi.
        """
        return fp_pi(max_iterations)

    def pi_value(self):
        """Return the approximated value of π."""
        return self.pi()
