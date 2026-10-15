import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from verify_network_ghcnh import exact_pairs, metrics, passes, pc24


class VerificationTests(unittest.TestCase):
    def test_exact_timestamp_not_hour_bucket(self):
        a = pd.DataFrame({'actual_time': pd.to_datetime(['2024-01-01T00:51Z'])})
        b = pd.DataFrame({'actual_time': pd.to_datetime(['2024-01-01T00:54Z'])})
        self.assertTrue(exact_pairs(a, b).empty)

    def test_missing_is_not_zero(self):
        frame = pd.DataFrame({'temperature_c_ghcnh': [10., None],
                              'temperature_c_lcd': [10.1, 20.]})
        result = metrics(frame, 'temperature_c')
        self.assertEqual(result['paired_values'], 1)
        self.assertAlmostEqual(result['bias'], -.1)
        self.assertFalse(passes(result, 'temperature_c'))

    def test_pc24_exact_gap_safe(self):
        frame = pd.DataFrame({'actual_time': pd.to_datetime(
            ['2024-01-01T00:51Z', '2024-01-02T00:51Z', '2024-01-03T00:54Z']),
            'pressure': [1000., 1005., 1010.]})
        values = pc24(frame, 'pressure')
        self.assertTrue(pd.isna(values.iloc[0]))
        self.assertEqual(values.iloc[1], 5.)
        self.assertTrue(pd.isna(values.iloc[2]))

    def test_unit_mistake_fails_gate(self):
        result = {'paired_values': 5000, 'median_abs': 960., 'p95_abs': 990.}
        self.assertFalse(passes(result, 'station_pressure_hpa'))


if __name__ == '__main__':
    unittest.main()
