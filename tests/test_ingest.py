from pathlib import Path
import csv
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from file_utils import WeatherDataFile
from ingest import prepare_records


class IngestPreparationTests(unittest.TestCase):
    def test_prepare_records_preserves_station_and_year(self):
        headers = [
            "DATE",
            "REPORT_TYPE",
            "HourlyDryBulbTemperature",
            "HourlyDewPointTemperature",
            "HourlyRelativeHumidity",
            "HourlyPrecipitation",
            "HourlySkyConditions",
            "HourlyStationPressure",
            "HourlyWindDirection",
            "HourlyWindSpeed",
            "HourlyWindGustSpeed",
        ]
        row = [
            "2025-01-01 00:54:00",
            "FM-15",
            "32",
            "28",
            "85",
            "T",
            "BKN",
            "29.90",
            "270",
            "8",
            "15",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "bos_hourly_2025_cleaned.csv"
            with path.open("w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)
                special_report = row.copy()
                special_report[1] = "FM-16"
                special_report[5] = "0.03"
                writer.writerow(special_report)
                writer.writerow(row)
                writer.writerow(row)  # Duplicate station-time should be removed.

            records = prepare_records(
                WeatherDataFile(path=path, station="BOS", year=2025)
            )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["station"], "BOS")
        self.assertEqual(records[0]["datetime"].year, 2025)
        self.assertEqual(records[0]["precipitation"], 0.001)
        self.assertEqual(records[0]["report_type"], "FM-15")

    def test_prepare_records_converts_missing_numbers_to_null(self):
        headers = [
            "DATE", "REPORT_TYPE", "HourlyDryBulbTemperature", "HourlyDewPointTemperature",
            "HourlyRelativeHumidity", "HourlyPrecipitation",
            "HourlySkyConditions", "HourlyStationPressure",
            "HourlyWindDirection", "HourlyWindSpeed", "HourlyWindGustSpeed",
        ]
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "pvc_hourly_2020_cleaned.csv"
            with path.open("w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)
                writer.writerow(["2020-01-01 00:00:00", "FM-15", "", "", "", "", "", "", "", "", ""])

            records = prepare_records(WeatherDataFile(path, "PVC", 2020))

        self.assertIsNone(records[0]["temperature"])
        self.assertIsNone(records[0]["precipitation"])


if __name__ == "__main__":
    unittest.main()
