import csv
import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
from publish_final_observations import lcd_quality, snapshot_sql, policy_definition
from ingest_auxiliary_cqx import auxiliary_stream, VERSION
from add_parallel_ghcnh import COLUMNS
from audit_network_ghcnh import select_records
from test_network_ghcnh_audit import row


class FinalPublicationTests(unittest.TestCase):
    def test_lcd_suspect_and_original_raw_consistency(self):
        self.assertTrue(lcd_quality({'HourlyDryBulbTemperature':'50s'},'temperature_c',10.))
        self.assertFalse(lcd_quality({'HourlyDryBulbTemperature':'50'},'temperature_c',10.))
        self.assertTrue(lcd_quality({'HourlyDryBulbTemperature':'51'},'temperature_c',10.))
        self.assertTrue(lcd_quality(None,'temperature_c',10.))

    def test_trace_marker_is_not_positive_rainfall(self):
        self.assertFalse(lcd_quality({'HourlyPrecipitation':'T'},'precipitation_reported_mm',.0254))

    def test_snapshot_keeps_hour_and_null_override(self):
        sql=snapshot_sql()
        self.assertIn('generate_series',sql)
        self.assertIn("d.decisions ? 'temperature_c'",sql)
        self.assertNotIn('COALESCE(g.temperature_c',sql)
        self.assertNotIn('DELETE',sql.upper())
        self.assertNotIn('public.weather_observations',sql)

    def test_policy_remains_core20_no_cqx(self):
        self.assertEqual(len(policy_definition()['core_stations']),20)
        self.assertNotIn('CQX',policy_definition()['core_stations'])

    def test_auxiliary_identity_not_pvc(self):
        raw=pd.DataFrame([row()])
        chosen,_=select_records(raw)
        data=dict(zip(COLUMNS,next(csv.reader(auxiliary_stream(raw,chosen,2024)))))
        self.assertEqual(data['dataset_version'],VERSION)
        self.assertEqual(data['station'],'CQX')
        self.assertNotEqual(data['station'],'PVC')


if __name__=='__main__':
    unittest.main()
