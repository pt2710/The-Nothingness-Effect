import numpy as np

class ElasticPi:
    """
    Universal ElasticPi class for computation and analysis of the elastic pi field.

    Args:
        K_D (float, optional): Default characteristic scaling constant for the system.
            Defaults to 1.0 (not np.pi). Can be overridden per call.
    """

    def __init__(self, K_D=1.0):
        """
        Initialize ElasticPi with the default scaling constant.

        Args:
            K_D (float, optional): Default entropy scaling constant. Defaults to 1.0.
        """
        self.K_D = float(K_D)

    def build_S_analytic(self, x, formula=None, **kwargs):
        """
        Construct analytic or synthetic relative entropy S(x).

        Args:
            x (np.ndarray): 1D spatial or temporal coordinate array.
            formula (callable, optional): Function to compute S(x). Must accept x and **kwargs.
            **kwargs: Extra parameters for formula.

        Returns:
            np.ndarray: Analytic S(x).
        """
        if formula is not None:
            return formula(x, **kwargs)
        return np.zeros_like(x)

    def compute_piE_and_laplacian(self, S, x=None, K_D=None):
        """
        Compute elastic pi field and Laplacian of its log.

        Args:
            S (np.ndarray): Relative entropy array.
            x (np.ndarray, optional): Coordinates. If None, uses unit spacing.
            K_D (float, optional): Override scaling constant for this computation. Defaults to self.K_D.

        Returns:
            tuple:
                x (np.ndarray): Coordinates.
                piE (np.ndarray): Elastic pi field.
                lap (np.ndarray): Laplacian of log(piE).
        """
        _K_D = float(self.K_D) if K_D is None else float(K_D)
        if x is None:
            x = np.arange(len(S))
            h = 1.0
        else:
            x = np.asarray(x)
            h = np.mean(np.diff(x))

        # --- Robust handling to prevent overflow/underflow ---
        expo = np.clip(-S / _K_D, -700, 700)
        piE = np.pi * np.exp(expo)
        # Avoid log(0): replace zeros with tiny value before log
        piE = np.where(piE == 0, 1e-300, piE)
        lnE = np.log(piE)
        lap = np.zeros_like(lnE)
        lap[1:-1] = (lnE[2:] - 2 * lnE[1:-1] + lnE[:-2]) / (h ** 2)
        return x, piE, lap

    def empirical_from_dfi(self, data, dfi_engine, soi=1.0, feature=None):
        """
        Compute relative entropy S from a DFI engine.

        Args:
            data (np.ndarray or pd.DataFrame): Input dataset.
            dfi_engine (DynamicFluctuationIndex): Instance of DFI calculator.
            soi (float, optional): Spectrum of Infinities parameter.
            feature (str or int, optional): Use specific feature, else mean across all.

        Returns:
            np.ndarray: Relative entropy S.
        """
        entropic = dfi_engine.dfi(data, soi=soi)
        if feature is not None:
            S = entropic[feature]["Relative_Entropy"]
        else:
            all_S = [featdict["Relative_Entropy"] for featdict in entropic.values()]
            S = np.mean(np.vstack(all_S), axis=0)
        return S
