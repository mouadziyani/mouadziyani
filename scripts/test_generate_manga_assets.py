import unittest
import xml.etree.ElementTree as ET

from generate_manga_assets import ARCS, CHAPTERS, OUTPUT_DIR, build


class MangaAssetTests(unittest.TestCase):
    def test_every_asset_is_well_formed_self_contained_svg(self):
        assets = build()
        self.assertEqual(len(assets), 6 + len(CHAPTERS) + len(ARCS))
        for name, svg in assets.items():
            with self.subTest(name=name):
                root = ET.fromstring(svg)
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}title"))
                self.assertNotIn("<script", svg)
                self.assertNotIn("https://", svg)

    def test_committed_assets_match_the_generator(self):
        for name, svg in build().items():
            with self.subTest(name=name):
                self.assertEqual((OUTPUT_DIR / name).read_text(encoding="utf-8"), svg)


if __name__ == "__main__":
    unittest.main()
