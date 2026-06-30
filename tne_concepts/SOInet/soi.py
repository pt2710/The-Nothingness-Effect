import numpy as np
from countable_infinity import countable_infinity
from uncountable_infinity import uncountable_infinity

class SpectrumOfInfinities:
    def __init__(self, normalize_to=1.0, adv_mode=False, type=None, test_mode=False, test_value=100):
        self.normalize_to = normalize_to
        self.countable_infinity = next(countable_infinity(x=1, y=1, z=1))
        self.uncountable_infinity = next(uncountable_infinity(x=1, y=1, z=1))
        self.adv_mode = adv_mode
        self.type = type
        self.test_mode = test_mode
        self.test_value = test_value

    def soi(self, normalize_to=None, adv_mode=None, type=None):
        # Use class defaults if not explicitly provided
        if normalize_to is None:
            normalize_to = self.normalize_to if self.normalize_to is not None else 100
        else:
            self.normalize_to = normalize_to

        if adv_mode is None:
            adv_mode = self.adv_mode
        else:
            self.adv_mode = adv_mode

        # Enforce type if adv_mode is True
        if adv_mode:
            if type is not None:
                self.type = type
            elif self.type is not None:
                type = self.type
            else:
                raise ValueError("Type must be specified when adv_mode is True")
        else:
            self.type = None
            type = None

        if self.test_mode:
            return self.test_value

        ci = np.real(np.atleast_1d(self.countable_infinity))
        ui = np.real(np.atleast_1d(self.uncountable_infinity))

        mask = ui <= 1
        if np.any(mask):
            if adv_mode:
                return normalize_to, -normalize_to
            else:
                return normalize_to

        ci = np.maximum(ci, 1e-10)
        ui = np.maximum(ui, 1e-10)

        try:
            spec_of_infinities = np.log(ci) / np.log(ui)
            spec_of_infinities = np.real(spec_of_infinities).item()
        except Exception as e:
            print(f"Error computing spec_of_infinities: {e}")
            spec_of_infinities = np.nan

        if adv_mode and type == 'symmetric':
            result_pos = spec_of_infinities * normalize_to
            result_neg = -spec_of_infinities * normalize_to
            return result_pos, result_neg
        else:
            return spec_of_infinities * normalize_to

    def get_value(self, n=None):
        # Always pass through the current class state for robust usage
        return self.soi(
            normalize_to=self.normalize_to,
            adv_mode=self.adv_mode,
            type=self.type
        )
