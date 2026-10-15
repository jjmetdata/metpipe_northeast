import sys
from pathlib import Path
import unittest
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
from audit_finalized_availability import missing_runs, annual_summary, FIELDS


class FinalAvailabilityTests(unittest.TestCase):
    def test_runs_cross_year_and_boundary(self):
        index=pd.date_range('2023-12-31T22:00Z',periods=5,freq='h')
        runs=missing_runs(index,[True,False,False,True,False])
        self.assertEqual([r['missing_hours'] for r in runs],[2,1])
        self.assertEqual(runs[0]['end_utc_exclusive'],'2024-01-01T01:00:00+00:00')
        self.assertFalse(runs[0]['touches_scope_boundary'])
        self.assertTrue(runs[1]['touches_scope_boundary'])

    def test_72h_is_only_length_not_model_eligibility(self):
        index=pd.date_range('2024-01-01',periods=75,freq='h',tz='UTC')
        r=missing_runs(index,[True]+[False]*72+[True]*2)[0]
        self.assertTrue(r['within_72h_length_only'])
        r=missing_runs(index,[True]+[False]*73+[True])[0]
        self.assertFalse(r['within_72h_length_only'])

    def test_missing_scaffold_rejected(self):
        index=pd.to_datetime(['2024-01-01T00:00Z','2024-01-01T02:00Z'])
        with self.assertRaises(ValueError):
            missing_runs(index,[True,False])

    def test_weighted_denominator_not_mean_of_percentages(self):
        rows=[]
        for year,expected,present in [(2023,8760,8760),(2024,8784,0)]:
            r={'station':'PVC','year':year,'expected_hours':expected,'stored_rows':expected}
            r.update({f+'_hours':present for f in FIELDS})
            r.update({f+'_hours':present for f in ['wind_reported_state','any_core','all_core','selected_report']})
            rows.append(r)
        s=annual_summary(pd.DataFrame(rows),'core').iloc[0]
        self.assertAlmostEqual(s.temperature_c_pct,100*8760/17544)
        self.assertNotEqual(s.temperature_c_pct,50.)


if __name__=='__main__':
    unittest.main()
