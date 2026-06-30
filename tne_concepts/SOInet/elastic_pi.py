import numpy as np
from sympy import primerange

class ElasticPi:
    def __init__(self, K_D):
        self.K_D = K_D

    def build_S_analytic(self, L, N, num_primes=100, fp_gen=None):
        h = L/(N+1)
        x = h * np.arange(1, N+1)
        primes = list(primerange(2, 10000))[:num_primes]
        S_raw = np.zeros_like(x)

        if fp_gen is None:
            raise ValueError("You must supply a Flowpoint generator (fp_gen).")
        for p in primes:
            a_p = next(fp_gen)
            arg = np.clip(1 - a_p * np.exp(-p * x), 1e-12, None)
            S_raw += np.log(arg)
        return -self.K_D * S_raw

    def compute_piE_and_laplacian(self, L, N, S):
        h = L/(N+1)
        x = h * np.arange(1, N+1)
        piE = np.pi * np.exp(-S/self.K_D)
        lnE = np.log(piE)
        lap = np.zeros_like(lnE)
        lap[1:-1] = (lnE[2:] - 2*lnE[1:-1] + lnE[:-2]) / h**2
        return x, piE, lap

    def empirical_from_dfi(self, data, soi=1.0, feature=None):
        from dfi import DFI
        entropic = DFI.compute_entropical_data(data, soi=soi)
        if feature is not None:
            S = entropic[feature]["Relative_Entropy"]
        else:
            all_S = [featdict["Relative_Entropy"] for featdict in entropic.values()]
            S = np.mean(np.vstack(all_S), axis=0)
        return S
