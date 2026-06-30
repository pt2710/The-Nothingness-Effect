import numpy as np
from soi import SpectrumOfInfinities  # Make sure this class exists in your soi.py

class DFI:
    def __init__(self, soi_params=None):
        """
        Optionally accept parameters for the SpectrumOfInfinities class.
        """
        self.soi_params = soi_params if soi_params is not None else {}

    def compute_entropical_data(self, data, soi=None):
        """
        Compute entropic metrics for each column in 2D array/DataFrame.
        Uses a SpectrumOfInfinities instance for SOI logic.
        Handles bidirectional/symmetric SOI (tuple output) by using the positive branch by default.
        """
        ε = np.finfo(float).eps
        # Feature/column extraction
        if hasattr(data, "columns"):
            feature_list = data.columns
            data = data.values
        else:
            feature_list = list(range(data.shape[1]))

        xn = data.shape[1]

        # SOI calculation
        # Use argument if provided, else build new SOI instance from self.soi_params
        if soi is None:
            soi_instance = SpectrumOfInfinities(**self.soi_params)
            soi_value = soi_instance.get_value(xn)
        elif isinstance(soi, SpectrumOfInfinities):
            soi_value = soi.get_value(xn)
        else:
            soi_value = float(soi)

        # --- Handle possible tuple (bidirectional/symmetric SOI) ---
        if isinstance(soi_value, tuple):
            # By default, use only the positive branch (first element)
            # Optionally, you could compute analytics for both directions if needed
            soi_value = soi_value[0]

        V0 = soi_value / xn
        entropical_data = {}

        for idx, col in enumerate(feature_list):
            x_i = data[:, idx]
            x_n = data.sum(axis=1)
            x_r = x_n - x_i + ε  # Avoid div by zero

            sigma_x = (x_n * (xn - 1)) / (x_r * xn)
            V_x     = V0 * sigma_x
            S       = V_x - V0

            entropical_data[col] = {
                "Relative_Entropy": S,
                "Entropic_Weight":  sigma_x,
                "Relative_Volume":  V_x,
            }
        return entropical_data
