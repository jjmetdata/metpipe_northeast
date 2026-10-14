import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import station_map
from export_station_map import build_svg


class StationMapTests(unittest.TestCase):
    def test_checked_network_contains_original_twenty(self):
        stations = station_map.load_network()
        self.assertEqual(len(stations), 20)
        self.assertEqual({s["code"] for s in stations},
                         set("ALB AUG BAF BDL BOS BTV DDH EWB HVN HYA JFK LEB MHT MVY ORH PVC PVD PWM PYM UUU".split()))

    def test_fresh_clone_without_raw_data_uses_checked_coordinates(self):
        with TemporaryDirectory() as directory, patch.object(station_map, "RAW_DIR", Path(directory)):
            self.assertEqual(station_map.load_stations(), station_map.load_network())

    def test_static_map_has_twenty_equal_circle_markers_and_no_scripts(self):
        root = ET.fromstring(build_svg())
        ns = {"svg":"http://www.w3.org/2000/svg"}
        markers = root.findall(".//svg:g[@class='station']", ns)
        self.assertEqual(len(markers), 20)
        self.assertTrue(all(m.find("svg:circle", ns).get("r") == "8" for m in markers))
        self.assertEqual({m.get("data-code") for m in markers},
                         {s["code"] for s in station_map.load_network()})
        self.assertEqual(root.findall(".//svg:script", ns), [])
        self.assertEqual(root.findall(".//svg:image", ns), [])


if __name__ == "__main__":
    unittest.main()
