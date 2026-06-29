"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Pi Modeling Script

This script approximates Pi using The Nothingness Effect framework and existing Flowpoint-based trigonometric functions.
The method employs a series expansion derived from the Leibniz formula for Pi and enhances its performance using the imported `flowpoint` function.

Equation Name: Leibniz Formula for Pi

This script extends the standard series computation by integrating the Flowpoint (fp) function to optimize the computation and provide an efficient approximation of Pi.
"""
import os
import sys
import math

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from flowpoint import fp

def fp_pi(max_iterations):
    """
    Approximate Pi using the Leibniz formula and the Flowpoint (fp) function.

    Args:
        max_iterations (int): The maximum number of iterations for the series expansion.

    Returns:
        float: The approximation of Pi after the specified number of iterations.

    Detailed Explanation:
        The function uses the Leibniz formula for Pi, which is a simple alternating series:

            \[ \pi = 4 \sum_{k=0}^{\infty} \frac{(-1)^k}{2k+1} \]

        Each term of the series is computed using:
            - Numerator: \((-1)^k\) alternates between 1 and -1 for successive terms.
            - Denominator: \(2k + 1\) generates the odd numbers for the series.

        To improve performance, the function integrates the Flowpoint (fp) function, which provides optimized handling of series terms.

        The function stops iterating early if the approximation of Pi reaches a precision threshold (default: \(10^{-5}\)) after 1,000,000 iterations.

    """
    # Initialize the approximation of Pi
    pi_approx = 0.0

    # Loop over the series for the specified number of iterations
    for k in range(max_iterations):
        # Calculate the numerator using the Flowpoint function and the alternating series formula
        numerator = next(fp((-1) ** k))

        # Calculate the denominator (2k + 1 for odd numbers)
        denominator = 2 * k + 1

        # Compute the term of the series
        term = numerator / denominator

        # Add the term to the Pi approximation
        pi_approx += term

        # Early stopping condition for performance optimization
        if k > 1000000 and abs((4 * pi_approx) - math.pi) < 1e-5:
            break

    # Multiply by 4 as per the Leibniz formula to get the final approximation of Pi
    return 4 * pi_approx
