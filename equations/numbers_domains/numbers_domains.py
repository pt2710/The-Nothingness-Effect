"""
Author  : B. McCrackn
Email   : thenothingnesseffect@gmail.com
Usage   : from equations.mccrackns_prime_law.numbers_domains import NumbersDomains

NumbersDomains — Canonical motif domain handler for prime gaps.
Implements motif label encoding for deterministic prime law.
"""

class NumbersDomains:
    """
    Handles canonical motif calculation for prime gaps.

    Attributes:
        _cache (dict[int, str]): Motif label cache keyed by gap.
    """
    __slots__ = ("_cache",)
    _CACHE_LIMIT = 1 << 20

    def __init__(self):
        """
        Initialize empty motif cache.
        """
        self._cache: dict[int, str] = {}

    def canonical_motif(self, g: int, *, use_cache: bool = True) -> str:
        """
        Return canonical motif label for a given gap.

        Args:
            g (int): Prime gap.
            use_cache (bool): If True, enable cache for gaps <= _CACHE_LIMIT.

        Returns:
            str: Motif label ("U1", "E1.0", ...).

        Raises:
            ValueError: If gap is not 1 or an even integer of required form.
        """
        if g == 1:
            return "U1"
        if g & 1:
            raise ValueError("gap must be 1 or an even integer")
        if use_cache and g <= self._CACHE_LIMIT and g in self._cache:
            return self._cache[g]
        if g & (g - 1) == 0:
            x = (g.bit_length() - 1) - 1
            lbl = f"E1.{x}"
        else:
            k = (g & -g).bit_length() - 1
            odd = g >> k
            if odd < 3 or odd % 2 == 0:
                raise ValueError("gap does not fit 2^k·(2x+3) form")
            x = (odd - 3) // 2
            lbl = f"E{k+1}.{x}"
        if use_cache and g <= self._CACHE_LIMIT:
            self._cache[g] = lbl
        return lbl
