import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from audit_pvc_neighbors import qc_tier, select_routine, pair_mask, compare, temperature_review_flags


class NeighborTests(unittest.TestCase):
    def test_source_dependent_pressure_quality_four(self):
        self.assertEqual(qc_tier("343", "4", "station_level_pressure"), 1)
        self.assertEqual(qc_tier("220", "4", "station_level_pressure"), 0)
        self.assertEqual(qc_tier("343", "5", "temperature"), 2)
        self.assertEqual(qc_tier("343", "5p", "station_level_pressure"), 0)
        self.assertEqual(qc_tier("343", "6", "station_level_pressure"), 0)

    def test_awos_temperature_flag_not_unknown_pressure_flag(self):
        self.assertEqual(qc_tier("343", "C", "temperature"), 1)
        self.assertEqual(qc_tier("343", "C", "station_level_pressure"), 0)
        self.assertEqual(qc_tier("999", "1", "temperature"), 0)

    def test_routine_selection_keeps_coherent_times_and_excludes_specials(self):
        raw = pd.DataFrame({"DATE": ["2024-01-01T00:51:00", "2024-01-01T00:55:00", "2024-01-01T00:58:00"],
                            "temperature": [10., 11., 30.], "station_level_pressure": [1000., 1001., 1030.]})
        for e in ["temperature", "station_level_pressure"]:
            raw[e+"_Source_Code"] = "343"
            raw[e+"_Quality_Code"] = "4" if e == "station_level_pressure" else "5"
            raw[e+"_Report_Type"] = ["FM15", "FM15", "FM16"]
        chosen, _ = select_routine(raw, "GHG", 2024)
        self.assertEqual(len(chosen), 1)
        self.assertEqual(chosen.iloc[0].observation_time_utc.minute, 55)
        self.assertEqual(chosen.iloc[0].station_pressure_hpa, 1001)
        self.assertTrue(pd.isna(chosen.iloc[0].station_pressure_hpa_fullqc))

    def test_pc24_pair_checks_both_endpoint_alignment(self):
        pair = pd.DataFrame({"pc24_hpa_candidate": [1.], "pc24_hpa_PVC": [1.],
            "observation_time_utc_candidate": pd.to_datetime(["2024-01-02T00:55Z"]),
            "observation_time_utc_PVC": pd.to_datetime(["2024-01-02T00:56Z"]),
            "observation_time_24h_ago_utc_candidate": pd.to_datetime(["2024-01-01T00:05Z"]),
            "observation_time_24h_ago_utc_PVC": pd.to_datetime(["2024-01-01T00:56Z"])})
        self.assertFalse(pair_mask(pair, "pc24_hpa").iloc[0])

    def test_common_sample_does_not_rank_different_missingness(self):
        times = pd.date_range("2024-01-01", periods=600, freq="h", tz="UTC")
        rows = []
        for station in ["HYA", "PYM", "GHG", "CQX", "PVC"]:
            for i, time in enumerate(times):
                rows.append({"station": station, "hour_utc": time,
                             "observation_time_utc": time,
                             "temperature_c": np.nan if station == "GHG" and i < 30 else float(i)})
        result, _, _ = compare(pd.DataFrame(rows), ["temperature_c"])
        self.assertTrue(result[result["sample"].eq("common_all_four")].paired_hours.eq(570).all())
        self.assertEqual(result[result["sample"].eq("pairwise") & result.candidate.eq("HYA")].iloc[0].paired_hours, 600)

    def test_temperature_review_not_based_on_neighbor_difference(self):
        frame = pd.DataFrame({"hour_utc": pd.to_datetime(["2021-06-15T20:00Z", "2020-01-01T00:00Z", "2024-07-01T00:00Z"]),
                              "temperature_c": [-40., -48.9, 30.]})
        self.assertEqual(temperature_review_flags(frame).tolist(), [True, True, False])


if __name__ == "__main__":
    unittest.main()
