"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Flowpoint Module
----------------

This module implements the Flowpoint (fp) function as defined in the framework of *The Nothingness Effect*.
The Flowpoint encapsulates the dynamic oscillation between a positive state \( f \) and its negative counterpart \(-f\),
thereby mediating a state of dynamic equilibrium. Its mathematical definition is given by:

\[
fp = (f \neq -f)^{(f = -f)}
\]

This expression captures the inherent duality and symmetry of the system:
  - **Duality:** The function recognizes both the state \( f \) and its inverse \(-f\).
  - **Symmetry:** The balanced coexistence of these opposing states ensures neutrality.
  - **Oscillation:** The system alternates between \( f \) and \(-f\) according to the recursive relation:
    
    \[
    fp_{n+1} = -fp_n
    \]

The Flowpoint thereby maintains a dynamic equilibrium by continuously toggling between its two states.
It supports booleans, integers, floats, and complex numbers, applying:
  - Logical negation for booleans.
  - Arithmetic negation for numerical types.

**GitHub Link to Flowpoint Implementation:**  
\href{https://github.com/YourUsername/YourRepository/blob/main/flowpoint.py}{\texttt{flowpoint.py}}

For a comprehensive explanation of the underlying theory, please refer to the accompanying documentation.
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def _neg(value):
    """
    Negates a value while preserving its type.
    
    For boolean values, the logical negation is applied.
    For numerical types (int, float, complex), the arithmetic negation is used.
    
    Parameters
    ----------
    value : bool, int, float, or complex
        The value to negate.
    
    Returns
    -------
    bool, int, float, or complex
        The negated value.
    """
    if isinstance(value, bool):
        return not value
    else:
        return -value

def _cast(value, orig_type):
    """
    Casts a value back to its original type.
    
    This function ensures that the output of operations remains consistent with the input type.
    For booleans, nonzero values become True and zero becomes False.
    For numerical types, the value is cast using the original type.
    
    Parameters
    ----------
    value : any
        The value to cast.
    orig_type : type
        The original type of the value.
    
    Returns
    -------
    The value cast to `orig_type`.
    """
    if orig_type == bool:
        return bool(value)
    else:
        return orig_type(value)

def fp(f):
    """
    Flowpoint (fp) Generator Function
    -------------------------------------------
    
    Implements the dynamic oscillatory behavior of the Flowpoint as defined by:
    
        fp = (f ≠ -f)^(f = -f)
    
    This function embodies the following key properties:
      - **Duality:** Recognizes both the positive unit \( f \) and its inverse \(-f\).
      - **Symmetry:** Ensures balanced coexistence between \( f \) and \(-f\).
      - **Oscillation:** Alternates the state in each iteration, following:
        
            fp_{n+1} = -fp_n
        
      - **Dynamic Equilibrium:** Maintains a stable, unbiased state over time.
      - **Idempotency & Neutrality:** Guarantees that repeated applications yield consistent results.
    
    The generator supports inputs of type bool, int, float, or complex:
      - For booleans, it toggles using logical negation.
      - For numeric types, it toggles using arithmetic negation.
    
    Parameters
    ----------
    f : bool, int, float, or complex
        The initial value for the Flowpoint. This value represents the positive unit,
        while its negation is the negative unit.
    
    Yields
    ------
    The current state of the Flowpoint, cast to the original type of `f`.
    
    The generator alternates between \( f \) and \(-f \) indefinitely, preserving the dynamic equilibrium
    of the system.
    
    Implementation Details
    ----------------------
    1. **State Initialization:**  
       The input `f` is converted into a tuple `state` containing:
         - For booleans: `(f, not f)`
         - For numerics: `(f, -f)` (using the `_neg` function)
         
    2. **Oscillatory Loop:**  
       An infinite loop generates the Flowpoint's behavior:
         - **XOR Logic:**  
           The variables `positive_unit` and `negative_unit` are computed using XOR logic to reflect
           the conditions \((f \neq -f)\) and \((f = -f)\). This layered logical evaluation underpins
           the oscillatory behavior.
         - **Value Computation:**  
           The current value is computed as the product:
           
               value = state[0] * positive_unit * negative_unit
               
           This operation symbolically represents the toggling between the positive and negative states.
         - **Type Preservation:**  
           The computed value is cast back to the original type using `_cast` to maintain consistency.
         - **State Swap:**  
           The tuple `state` is swapped so that the next iteration toggles the state.
    
    Examples
    --------
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
    ------
    TypeError
        If the input `f` is not a supported type (bool, int, float, or complex).
    """
 
    if isinstance(f, bool):
        state = (f, not f)
    elif isinstance(f, (int, float, complex)):
        state = (f, _neg(f))
    else:

        raise TypeError(f"Unsupported type for flowpoint: {type(f)}")


    orig_type = type(f)

    while True:

        positive_unit = (state[1] != _neg(state[0])) ^ (state[1] == _neg(state[0]))
        negative_unit = (_neg(state[0]) != state[1]) ^ (_neg(state[0]) == state[1])

       
        val = state[0] * positive_unit * negative_unit

        yield _cast(val, orig_type)

        state = (state[1], state[0])

