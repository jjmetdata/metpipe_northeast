import csv
import json
import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from add_parallel_ghcnh import serialize, wind_value, COLUMNS
from audit_network_ghcnh import select_records
from test_network_ghcnh_audit import row


class ParallelDatasetTests(unittest.TestCase):
    def test_calm_variable_not_bearing(self):
        self.assertEqual(wind_value({'wind_direction_Measurement_Code': 'C'}, 0), (None, 'calm'))
        self.assertEqual(wind_value({'wind_direction_Measurement_Code': 'V'}, 0), (None, 'variable'))
        self.assertEqual(wind_value({}, 350), (350., 'numeric'))
        self.assertEqual(wind_value({}, float('nan')), (None, 'missing'))

    def test_serialization_missing_rain_and_source_flags(self):
        raw = pd.DataFrame([row()])
        chosen, _ = select_records(raw)
        serialized = next(csv.reader(serialize(raw, chosen, 'BOS', 2024)))
        data = dict(zip(COLUMNS, serialized))
        self.assertEqual(data['temperature_c'], '10.0')
        self.assertEqual(data['precipitation_reported_mm'], '\\N')
        self.assertEqual(data['precipitation_trace'], '\\N')
        self.assertEqual(data['wind_direction_deg'], '\\N')
        self.assertEqual(data['wind_state'], 'missing')
        self.assertEqual(json.loads(data['quality_flags'])['temperature']['q'], '4')
        self.assertIn('+00:00', data['observation_datetime_utc'])

    def test_trace_preserved_separately(self):
        item = row()
        item['precipitation'] = 0.
        item['precipitation_Measurement_Code'] = '2'
        raw = pd.DataFrame([item])
        chosen, _ = select_records(raw)
        data = dict(zip(COLUMNS, next(csv.reader(serialize(raw, chosen, 'BOS', 2024)))))
        self.assertEqual(data['precipitation_reported_mm'], '0.0')
        self.assertEqual(data['precipitation_trace'], 'True')


if __name__ == '__main__':
    unittest.main()
