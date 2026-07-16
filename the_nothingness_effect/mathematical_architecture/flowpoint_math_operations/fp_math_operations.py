"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

fp_math_operations.py

This module implements a suite of mathematical operations using the Flowpoint function (\(fp\)).
The Flowpoint function embodies dynamic equilibrium and idempotence, meaning that for any input \(a\),
the property \(fp(a) = fp(-a)\) holds. This property is central to the derivation of various operations,
which can be summarized by the following equations:

    Addition:
        fp(a + b) = fp(a) + fp(b)
    Subtraction:
        fp(a - b) = fp(a) - fp(b)
    Multiplication:
        fp(a * b) = fp(a) * fp(b)
    Division:
        fp(a / b) = fp(a) / fp(b)
    Exponentiation:
        fp(a^n) = (fp(a))^n
    Square Root:
        fp(sqrt(a)) = sqrt(fp(a))
    Trigonometric Functions:
        fp(sin(a)) = sin(fp(a))
        fp(cos(a)) = cos(fp(a))
        fp(tan(a)) = tan(fp(a))

These operations derive from the concept of dynamic equilibrium and symmetry in the Flowpoint function.
Each method in the FlowpointMath class retrieves an oscillatory value for a given input and then applies the
corresponding mathematical function, ensuring consistency with the theoretical framework.

Dependencies:
    - os
    - sys
    - math
    - fp

Classes:
    - FlowpointMath

Usage:
    Ensure that the 'flowpoint.py' script is accessible at the specified path.
    Instantiate the FlowpointMath class and use its methods to compute values.
    Example:
        fp_math = FlowpointMath()
        result = fp_math.fp_addition(3, 5)
"""

import os
import math

# Set up the parent directory so that the 'flowpoint' module is accessible.
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint import fp

class FlowpointMath:
    def __init__(self):
        """
        Initializes the FlowpointMath class.

        This constructor sets up a dictionary of generators, one for each unique input value.
        These generators provide oscillatory Flowpoint values that embody the dynamic equilibrium
        (i.e. the idempotent nature: fp(a) = fp(-a)) required by the theoretical framework.
        """
        self.generators = {}

    def fp_value(self, f):
        """
        Retrieves the next value in the oscillatory sequence for a given input f.

        In the context of Flowpoint theory, each input \(f\) has an associated oscillatory
        generator that produces values reflecting the equilibrium state. This method ensures
        that the same generator is reused for identical inputs, preserving the idempotent property.

        Parameters:
            - f (float): The input value for which the Flowpoint is to be computed.

        Returns:
            - float: The next oscillatory value for \(f\), representing fp(f).
        """
        if f not in self.generators:
            self.generators[f] = fp(f)
        return next(self.generators[f])

    def fp_addition(self, a, b):
        """
        Models addition using the Flowpoint function.

        Based on the theoretical derivation:
            fp(a + b) = fp(a) + fp(b)
        This method computes the Flowpoint values for \(a\) and \(b\) individually, then sums them,
        reflecting the cumulative nature of addition within an equilibrated system.

        Parameters:
            - a (float): The first operand.
            - b (float): The second operand.

        Returns:
            - float: The result of adding the Flowpoint values of \(a\) and \(b\).
        """
        fp_a = self.fp_value(a)
        fp_b = self.fp_value(b)
        return fp_a + fp_b

    def fp_subtraction(self, a, b):
        """
        Models subtraction using the Flowpoint function.

        The derivation is given by:
            fp(a - b) = fp(a) - fp(b)
        This reflects the relative equilibrium between \(a\) and \(b\). The method computes the Flowpoint
        for both operands and subtracts the second from the first.

        Parameters:
            - a (float): The minuend.
            - b (float): The subtrahend.

        Returns:
            - float: The difference between the Flowpoint values of \(a\) and \(b\).
        """
        fp_a = self.fp_value(a)
        fp_b = self.fp_value(b)
        return fp_a - fp_b

    def fp_multiplication(self, a, b):
        """
        Models multiplication using the Flowpoint function.

        In accordance with:
            fp(a * b) = fp(a) * fp(b)
        the multiplication of two Flowpoint values reflects the compounded equilibrium of the operands.
        This method computes the product of the individual Flowpoint values.

        Parameters:
            - a (float): The first operand.
            - b (float): The second operand.

        Returns:
            - float: The product of fp(a) and fp(b).
        """
        fp_a = self.fp_value(a)
        fp_b = self.fp_value(b)
        return fp_a * fp_b

    def fp_division(self, a, b):
        """
        Models division using the Flowpoint function.

        The theoretical derivation is:
            fp(a / b) = fp(a) / fp(b)
        This method computes the Flowpoint values for \(a\) and \(b\), with a subtle inversion in the
        arguments to respect the equilibrium (using \(-a\) and \(-b\)). Division by zero is checked
        based on the Flowpoint result for \(b\).

        Parameters:
            - a (float): The numerator.
            - b (float): The denominator.

        Returns:
            - float: The quotient of fp(a) divided by fp(b).

        Raises:
            - ZeroDivisionError: If the Flowpoint value for \(b\) is zero.
        """
        fp_a = self.fp_value(-a)
        fp_b = self.fp_value(-b)
        if fp_b == 0:
            raise ZeroDivisionError("Division by zero encountered in fp_division.")
        return fp_a / fp_b

    def fp_exponentiation(self, a, n):
        """
        Models exponentiation using the Flowpoint function.

        The relationship:
            fp(a^n) = (fp(a))^n
        illustrates that raising \(a\) to the power \(n\) corresponds to raising the Flowpoint of \(a\)
        to \(n\). This method applies the exponentiation to the Flowpoint value of \(a\).

        Parameters:
            - a (float): The base.
            - n (float): The exponent.

        Returns:
            - float: The result of (fp(a))^n.
        """
        fp_a = self.fp_value(a)
        return fp_a ** n

    def fp_square_root(self, a):
        """
        Models the square root operation using the Flowpoint function.

        The derivation:
            fp(sqrt(a)) = sqrt(fp(a))
        signifies that the square root of \(a\) is computed after obtaining its Flowpoint value.
        This method ensures that if the Flowpoint value is negative, a ValueError is raised,
        preserving the mathematical validity of the square root operation.

        Parameters:
            - a (float): The input value.

        Returns:
            - float: The square root of fp(a).

        Raises:
            - ValueError: If fp(a) is negative.
        """
        fp_a = self.fp_value(a)
        if fp_a < 0:
            raise ValueError("Cannot compute square root of negative number in fp_square_root.")
        return math.sqrt(fp_a)

    def fp_sin(self, a):
        """
        Models the sine function using the Flowpoint function.

        The derivation:
            fp(sin(a)) = sin(fp(a))
        indicates that the sine of an angle is computed by first obtaining its Flowpoint value.
        This method applies the standard sine function to the Flowpoint value of the input angle,
        thereby capturing the oscillatory nature of trigonometric functions in equilibrium.

        Parameters:
            - a (float): The input angle in radians.

        Returns:
            - float: The sine of fp(a).
        """
        return math.sin(self.fp_value(a))

    def fp_cos(self, a):
        """
        Models the cosine function using the Flowpoint function.

        Following the derivation:
            fp(cos(a)) = cos(fp(a))
        the method computes the cosine by first determining the Flowpoint value of the input angle.
        This reflects the symmetry and periodicity intrinsic to cosine within an equilibrated system.

        Parameters:
            - a (float): The input angle in radians.

        Returns:
            - float: The cosine of fp(a).
        """
        return math.cos(self.fp_value(a))

    def fp_tan(self, a):
        """
        Models the tangent function using the Flowpoint function.

        As derived:
            fp(tan(a)) = tan(fp(a))
        the tangent is computed by applying the standard tangent function to the Flowpoint of \(a\).
        This preserves the oscillatory and equilibrium properties of the tangent function as defined by
        the idempotence \(fp(a) = fp(-a)\).

        Parameters:
            - a (float): The input angle in radians.

        Returns:
            - float: The tangent of fp(a).
        """
        return math.tan(self.fp_value(a))

