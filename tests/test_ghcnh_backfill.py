import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ghcnh_backfill import transform, rejected, ingest


def sample():
    row = {"DATE": "2006-01-01T05:53:00", "temperature": 0.0, "dew_point_temperature": -5.0,
           "wind_speed": 10.0, "wind_gust": 15.0, "relative_humidity": 70.0,
           "station_level_pressure": 1013.25, "wind_direction": 270.0, "precipitation": 25.4,
           "sky_condition": "08;;08"}
    for e in ["temperature", "dew_point_temperature", "wind_speed", "wind_gust", "relative_humidity",
              "station_level_pressure", "wind_direction", "precipitation"]:
        row[e + "_Source_Code"] = "223"
        row[e + "_Quality_Code"] = "1"
        row[e + "_Report_Type"] = "FM15"
    return row


class BackfillTests(unittest.TestCase):
    def test_zero_row_checkpoint_is_still_idempotent(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = ("abc", 0)
        self.assertEqual(ingest(connection, "BOS", 2020, None, None, "abc", [], None, None),
                         (0, "unchanged"))
        cursor.copy_expert.assert_not_called()
        connection.commit.assert_not_called()

    def test_units_and_standard_time(self):
        r = transform(sample(), "BOS", 2006)
        self.assertEqual(r["datetime"].isoformat(), "2006-01-01T00:53:00")
        self.assertEqual(r["datetime_utc"].isoformat(), "2006-01-01T05:53:00+00:00")
        self.assertEqual(r["temperature"], 32)
        self.assertAlmostEqual(r["wind_speed"], 22.369362921)
        self.assertAlmostEqual(r["station_pressure"], 29.9212524, places=5)
        self.assertEqual(r["precipitation"], 1)
        self.assertEqual(r["wind_direction"], "270")
        self.assertEqual(r["source_metadata"]["fields"]["temperature"]["raw"], 0)

    def test_no_dst_shift_in_summer(self):
        row = sample(); row["DATE"] = "2006-07-01T05:53:00"
        self.assertEqual(transform(row, "BOS", 2006)["datetime"].hour, 0)

    def test_source_dependent_quality_five(self):
        self.assertTrue(rejected("temperature", {"s":"223", "q":"5"}))
        self.assertFalse(rejected("temperature", {"s":"335", "q":"5"}))
        row = sample(); row["temperature_Quality_Code"] = "2"
        r = transform(row, "BOS", 2006)
        self.assertIsNone(r["temperature"])
        self.assertEqual(r["source_metadata"]["fields"]["temperature"]["raw"], 0)

    def test_trace_is_not_invented_amount(self):
        row = sample(); row["precipitation"] = 0; row["precipitation_Measurement_Code"] = "2"
        r = transform(row, "BOS", 2006)
        self.assertEqual(r["precipitation"], 0)
        self.assertTrue(r["precipitation_trace"])

    def test_trace_measurement_code_is_source_dependent(self):
        row = sample()
        row["precipitation_Source_Code"] = "382"
        row["precipitation_Measurement_Code"] = "2"
        r = transform(row, "BOS", 2006)
        self.assertEqual(r["precipitation"], 1)
        self.assertFalse(r["precipitation_trace"])

    def test_rejected_variable_wind_is_not_restored(self):
        row = sample()
        row["wind_direction_Measurement_Code"] = "V"
        row["wind_direction_Quality_Code"] = "2"
        self.assertIsNone(transform(row, "BOS", 2006)["wind_direction"])
        row["wind_direction_Quality_Code"] = "1"
        self.assertEqual(transform(row, "BOS", 2006)["wind_direction"], "VRB")
        row["wind_direction_Report_Type"] = "NSRDB"
        self.assertIsNone(transform(row, "BOS", 2006)["wind_direction"])

    def test_blank_and_special_precip_stay_unknown(self):
        row = sample(); row["precipitation"] = None
        self.assertIsNone(transform(row, "BOS", 2006)["precipitation"])
        row = sample(); row["precipitation_Report_Type"] = "FM16"
        self.assertIsNone(transform(row, "BOS", 2006)["precipitation"])

    def test_accumulation_not_counted_as_hourly(self):
        row = sample(); row["precipitation_Measurement_Code"] = "4"
        r = transform(row, "BOS", 2006)
        self.assertIsNone(r["precipitation"])
        self.assertEqual(r["source_metadata"]["fields"]["precipitation"]["raw"], 25.4)

    def test_synthetic_field_not_mixed_into_real_point(self):
        row = sample(); row["temperature_Report_Type"] = "NSRDB"
        r = transform(row, "BOS", 2006)
        self.assertIsNone(r["temperature"])
        self.assertIsNotNone(r["wind_speed"])
        self.assertEqual(r["source_metadata"]["fields"]["temperature"]["raw"], 0)


if __name__ == "__main__":
    unittest.main()
