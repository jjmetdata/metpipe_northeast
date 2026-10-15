import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from export_availability import load_reports, FIELDS


class ReportSnapshotTests(unittest.TestCase):
    def test_calendar_counts_reconcile(self):
        stations, years = load_reports()
        self.assertEqual(set(years.year), set(range(2005, 2025)))
        totals = years.groupby('station').sum(numeric_only=True).sort_index()
        for field in FIELDS:
            column = field.removesuffix('_pct') + '_hours'
            np.testing.assert_array_equal(stations[column], totals[column])
        self.assertTrue(years.expected_hours.isin([8760, 8784]).all())

    def test_observed_only_snapshot(self):
        stations, _ = load_reports()
        self.assertTrue(stations.role.eq('core_finalized').all())
        self.assertEqual(int(stations.loc[stations.station.eq('PVC'), 'station_pressure_hpa_hours'].iloc[0]), 162681)


if __name__ == '__main__':
    unittest.main()
