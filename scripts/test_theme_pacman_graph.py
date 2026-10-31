import unittest
import xml.etree.ElementTree as ET

from theme_pacman_graph import MARKER, recolor, theme


GAME = (
    '<svg width="40" height="20" xmlns="http://www.w3.org/2000/svg">'
    '<rect width="100%" height="100%" fill="#ffffff"/>'
    '<image href="data:image/png;base64,yellow+red/AAAA" width="20" height="20"/>'
    '<rect x="0" y="0" width="20" height="20" rx="5" fill="#ebedf0">'
    '<animate attributeName="fill" values="#40c463;#ebedf0;#ebedf0"/></rect>'
    '<path id="pacman" d="M 0,0 Z" fill="yellow"><animate attributeName="fill" values="yellow;red"/></path>'
    '</svg>'
)


class PacmanThemeTests(unittest.TestCase):
    def test_recolors_attributes_but_not_embedded_images(self):
        result = recolor(GAME)
        self.assertNotIn('fill="yellow"', result)
        self.assertNotIn("#40c463", result)
        self.assertIn('values="#121212;#D92632"', result)
        self.assertIn("base64,yellow+red/AAAA", result)

    def test_wraps_game_in_well_formed_panel(self):
        svg = theme(GAME)
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn(MARKER, svg)
        self.assertIn('viewBox="0 0 40 20"', svg)
        self.assertNotIn("https://", svg)


if __name__ == "__main__":
    unittest.main()
