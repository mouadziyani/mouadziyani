import datetime as dt
import io
import json
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urlparse

from generate_activity_graph import fetch_monthly_counts, month_windows, render_svg


class ActivityGraphTests(unittest.TestCase):
    def test_month_windows_cover_twelve_months_through_today(self):
        windows = month_windows(dt.date(2026, 10, 18))
        self.assertEqual(len(windows), 12)
        self.assertEqual(windows[0], (dt.date(2025, 11, 1), dt.date(2025, 11, 30)))
        self.assertEqual(windows[-1], (dt.date(2026, 10, 1), dt.date(2026, 10, 18)))

    def test_fetches_api_count_fields_for_each_month(self):
        requests = []

        def opener(request, timeout):
            requests.append((request, timeout))
            payload = {"total_count": len(requests) * 3, "incomplete_results": False}
            return io.BytesIO(json.dumps(payload).encode("utf-8"))

        labels, counts = fetch_monthly_counts("test-token", dt.date(2026, 10, 18), opener)
        self.assertEqual(len(requests), 12)
        self.assertTrue(all(timeout == 20 for _, timeout in requests))
        self.assertEqual(counts, [index * 3 for index in range(1, 13)])
        query = parse_qs(urlparse(requests[0][0].full_url).query)["q"][0]
        self.assertIn("author:mouadziyani", query)
        self.assertIn("author-date:2025-11-01..2025-11-30", query)
        self.assertEqual(labels[0], "Nov 25")

    def test_svg_is_well_formed_and_discloses_measurement_limits(self):
        labels = [f"Month {index}" for index in range(12)]
        svg = render_svg(labels, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("not official contribution totals", svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("https://", svg)

    def test_empty_and_unavailable_states_are_truthful(self):
        labels = [f"Month {index}" for index in range(12)]
        empty_svg = render_svg(labels, [0] * 12)
        unavailable_svg = render_svg(labels, [], unavailable=True)
        ET.fromstring(empty_svg)
        ET.fromstring(unavailable_svg)
        self.assertIn("No matching public commits", empty_svg)
        self.assertIn("Activity data unavailable", unavailable_svg)


if __name__ == "__main__":
    unittest.main()
