import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from weather_events import (add_reference_and_changes, temperature_reference,
                            select_events, response_screen, field_segments, shift_hours,
                            pressure_from_window_start, pressure_window_summary, add_pc24,
                            pc24_transition_screen, pc24_timing_comparisons)


def example(hours=240):
    times = pd.date_range("2024-01-01", periods=hours, freq="h", tz="UTC")
    return pd.DataFrame([{ "hour_utc": time, "station": station,
                         "observation_time_utc": shift_hours(time, minute / 60),
                         "temperature_c": 10., "dewpoint_c": 3., "station_pressure_hpa": 1000.,
                         "has_report": True}
                        for time in times for station, minute in [("ALB", 51), ("BOS", 54)]])


def signals():
    frame = example()
    ref = temperature_reference(frame, minimum_samples=1)
    result = add_reference_and_changes(frame, ref)
    for hour, change in [(30, -8.), (31, -7.), (130, -6.), (220, -9.)]:
        mask = result.station.eq("ALB") & result.hour_utc.eq(shift_hours(result.hour_utc.min(), hour))
        result.loc[mask, ["temperature_c_change_3h", "temperature_anomaly_c_change_3h"]] = change
    return result


class WeatherEventTests(unittest.TestCase):
    def test_changes_reject_gaps_and_keep_units(self):
        frame = example(6)
        frame.loc[frame.station.eq("ALB") & frame.hour_utc.dt.hour.eq(1), "temperature_c"] = np.nan
        ref = temperature_reference(frame, minimum_samples=1)
        result = add_reference_and_changes(frame, ref)
        alb = result[result.station.eq("ALB")]
        self.assertTrue(alb.temperature_c_change_3h.iloc[3:5].isna().all())
        self.assertEqual(alb.temperature_c_change_3h.iloc[5], 0.)

    def test_irregular_actual_elapsed_time_rejected(self):
        frame = example(6)
        mask = frame.station.eq("ALB") & frame.hour_utc.dt.hour.eq(3)
        frame.loc[mask, "observation_time_utc"] = frame.loc[mask, "observation_time_utc"].map(lambda t: shift_hours(t, -.75))
        result = add_reference_and_changes(frame, temperature_reference(frame, 1))
        self.assertTrue(pd.isna(result.loc[mask, "temperature_c_change_3h"]).all())

    def test_reference_requires_sample_support(self):
        self.assertTrue(temperature_reference(example(6)).reference_temperature_c.isna().all())

    def test_month_boundary_reference_step_not_weather_change(self):
        frame = example(8)
        frame["hour_utc"] = frame.hour_utc.map(lambda t: shift_hours(t, 30 * 24 + 22))
        frame["observation_time_utc"] = frame.observation_time_utc.map(lambda t: shift_hours(t, 30 * 24 + 22))
        ref = temperature_reference(frame, 1)
        ref.loc[ref.month.eq(2), "reference_temperature_c"] = 20.
        result = add_reference_and_changes(frame, ref)
        alb = result[result.station.eq("ALB")]
        self.assertTrue(alb.temperature_anomaly_c_change_3h.iloc[2:5].isna().all())
        self.assertEqual(alb.temperature_anomaly_c_change_3h.iloc[5], 0.)
        self.assertEqual([len(s) for s in field_segments(alb, "temperature_anomaly_c")], [2, 6])

    def test_source_only_selection_separation_and_edges(self):
        data = signals()
        selected = select_events(data)
        self.assertEqual(selected.hour_utc.dt.day.tolist(), [2, 6])
        # Strongest edge event excluded; adjacent source event suppressed.
        data.loc[data.station.eq("BOS"), "temperature_anomaly_c_change_3h"] = -100.
        pd.testing.assert_frame_equal(selected, select_events(data))

    def test_no_downstream_hit_stays_missing(self):
        data = signals()
        summary = response_screen(data, select_events(data).head(1), ["ALB", "BOS"])
        self.assertEqual(summary.iloc[0].detection_offset_hours_not_lag, 0.)
        self.assertTrue(pd.isna(summary.iloc[1].detection_offset_hours_not_lag))

    def test_segments_break_at_missing_element(self):
        frame = example(3).query("station == 'ALB'").copy()
        frame.iloc[1, frame.columns.get_loc("dewpoint_c")] = np.nan
        self.assertEqual([len(s) for s in field_segments(frame, "dewpoint_c")], [1, 1])

    def test_pressure_departures_remove_constant_station_offsets(self):
        frame = example(6)
        frame["station_pressure_hpa"] += frame.hour_utc.dt.hour * 2
        frame.loc[frame.station.eq("BOS"), "station_pressure_hpa"] += 15
        result = pressure_from_window_start(frame)
        self.assertEqual(result[result.station.eq("ALB")].pressure_departure_hpa.tolist(), [0, 2, 4, 6, 8, 10])
        self.assertEqual(result[result.station.eq("BOS")].pressure_departure_hpa.tolist(), [0, 2, 4, 6, 8, 10])

    def test_missing_pressure_anchor_is_not_replaced_by_later_value(self):
        frame = example(6)
        frame.loc[frame.station.eq("ALB") & frame.hour_utc.dt.hour.eq(0), "station_pressure_hpa"] = np.nan
        result = pressure_from_window_start(frame)
        self.assertTrue(result[result.station.eq("ALB")].pressure_departure_hpa.isna().all())
        self.assertTrue(result[result.station.eq("BOS")].pressure_departure_hpa.eq(0).all())

    def test_pressure_changes_and_summary_preserve_missingness(self):
        frame = example(7)
        frame["station_pressure_hpa"] += frame.hour_utc.dt.hour
        frame.loc[frame.station.eq("ALB") & frame.hour_utc.dt.hour.eq(1), "station_pressure_hpa"] = np.nan
        data = add_reference_and_changes(frame, temperature_reference(frame, 1))
        summary = pressure_window_summary(data).set_index("station")
        self.assertEqual(summary.loc["ALB", "valid_pressure_hours"], 6)
        self.assertEqual(summary.loc["ALB", "valid_pressure_change_3h_hours"], 2)
        self.assertEqual(summary.loc["ALB", "largest_observed_3h_change_hpa"], 3)
        self.assertEqual(summary.loc["BOS", "baseline_report_utc"].minute, 54)

    def test_pressure_anchor_requires_common_start_scaffold(self):
        frame = example(6)
        frame = frame[~(frame.station.eq("ALB") & frame.hour_utc.dt.hour.eq(0))]
        with self.assertRaises(ValueError):
            pressure_from_window_start(frame)

    def test_pc24_sign_units_and_station_independence(self):
        frame = example(30)
        elapsed = (frame.hour_utc - frame.hour_utc.min()).dt.total_seconds() / 3600
        frame["station_pressure_hpa"] += elapsed
        frame.loc[frame.station.eq("BOS"), "station_pressure_hpa"] = 1050 - elapsed[frame.station.eq("BOS")]
        result = add_pc24(frame)
        alb = result[result.station.eq("ALB")]
        bos = result[result.station.eq("BOS")]
        self.assertTrue(alb.pc24_hpa.iloc[:24].isna().all())
        self.assertTrue(alb.pc24_hpa.iloc[24:].eq(24).all())
        self.assertTrue(bos.pc24_hpa.iloc[24:].eq(-24).all())
        self.assertEqual(alb.iloc[24].observation_time_24h_ago_utc.minute, 51)

    def test_pc24_missing_endpoint_not_missing_intermediate(self):
        frame = example(30)
        frame.loc[frame.station.eq("ALB") & frame.hour_utc.eq(frame.hour_utc.min()), "station_pressure_hpa"] = np.nan
        frame.loc[frame.station.eq("BOS") & frame.hour_utc.dt.hour.eq(10), "station_pressure_hpa"] = np.nan
        result = add_pc24(frame)
        self.assertTrue(pd.isna(result[result.station.eq("ALB")].iloc[24].pc24_hpa))
        bos = result[result.station.eq("BOS")].iloc[24]
        self.assertEqual(bos.pc24_hpa, 0.)
        self.assertEqual(bos.pc24_window_valid_pressure_hours, 24)

    def test_pc24_rejects_missing_calendar_rows(self):
        frame = example(30)
        frame = frame[~(frame.station.eq("ALB") & frame.hour_utc.dt.hour.eq(10))]
        with self.assertRaises(ValueError):
            add_pc24(frame)

    def test_pc24_irregular_endpoint_time_rejected(self):
        frame = example(30)
        mask = frame.station.eq("ALB") & frame.hour_utc.eq(shift_hours(frame.hour_utc.min(), 24))
        frame.loc[mask, "observation_time_utc"] = frame.loc[mask, "observation_time_utc"].map(lambda t: shift_hours(t, -.75))
        result = add_pc24(frame)
        self.assertTrue(result.loc[mask, "pc24_hpa"].isna().all())

    def test_pc24_transition_confirmation_not_backdated(self):
        frame = example(50)
        frame["pc24_hpa"] = -1.
        frame.loc[frame.station.eq("ALB") & frame.hour_utc.ge(shift_hours(frame.hour_utc.min(), 20)), "pc24_hpa"] = 2.
        frame.loc[frame.station.eq("BOS") & frame.hour_utc.ge(shift_hours(frame.hour_utc.min(), 25)), "pc24_hpa"] = 2.
        event = pd.DataFrame([{"event_rank": 1, "hour_utc": shift_hours(frame.hour_utc.min(), 20)}])
        found = pc24_transition_screen(frame, event, ["ALB", "BOS"])
        self.assertEqual(found.iloc[0].first_positive_report_utc.hour, 20)
        self.assertEqual(found.iloc[0].confirmation_report_utc.hour, 22)
        comparison = pc24_timing_comparisons(found, targets=["BOS"]).iloc[0]
        self.assertTrue(comparison.unambiguous_complete_search_pair)
        self.assertAlmostEqual(comparison.first_positive_offset_hours, 5.05)
        self.assertAlmostEqual(comparison.source_confirmation_to_target_first_positive_hours, 3.05)
        self.assertAlmostEqual(comparison.crossing_offset_lower_bound_hours, 4.05)

    def test_pc24_transition_gap_does_not_create_crossing(self):
        frame = example(50)
        frame["pc24_hpa"] = -1.
        frame.loc[frame.hour_utc.ge(shift_hours(frame.hour_utc.min(), 20)), "pc24_hpa"] = 2.
        frame.loc[frame.hour_utc.eq(shift_hours(frame.hour_utc.min(), 19)), "pc24_hpa"] = np.nan
        event = pd.DataFrame([{"event_rank": 1, "hour_utc": shift_hours(frame.hour_utc.min(), 20)}])
        found = pc24_transition_screen(frame, event, ["ALB", "BOS"])
        self.assertTrue(found.first_positive_report_utc.isna().all())
        self.assertTrue(found.status.eq("no_observed_crossing_with_gaps").all())

    def test_pc24_short_positive_blip_does_not_confirm(self):
        frame = example(50)
        frame["pc24_hpa"] = -1.
        frame.loc[frame.hour_utc.eq(shift_hours(frame.hour_utc.min(), 20)), "pc24_hpa"] = 2.
        event = pd.DataFrame([{"event_rank": 1, "hour_utc": shift_hours(frame.hour_utc.min(), 20)}])
        found = pc24_transition_screen(frame, event, ["ALB", "BOS"])
        self.assertTrue(found.qualifying_crossings.eq(0).all())

    def test_pc24_multiple_crossings_flagged_not_cherry_picked(self):
        frame = example(50)
        frame["pc24_hpa"] = -1.
        for offset in [20, 28]:
            frame.loc[frame.hour_utc.ge(shift_hours(frame.hour_utc.min(), offset)) &
                      frame.hour_utc.lt(shift_hours(frame.hour_utc.min(), offset + 4)), "pc24_hpa"] = 2.
        event = pd.DataFrame([{"event_rank": 1, "hour_utc": shift_hours(frame.hour_utc.min(), 20)}])
        found = pc24_transition_screen(frame, event, ["ALB", "BOS"])
        self.assertTrue(found.status.eq("multiple_observed_crossings").all())
        self.assertFalse(pc24_timing_comparisons(found, targets=["BOS"]).iloc[0].unambiguous_complete_search_pair)


if __name__ == "__main__":
    unittest.main()
