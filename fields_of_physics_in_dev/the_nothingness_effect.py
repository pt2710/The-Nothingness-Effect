"""
-- CURRENTLY IN DEVELOPMENT --

Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com

...
The Nothingness Effect: A Mathematical Framework for Infinity, Symmetry, and Duality

This script defines the "NothingnessEffect" class, which provides a comprehensive mathematical framework for exploring concepts of infinity, symmetry, and duality. The class serves as a central hub for accessing various mathematical models and operations related to these fundamental concepts.

Key Features:
1. Flowpoint (fp): The core element of "The Nothingness Effect", representing an oscillation between positive and negative functional-unit states.
2. Infinity Models: Implementations of countable infinity (countable_infinity) and uncountable infinity (uncountable_infinity).
3. Spectrum of Infinity: A blend of countable and uncountable infinity, normalized to a specified value.
4. Mathematical Constants: Approximation of pi using the Flowpoint function.
5. Trigonometry: Flowpoint-based trigonometric operations.
6. Observation and Collapse: Modeling of observation and collapse phenomena.
7. Dynamic Fluctuation: Calculation of dynamic fluctuation indices with "Dynamic Fluctuation Index Theorem" and application of the "Dynamic Fluctuation Theorem".
8. Symmetry, Duality, and Spatiality: Mathematical representations of these fundamental concepts.

The NothingnessEffect class provides a unified interface for accessing these mathematical models and operations, allowing for easy integration and exploration of these complex concepts in various scientific and philosophical contexts.

Usage:
    ne = NothingnessEffect()
    # Access various methods and models through the ne object
"""

import os
import warnings
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.flowpoint import fp
from the_nothingness_effect.foundational_architecture.symmetry.symmetry import symmetry_equation
from the_nothingness_effect.foundational_architecture.duality.duality import duality_equation
from the_nothingness_effect.foundational_architecture.spatiality.spatiality import spatiality_equation
from the_nothingness_effect.foundational_architecture.countable_infinity.countable_infinity import countable_infinity
from the_nothingness_effect.foundational_architecture.uncountable_infinity.uncountable_infinity import uncountable_infinity
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.spectrum_of_infinities import SpectrumOfInfinities
from the_nothingness_effect.foundational_architecture.observation_and_collapse.observation_and_collapse import observation_and_collapse
from the_nothingness_effect.mathematical_architecture.flowpoint_trigonometry.fp_trigonometry import FlowpointTrigonometry
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import DynamicFluctuationIndex
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import evaluate_elastic_pi
from the_nothingness_effect.mathematical_architecture.flowpoint_math_operations.fp_math_operations import FlowpointMath

class NothingnessEffect:
    def __init__(self):
        """
        Initialiserer NothingnessEffect klassen med standard spektral normalisering.

        """

    def fp(self, value):
        """
        Flowpoint (fp) Generator Function
        Implements the dynamic oscillatory behavior of the Flowpoint as defined by:

            fp = (f ≠ -f)^(f = -f)
        This function embodies the following key properties:

        Duality: Recognizes both the positive unit ( f ) and its inverse (-f).
        Symmetry: Ensures balanced coexistence between ( f ) and (-f).
        Oscillation: Alternates the state in each iteration, following:
                fp_{n+1} = -fp_n

        Dynamic Equilibrium: Maintains a stable, unbiased state over time.
        Idempotency & Neutrality: Guarantees that repeated applications yield consistent results.
        The generator supports inputs of type bool, int, float, or complex:

        For booleans, it toggles using logical negation.
        For numeric types, it toggles using arithmetic negation.
        Parameters
        f : bool, int, float, or complex
        The initial value for the Flowpoint. This value represents the positive unit, while its negation is the negative unit.

        Yields
        The current state of the Flowpoint, cast to the original type of f.

        The generator alternates between ( f ) and (-f ) indefinitely, preserving the dynamic equilibrium of the system.

        Implementation Details
        State Initialization:
        The input f is converted into a tuple state containing:

        For booleans: (f, not f)
        For numerics: (f, -f) (using the _neg function)
        Oscillatory Loop:
        An infinite loop generates the Flowpoint's behavior:

        XOR Logic:
        The variables positive_unit and negative_unit are computed using XOR logic to reflect the conditions ((f
        eq -f)) and ((f = -f)). This layered logical evaluation underpins

        the oscillatory behavior.

        Value Computation:
        The current value is computed as the product:

                value = state[0] * positive_unit * negative_unit
        This operation symbolically represents the toggling between the positive and negative states.

        Type Preservation:
        The computed value is cast back to the original type using _cast to maintain consistency.

        State Swap:
        The tuple state is swapped so that the next iteration toggles the state.

        Examples
        >>> gen = fp(5)
        >>> next(gen)
        5
        >>> next(gen)
        -5
        >>> next(gen)
        5
        >>> bool_gen = fp(True)
        >>> next(bool_gen)
        True
        >>> next(bool_gen)
        False
        Raises
        TypeError
        If the input f is not a supported type (bool, int, float, or complex).
        """
        return fp(value)

    def sym_eq(self, x):
        """
        Implements the symmetry equation: ±X = (x, -x) = ((x ≠ -x)^(x = -x) × (-x ≠ x)^(-x = x))

        This function calculates the symmetry of a given input by evaluating the logical conditions that define the symmetry equation. It returns a tuple containing the result for the input and its negative counterpart.

        Parameters
        x : int, float, or bool
        The input value for which the symmetry is to be calculated.

        Returns
        tuple
        A tuple containing the result for x and -x. For boolean inputs, it returns (x, not x). For integers, it returns (x, -x). For floats, it returns the calculated symmetry values.
        """
        return symmetry_equation(x)

    def dual_eq(self, y):
        """
        Implements the duality equation for Y: ±Y = (y, -y) = ((-y ≠ y)^(-y = y)) / ((y ≠ -y)^(y = -y))

        This function calculates the duality of a given input by evaluating the logical conditions that define the duality equation. It returns a tuple containing the result for the input and its negative counterpart.

        Parameters
        y : float
        The input value for which the duality is to be calculated.

        Returns
        tuple
        A tuple containing the result for y and -y. For boolean inputs, it returns (y, not y). For integers, it returns (y, -y). For floats, it returns the calculated duality values.
        """
        return duality_equation(y)
    
    def spa_eq(self, z):
        """
        Implements the spatiality equation for Z: ±Z = (z, -z) = ∛((z ≠ -z)^(z = -z) · (-z ≠ z)^(-z = z))

        Args
        z : float
        Input value

        Returns
        tuple
        A tuple containing the result for z and -z
        """
        return spatiality_equation(z)
    
    def countable_infinity(self, x, y, z):
        """Defines the countable infinity function."""
        return countable_infinity(x, y, z)

    def uncountable_infinity(self, x=1, y=1, z=1):
        """Defines the uncountable infinity function."""
        return uncountable_infinity(x, y, z)

    def soi(self, **soi_kwargs):
        """
        Compute the Spectrum of Infinities.

        Delegates to SpectrumOfInfinities.soi(), passing through any
        of normalize_to, adv_mode, type, test_mode, test_value, etc.

        Usage:
          ne = NothingnessEffect()
          ne.soi()                                    # default normalize_to=100
          ne.soi(normalize_to=150)                    # override normalization
          ne.soi(adv_mode=True, type="symmetric")     # advanced symmetric spectrum
        """
        engine = SpectrumOfInfinities(**soi_kwargs)
        return engine.soi()


    def dfi(self, data, soi=None, **soi_kwargs):
        """
        Compute the Dynamic Fluctuation Index on `data`.

        This delegates to the canonical typed DFI evaluator. Finite input
        returns a NormalizedDFIResult; a denominator obstruction returns the
        same type with an explicit singular status and no neutralized arrays.

        Usage:
          ne = NothingnessEffect()
          ne.dfi(df)                   # typed result with default SOI
          ne.dfi(df, soi=250)          # typed result with manual SOI
        """
        engine = DynamicFluctuationIndex()
        return engine.compute(data, soi=soi, **soi_kwargs)

    def legacy_dfi(self, data, soi=None, **soi_kwargs):
        """Return the historical per-feature dictionary with a deprecation warning."""
        warnings.warn(
            "legacy_dfi is a compatibility wrapper; use dfi for a typed fail-closed result",
            DeprecationWarning,
            stacklevel=2,
        )
        return DynamicFluctuationIndex(compatibility_mode=True).dfi(
            data, soi=soi, **soi_kwargs
        )

    def elastic_pi(self, entropy, *, K_D=1.0, x=None, exponent_clip=None):
        """Evaluate the typed Elastic-pi source law and retain diagnostics."""
        return evaluate_elastic_pi(
            entropy, K_D=K_D, x=x, exponent_clip=exponent_clip
        )


    def obs_n_col(self, *coordinates):
        """
        Implements the observation and collapse process in The Nothingness Effect.

        This function returns a nested function that combines countable and uncountable infinity through the flowpoint function, representing the observation and collapse process.

        Returns
        function
        A function that takes three arguments (x, y, z) and returns a tuple of two values.
        """
        operator = observation_and_collapse()
        if not coordinates:
            return operator
        if len(coordinates) != 3:
            raise TypeError("obs_n_col expects either no arguments or exactly x, y, z")
        return operator(*coordinates)

    def fp_trig(self):
        """
        Returns a FlowpointTrigonometry object for performing trigonometric operations.

        Returns:
            FlowpointTrigonometry: Object for Flowpoint-based trigonometric calculations.
        """
        return FlowpointTrigonometry()
    
    def fp_math(self):
        """
        Returns a FlowpointMath object for performing mathematical operations.

        Returns:
            FlowpointMath: Object for Flowpoint-based mathematical calculations.
        """
        return FlowpointMath()
