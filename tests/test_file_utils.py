from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from file_utils import discover_weather_files, parse_weather_file


class WeatherFileTests(unittest.TestCase):
    def test_parse_cleaned_file(self):
        weather_file = parse_weather_file(
            Path("bos_hourly_2025_cleaned.csv"),
            cleaned=True,
        )

        self.assertEqual(weather_file.station, "BOS")
        self.assertEqual(weather_file.year, 2025)

    def test_discovery_retains_multiple_years_for_same_station(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_directory = Path(temporary_directory)
            for filename in (
                "bos_hourly_2024_cleaned.csv",
                "bos_hourly_2025_cleaned.csv",
                "bos_hourly_2026_cleaned.csv",
                "alb_hourly_2024_cleaned.csv",
            ):
                (data_directory / filename).touch()

            discovered = discover_weather_files(data_directory, cleaned=True)
            station_years = [
                (weather_file.station, weather_file.year)
                for weather_file in discovered
            ]

        self.assertEqual(
            station_years,
            [
                ("ALB", 2024),
                ("BOS", 2024),
                ("BOS", 2025),
                ("BOS", 2026),
            ],
        )

    def test_discovery_ignores_unsupported_names(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_directory = Path(temporary_directory)
            (data_directory / "bos_hourly_latest.csv").touch()
            (data_directory / "bos_hourly_2024.csv").touch()
            (data_directory / "notes.csv").touch()

            discovered = discover_weather_files(data_directory, cleaned=False)

        self.assertEqual(len(discovered), 1)
        self.assertEqual(discovered[0].station, "BOS")
        self.assertEqual(discovered[0].year, 2024)

    def test_discovery_finds_year_folders_and_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_directory = Path(temporary_directory)
            year_directory = data_directory / "2024"
            year_directory.mkdir()
            nested_file = year_directory / "bos_hourly_2024.csv"
            nested_file.touch()

            discovered = discover_weather_files(data_directory, cleaned=False)
            self.assertEqual([item.path for item in discovered], [nested_file])

            (data_directory / "bos_hourly_2024.csv").touch()
            with self.assertRaisesRegex(ValueError, "Duplicate BOS 2024"):
                discover_weather_files(data_directory, cleaned=False)

    def test_discovery_rejects_wrong_year_folder(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_directory = Path(temporary_directory)
            year_directory = data_directory / "2023"
            year_directory.mkdir()
            (year_directory / "bos_hourly_2024.csv").touch()

            with self.assertRaisesRegex(ValueError, "must be directly"):
                discover_weather_files(data_directory, cleaned=False)


if __name__ == "__main__":
    unittest.main()
