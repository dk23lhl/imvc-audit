"""Verify closed-form expected_stats matches empirical_stats on Monte Carlo masks."""
import unittest

import numpy as np

from imvc_audit import expected_stats, empirical_stats, generate_mask


class TestClosedFormVsEmpirical(unittest.TestCase):
    """For each (V, r, protocol), generate a large mask and confirm
    empirical r_hat and p_c match the closed-form prediction."""

    def test_all_protocols_all_rates(self):
        rng = np.random.default_rng(0)
        n = 10000
        for V in (2, 3, 6):
            for r in (0.1, 0.3, 0.5, 0.7):
                for proto in ("P1", "P2", "P3", "P4"):
                    expected = expected_stats(V, r, proto)
                    M = generate_mask(n, V, r, proto, rng=rng)
                    emp = empirical_stats(M)
                    msg = f"V={V}, r={r}, {proto}: expected={expected} empirical={emp}"
                    # r_hat tolerance: stdev of mean of nV Bernoullis ~ 1/sqrt(nV)
                    self.assertAlmostEqual(emp["r_hat"], expected["r_hat"],
                                           delta=0.01, msg=msg)
                    # p_c tolerance: stdev ~ 1/sqrt(n) plus quantization
                    self.assertAlmostEqual(emp["p_c"], expected["p_c"],
                                           delta=0.02, msg=msg)


class TestEmpiricalStats(unittest.TestCase):
    def test_all_observed(self):
        M = np.ones((100, 4), dtype=bool)
        s = empirical_stats(M)
        self.assertEqual(s["r_hat"], 0.0)
        self.assertEqual(s["p_c"], 1.0)
        self.assertEqual(s["avg_views"], 4.0)
        self.assertEqual(s["min_views_per_sample"], 4)

    def test_eq1_eq2_direct_count(self):
        M = np.array([
            [1, 1, 1, 1],
            [1, 1, 1, 0],
            [0, 1, 1, 1],
            [0, 0, 1, 1],
        ], dtype=bool)
        s = empirical_stats(M)
        # 4 missing out of 16 cells -> 0.25
        self.assertAlmostEqual(s["r_hat"], 4 / 16)
        # 1 of 4 samples has all 4 views
        self.assertAlmostEqual(s["p_c"], 1 / 4)
        self.assertAlmostEqual(s["avg_views"], 12 / 4)
        self.assertEqual(s["min_views_per_sample"], 2)


class TestValidation(unittest.TestCase):
    def test_unknown_protocol_raises(self):
        with self.assertRaises(ValueError):
            generate_mask(10, 3, 0.5, "P5")
        with self.assertRaises(ValueError):
            expected_stats(3, 0.5, "P9")

    def test_bad_V_raises(self):
        with self.assertRaises(ValueError):
            generate_mask(10, 1, 0.5, "P1")
        with self.assertRaises(ValueError):
            expected_stats(1, 0.5, "P1")

    def test_bad_r_raises(self):
        with self.assertRaises(ValueError):
            generate_mask(10, 3, 1.5, "P1")
        with self.assertRaises(ValueError):
            expected_stats(3, -0.1, "P1")


if __name__ == "__main__":
    unittest.main()
