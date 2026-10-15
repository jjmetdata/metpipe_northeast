import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from eda_utils import FIELDS, complete_calendar, eligible_daily, period_means, correlations, lag_correlations


def frame():
    records = []
    for date, value, hours in [("2020-01-01",10.,24),("2020-01-03",20.,12)]:
        row = {"date":pd.Timestamp(date),"station":"AAA","routine_hours":hours,
               "source_dataset":"test","precipitation_mm_hours":0,"observed_precipitation_mm":np.nan}
        for field in FIELDS:
            row[field],row[field+"_hours"] = value,hours
        records.append(row)
    return pd.DataFrame(records)


class EdaTests(unittest.TestCase):
    def test_missing_day_is_not_zero_weather(self):
        daily = complete_calendar(frame(),["AAA"],"2020-01-01","2020-01-04")
        self.assertEqual(daily.iloc[1]["routine_hours"],0)
        self.assertTrue(pd.isna(daily.iloc[1]["temperature_c"]))
        self.assertTrue(pd.isna(daily.iloc[1]["observed_precipitation_mm"]))
        self.assertTrue(pd.isna(eligible_daily(daily).iloc[2]["temperature_c"]))

    def test_period_mean_is_weighted_and_coverage_screened(self):
        daily = complete_calendar(frame(),["AAA"],"2020-01-01","2020-01-04")
        result = period_means(daily,"temperature_c",minimum_fraction=0)
        self.assertAlmostEqual(result.iloc[0]["temperature_c"],40/3)
        self.assertAlmostEqual(result.iloc[0]["coverage"],0.5)
        self.assertTrue(pd.isna(period_means(daily,"temperature_c").iloc[0]["temperature_c"]))

    def test_pair_counts_are_pairwise_not_global_complete_cases(self):
        wide = pd.DataFrame({"A":[1,2,3,np.nan],"B":[2,4,np.nan,8],"C":[np.nan,3,5,7]})
        r,n = correlations(wide,minimum_pairs=3)
        self.assertEqual(n.loc["A","B"],2)
        self.assertTrue(pd.isna(r.loc["A","B"]))

    def test_positive_lag_means_source_earlier(self):
        source = pd.Series([2,7,1,8,3,9,4,6],index=pd.date_range("2020-01-01",periods=8))
        wide = pd.DataFrame({"A":source,"B":source.shift(1)})
        result = lag_correlations(wide,"A","B",maximum_days=2,minimum_pairs=3)
        self.assertAlmostEqual(result.loc[result.lag_days==1,"pearson_r"].iloc[0],1)

    def test_lag_cannot_silently_shift_across_missing_calendar_rows(self):
        wide = pd.DataFrame({"A":[1,2],"B":[2,3]}, index=pd.to_datetime(["2020-01-01","2020-01-03"]))
        with self.assertRaises(ValueError):
            lag_correlations(wide,"A","B")


if __name__ == "__main__":
    unittest.main()
