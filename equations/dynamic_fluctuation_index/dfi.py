import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import numpy as np
from equations.spectrum_of_infinities.spectrum_of_infinities import SpectrumOfInfinities


class DynamicFluctuationIndex:
    """
    DynamicFluctuationIndex computes the parity-based entropic features (DFI) of a dataset.

    You can also invoke the CLI for full options:
        $ python dfi.py --help

    Args:
      soi_params (dict, optional):
        Default kwargs passed to SpectrumOfInfinities
        (e.g. normalize_to, adv_mode, type, test_mode, test_value).
    """

    def __init__(self, soi_params=None):
        self.soi_params = soi_params.copy() if soi_params else {}

    def dfi(self, data, soi=None, **soi_kwargs):
        """
        Compute the Dynamic Fluctuation Index on `data`.

        Args:
          data       : pandas DataFrame or 2D numpy array.
          soi        : optional float/int or SpectrumOfInfinities instance.
          **soi_kwargs: any of normalize_to, adv_mode, type, test_mode, test_value
                       to override or extend soi_params.

        Returns:
          dict mapping column → {
              'Relative_Entropy': np.ndarray,
              'Entropic_Weight' : np.ndarray,
              'Relative_Volume' : np.ndarray
          }
        """
        ε = np.finfo(float).eps

        # pull out data values and feature names
        if hasattr(data, "columns"):
            feature_list = data.columns
            arr = data.values
        else:
            arr = np.asarray(data)
            feature_list = list(range(arr.shape[1]))

        # number of features
        xn = arr.shape[1]

        # resolve soi_val
        if isinstance(soi, SpectrumOfInfinities):
            # optionally update its params
            for k, v in soi_kwargs.items():
                setattr(soi, k, v)
            soi_val = soi.soi()
        elif soi is None:
            # build a new SpectrumOfInfinities from stored + call-time params
            params = dict(self.soi_params)
            params.update(soi_kwargs)
            soi_inst = SpectrumOfInfinities(**params)
            soi_val = soi_inst.soi()
        else:
            # numeric override
            soi_val = float(soi)

        # V0 is base volume
        V0 = soi_val / xn

        entropical_data = {}
        x_n = arr.sum(axis=1)[:, None]   # column sum per row

        for idx, col in enumerate(feature_list):
            x_i = arr[:, [idx]]
            x_r = x_n - x_i

            with np.errstate(divide='ignore', invalid='ignore'):
                # avoid division by zero
                sigma = (x_n * (xn - 1)) / (x_r * xn + ε)  # ε inside denominator!
            V_x = V0 * sigma
            S = V_x - V0

            # Replace non-finite values (from any still-possible numerical weirdness)
            S = np.where(np.isfinite(S), S, 0)
            sigma = np.where(np.isfinite(sigma), sigma, 1)
            V_x = np.where(np.isfinite(V_x), V_x, 1)

            entropical_data[col] = {
                "Relative_Entropy": S.ravel(),
                "Entropic_Weight":  sigma.ravel(),
                "Relative_Volume":  V_x.ravel(),
            }


        return entropical_data


if __name__ == "__main__":
    import argparse, textwrap
    parser = argparse.ArgumentParser(
        prog="dfi",
        description="Compute Dynamic Fluctuation Index on a dataset"
    )
    parser.add_argument("--soi", type=float, help="Manual SOI value (default: auto)", default=None)
    parser.add_argument("--normalize_to", type=float, default=100,
                        help="Normalization constant for SpectrumOfInfinities")
    parser.add_argument("--adv_mode", action="store_true",
                        help="Enable advanced symmetric spectrum mode")
    parser.add_argument("--type", choices=["symmetric","dualistic"],
                        help="Required if --adv_mode is set")
    args = parser.parse_args()

    print(textwrap.dedent(f"""
    DynamicFluctuationIndex CLI
    ----------------------------
    soi             : {args.soi}
    normalize_to    : {args.normalize_to}
    adv_mode        : {args.adv_mode}
    type            : {args.type}

    Usage in Python:
      from dfi import DynamicFluctuationIndex
      dfi = DynamicFluctuationIndex(normalize_to={args.normalize_to}, adv_mode={args.adv_mode}, type="{args.type}")
      results = dfi.dfi(my_dataframe, soi={args.soi})
    """))
