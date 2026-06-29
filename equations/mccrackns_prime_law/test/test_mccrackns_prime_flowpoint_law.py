"""
Author  : Budd McCrackn
Email   : thenothingnesseffect@gmail.com

Unit tests for McCracknsPrimeFlowpointLaw.

Usage:
    python -m unittest equations.mccrackns_prime_law.test_mccrackns_prime_flowpoint_law
"""
import sys
import os
import tempfile
import unittest
import csv

def find_project_root(marker_file_or_folder="equations"):
    d = os.path.abspath(__file__)
    while True:
        d = os.path.dirname(d)
        if marker_file_or_folder in os.listdir(d):
            return d
        if d == os.path.dirname(d):
            break
    raise RuntimeError(f"Could not find project root with marker '{marker_file_or_folder}'.")

project_root = find_project_root()
sys.path.insert(0, project_root)

from equations.mccrackns_prime_law.mccrackns_prime_flowpoint_law import McCracknsPrimeFlowpointLaw

class TestMcCracknsPrimeFlowpointLaw(unittest.TestCase):
    """
    Unit tests for deterministic prime/motif/parity/regime/domain generation and export.
    """

    def setUp(self):
        self.N = 13
        self.flowlaw = McCracknsPrimeFlowpointLaw(n_primes=self.N)
        self.flowlaw.generate()

    def test_prime_sequence(self):
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
        self.assertEqual(self.flowlaw.primes, expected_primes)
        self.assertEqual(len(self.flowlaw.primes), self.N)

    def test_gaps(self):
        expected_gaps = [1, 2, 2, 4, 2, 4, 2, 4, 6, 2, 6, 4]
        self.assertEqual(self.flowlaw.gaps, expected_gaps)
        self.assertEqual(len(self.flowlaw.gaps), self.N - 1)

    def test_parities(self):
        expected_parities = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1]
        self.assertEqual(self.flowlaw.parities, expected_parities)
        self.assertEqual(len(self.flowlaw.parities), self.N - 1)

    def test_motifs(self):
        expected_motifs = [
            "U1", "E1.0", "E1.0", "E1.1", "E1.0", "E1.1",
            "E1.0", "E1.1", "E2.0", "E1.0", "E2.0", "E1.1"
        ]
        self.assertEqual(self.flowlaw.motifs, expected_motifs)
        self.assertEqual(len(self.flowlaw.motifs), self.N - 1)

    def test_domains(self):
        expected_domains = [
            "U", "E", "E", "E", "E", "E",
            "E", "E", "E", "E", "E", "E"
        ]
        self.assertEqual(self.flowlaw.domains, expected_domains)
        self.assertEqual(len(self.flowlaw.domains), self.N - 1)

    def test_regimes(self):
        expected_regimes = [1, 6, 12]
        for r in expected_regimes:
            self.assertIn(r, self.flowlaw.regimes)

    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.flowlaw.export_all(tmpdir)
            csv_path = os.path.join(tmpdir, "data_results", "prime_flowpoint_table.csv")
            self.assertTrue(os.path.exists(csv_path))
            with open(csv_path, "r", newline="") as f:
                reader = csv.reader(f)
                header = next(reader)
                expected_header = ["index", "prime", "gap", "motif", "parity", "regime", "domain"]
                self.assertEqual(header, expected_header)
                rows = list(reader)
                self.assertEqual(len(rows), self.N)

    def test_export_feather(self):
        try:
            import pandas as pd
        except ImportError:
            return
        with tempfile.TemporaryDirectory() as tmpdir:
            self.flowlaw.export_all_feather(tmpdir)
            feather_path = os.path.join(tmpdir, "data_results", "prime_flowpoint_table.feather")
            self.assertTrue(os.path.exists(feather_path))
            df = pd.read_feather(feather_path)
            self.assertIn("prime", df.columns)
            self.assertEqual(len(df), self.N)

if __name__ == "__main__":
    unittest.main(verbosity=2)

