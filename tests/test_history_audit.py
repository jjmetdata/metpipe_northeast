"""Tests for denominator and source-role handling in the research audit."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


PATH = Path(__file__).resolve().parents[1] / "analysis/audit_station_history.py"
SPEC = importlib.util.spec_from_file_location("history_audit", str(PATH))
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class HistoryAuditTests(unittest.TestCase):
    def test_missing_years_stay_in_expected_hour_denominator(self):
        fields = {e: {"good_hours": 8784, "present_hours": 8784, "good_pct": 100}
                  for e in AUDIT.CORE}
        annual = {("TEST", 2024): {"year": 2024, "fields": fields}}
        windows = AUDIT.hourly_windows("TEST", annual, {("TEST", 2024)})
        by_start = {r["start_year"]: r for r in windows}
        for start, hours in [(2005, 175320), (1995, 262992), (1990, 306816)]:
            row = by_start[start]
            self.assertEqual(row["expected_hours"], hours)
            self.assertEqual(row["years_read"], 1)
            self.assertEqual(row["years_all_core95"], 1)
            self.assertLess(row["lowest_core_pct"], 6)
            self.assertEqual(len(row["unavailable_years"]), row["years_expected"] - 1)

    def test_missing_core_field_does_not_pass(self):
        annual = {("TEST", 2024): {"year": 2024, "fields": {}}}
        row = AUDIT.hourly_windows("TEST", annual, {("TEST", 2024)})[0]
        self.assertEqual(row["lowest_core_pct"], 0)
        self.assertEqual(row["years_all_core95"], 0)

    def test_archive_error_and_no_inventory_are_distinct(self):
        annual = {("TEST", 2024): {"year": 2024, "status": "archive_file_unavailable"}}
        row = AUDIT.hourly_windows("TEST", annual, {("TEST", 2024)})[0]
        self.assertEqual(row["unavailable_years"]["2024"], "archive_file_unavailable")
        self.assertEqual(row["unavailable_years"]["2023"], "no_matched_inventory_entry")

    def test_trace_zero_is_present_and_flagged_daily_values_are_excluded(self):
        sid = "USC00000001"
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            lines = []
            for element in ["TMAX", "TMIN", "PRCP"]:
                blocks = []
                for day in range(31):
                    value, measure, quality = 0, "T" if element == "PRCP" else " ", " "
                    if element == "TMAX" and day == 0:
                        value = -9999
                    if element == "TMAX" and day == 1:
                        quality = "X"
                    blocks.append("%5d%s%s%s" % (value, measure, quality, "0"))
                lines.append(sid + "202401" + element + "".join(blocks) + "\n")
            (cache / ("metpipe_broad_daily_%s.dly" % sid)).write_text("".join(lines))
            result = AUDIT.daily_windows(sid, cache)
            row = result["windows"][0]
            self.assertEqual(result["status"], "read")
            self.assertAlmostEqual(row["elements"]["PRCP"]["accepted_day_pct"],
                                   round(100 * 31 / row["expected_days"], 3))
            self.assertAlmostEqual(row["elements"]["TMAX"]["accepted_day_pct"],
                                   round(100 * 29 / row["expected_days"], 3))


if __name__ == "__main__":
    unittest.main()
