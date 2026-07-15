"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Creates the spectrum of infinities by combining countable and uncountable infinity,
and normalizes the spectrum to the specified value (e.g., 100, representing 100%).
This is made possible by the Lebesgue principle ([0, 1]), which manages infinite measures.

Args:
    countable_infinity (float): Result of countable_infinity calculation (countable infinity).
    uncountable_infinity (float): Result of uncountable_infinity calculation (uncountable infinity).
    normalize_to (float, optional): Normalization value. Defaults to 100.

Attributes:
    normalize_to (float): Normalization value for the spectrum.
    countable_infinity (numpy.array): Result of countable_infinity calculation.
    uncountable_infinity (numpy.array): Result of uncountable_infinity calculation.
    adv_mode (bool): Flag for advanced mode. Defaults to False.
    type (str): Type of spectrum in advanced mode. Can be 'symmetric' or 'dualistic'.
    normalize_to_neg (float): Normalization value for negative spectrum in dualistic mode.

Methods:
    soi: Calculates the spectrum of infinities.
"""

import numpy as np
from the_nothingness_effect.foundational_architecture.countable_infinity.countable_infinity import countable_infinity
from the_nothingness_effect.foundational_architecture.uncountable_infinity.uncountable_infinity import uncountable_infinity

class SpectrumOfInfinities:
    def __init__(self, normalize_to=100, adv_mode=False, type=None, test_mode=False, test_value=100):
        """
        Initializes the SpectrumOfInfinities class.

        Args:
            normalize_to (float, optional): Normalization value. Defaults to 100.
            test_mode (bool, optional): If True, soi() will return test_value. Defaults to False.
            test_value (float, optional): Value to return when in test_mode. Defaults to 100.
        """
        self.normalize_to = normalize_to

        self.countable_infinity = next(countable_infinity(x=1, y=1, z=1))
        self.uncountable_infinity = next(uncountable_infinity(x=1, y=1, z=1))
        
        self.adv_mode = adv_mode
        self.type = type
        self.test_mode = test_mode
        self.test_value = test_value

    def soi(self, normalize_to=None, adv_mode=None, type=None):
        """
        Calculates the Spectrum of Infinities.

        Optional Parameters:
            normalize_to (float, optional): Normalization value. If not provided, defaults to the instance's 
                                            value or 100 if not set.
            adv_mode (bool, optional): Flag for advanced mode. If not provided, defaults to the instance's setting.
            type (str, optional): Type for advanced mode. Must be provided if adv_mode is True (e.g., 'symmetric').

        Returns:
            float or tuple: The calculated spectrum of infinities. In advanced symmetric mode, returns a tuple
                            (positive, negative) values.
        """
        # Use the provided normalize_to value or default to the instance's setting (or 100)
        if normalize_to is None:
            normalize_to = self.normalize_to if self.normalize_to is not None else 100
        else:
            self.normalize_to = normalize_to

        # Use provided adv_mode or the instance's setting (default is False)
        if adv_mode is None:
            adv_mode = self.adv_mode
        else:
            self.adv_mode = adv_mode

        # If advanced mode is enabled, ensure a type is provided
        if adv_mode:
            if type is not None:
                self.type = type
            else:
                raise ValueError("Type must be specified when adv_mode is True")
        else:
            self.type = None

        # If test_mode is enabled, return the test_value immediately
        if self.test_mode:
            return self.test_value

        # Convert countable and uncountable infinity to arrays of real numbers
        ci = np.real(np.atleast_1d(self.countable_infinity))
        ui = np.real(np.atleast_1d(self.uncountable_infinity))

        # Check that the base for logarithm is greater than 1
        mask = ui <= 1
        if np.any(mask):
            if adv_mode:
                return normalize_to, -normalize_to
            else:
                return normalize_to

        # Avoid issues with log of zero by ensuring minimum values
        ci = np.maximum(ci, 1e-10)
        ui = np.maximum(ui, 1e-10)
        
        try:
            spec_of_infinities = np.log(ci) / np.log(ui)
            spec_of_infinities = np.real(spec_of_infinities).item()
        except Exception as e:
            print(f"Error computing spec_of_infinities: {e}")
            spec_of_infinities = np.nan

        if adv_mode and self.type == 'symmetric':
            result_pos = spec_of_infinities * normalize_to
            result_neg = -spec_of_infinities * normalize_to
            return result_pos, result_neg
        else:
            return spec_of_infinities * normalize_to


