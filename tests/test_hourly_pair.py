import sys
from pathlib import Path
import unittest
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from hourly_pair import align_hourly, coverage_stats, contiguous_temperature_segments, utc_hour


def records():
    return pd.DataFrame([
        {"hour_utc":"2024-01-01T05:00Z","station":"BOS","observation_time_utc":"2024-01-01T05:54Z","temperature_c":2.,"source_dataset":"test"},
        {"hour_utc":"2024-01-01T07:00Z","station":"BOS","observation_time_utc":"2024-01-01T07:54Z","temperature_c":3.,"source_dataset":"test"},
        {"hour_utc":"2024-01-01T05:00Z","station":"PVC","observation_time_utc":"2024-01-01T05:56Z","temperature_c":None,"source_dataset":"test"},
    ])


class HourlyPairTests(unittest.TestCase):
    def test_three_stations_retain_individual_reporting_times(self):
        extra = pd.DataFrame([{"hour_utc":"2024-01-01T05:00Z","station":"ALB",
                               "observation_time_utc":"2024-01-01T05:51Z","temperature_c":-2.,"source_dataset":"test"}])
        result = align_hourly(pd.concat([records(),extra]),["ALB","BOS","PVC"],
                              "2024-01-01T05:00Z","2024-01-01T08:00Z")
        self.assertEqual(len(result),9)
        self.assertEqual(result[result.station=="ALB"].iloc[0].observation_time_utc.minute,51)
        self.assertEqual(coverage_stats(result).loc["ALB","missing_report_hours"],2)

    def test_scaffold_preserves_missing_times_and_temperature(self):
        result = align_hourly(records(),["BOS","PVC"],"2024-01-01T05:00Z","2024-01-01T08:00Z")
        self.assertEqual(len(result),6)
        missing = result[(result.station=="BOS") & (result.hour_utc.dt.hour==6)].iloc[0]
        self.assertFalse(missing.has_report)
        self.assertTrue(pd.isna(missing.temperature_c))
        self.assertTrue(pd.isna(missing.observation_time_utc))
        stats = coverage_stats(result)
        self.assertEqual(stats.loc["PVC","reports_without_temperature"],1)
        self.assertEqual(stats.loc["PVC","missing_report_hours"],2)
        self.assertEqual(result[result.station=="BOS"].iloc[0].observation_time_utc.minute,54)

    def test_lines_break_at_gaps(self):
        aligned = align_hourly(records(),["BOS","PVC"],"2024-01-01T05:00Z","2024-01-01T08:00Z")
        segments = contiguous_temperature_segments(aligned[aligned.station=="BOS"])
        self.assertEqual([len(s) for s in segments],[1,1])

    def test_duplicates_and_wrong_bucket_are_rejected(self):
        data = records()
        with self.assertRaises(ValueError):
            align_hourly(pd.concat([data,data.iloc[:1]]),["BOS","PVC"],"2024-01-01T05:00Z","2024-01-01T08:00Z")
        data.loc[0,"observation_time_utc"] = "2024-01-01T06:54Z"
        with self.assertRaises(ValueError):
            align_hourly(data,["BOS","PVC"],"2024-01-01T05:00Z","2024-01-01T08:00Z")

    def test_window_requires_explicit_zone_and_whole_hour(self):
        with self.assertRaises(ValueError):
            utc_hour("2024-01-01")
        with self.assertRaises(ValueError):
            utc_hour("2024-01-01T05:30Z")


if __name__ == "__main__":
    unittest.main()
