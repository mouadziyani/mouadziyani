#!/usr/bin/env python3
"""Re-skin the generated Pac-Man contribution game as a manga panel.

abozanona/pacman-contribution-graph only ships GitHub/GitLab colour themes, so
this rewrites its light SVG into the profile palette (paper, ink, one red) and
frames it like the other README panels. Both light and dark outputs get the
same panel, matching the rest of the profile art.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from generate_manga_assets import INK, MUTED, PAPER, RED, SFX, WHITE, _svg, _text, _tone


DIST = Path("dist")
SOURCE = DIST / "pacman-contribution-graph.svg"
OUTPUTS = [SOURCE, DIST / "pacman-contribution-graph-dark.svg"]
MARKER = "mz-manga-pacman"

# GitHub light theme colour -> profile palette.
COLORS = {
    "#ffffff": WHITE,      # board background
    "#ebedf0": "#ECE6DA",  # empty day
    "#9be9a8": "#F4C1C0",  # contribution levels, light to heavy
    "#40c463": "#E8737A",
    "#30a14e": RED,
    "#216e39": "#7A1018",
    "#000000": INK,        # maze walls
    "#57606a": MUTED,      # month labels
    "yellow": INK,         # Pac-Man
    "red": RED,            # powered-up Pac-Man
}
ATTRIBUTE_PATTERN = re.compile(r'\b(fill|values)="([^"]*)"')
COLOR_PATTERN = re.compile(
    r"(?<![\w#])(" + "|".join(re.escape(color) for color in COLORS) + r")(?!\w)",
    re.IGNORECASE,
)


def recolor(game: str) -> str:
    """Swap theme colours in fills and animation value lists (never inside image data)."""
    def swap(match: re.Match) -> str:
        value = COLOR_PATTERN.sub(lambda color: COLORS[color.group(1).lower()], match.group(2))
        return f'{match.group(1)}="{value}"'

    return ATTRIBUTE_PATTERN.sub(swap, game)


def theme(game: str) -> str:
    """Return the game recoloured and nested inside a manga panel."""
    opening = re.match(r'\s*<svg\b[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"[^>]*>', game)
    if not opening:
        raise ValueError("Unexpected Pac-Man SVG: no sized root element")
    width, height = int(opening.group(1)), int(opening.group(2))
    inner = recolor(game[opening.end():].rsplit("</svg>", 1)[0]).replace(' rx="5"', ' rx="3"')

    pad, header = 26, 72
    panel_w, panel_h = width + pad * 2 + 16, height + header + pad + 16
    canvas_w, canvas_h = panel_w + 12, panel_h + 12
    css = f".game text{{font-family:{SFX};font-size:13px;letter-spacing:1px}}"
    body = (
        f'<g id="{MARKER}"/>'
        f"<defs>{_tone('tone', INK)}</defs>"
        f'<rect x="12" y="12" width="{panel_w}" height="{panel_h}" fill="{RED}"/>'
        f'<rect x="4" y="4" width="{panel_w}" height="{panel_h}" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="4" y="4" width="{panel_w}" height="{panel_h}" fill="url(#tone)" opacity=".1"/>'
        f'<polygon points="20,22 402,16 394,64 26,68" fill="{INK}"/>'
        + _text(40, 54, "BOSS FIGHT: PAC-MAN", "sfx", 30, WHITE, 'letter-spacing="1.5"')
        + _text(424, 40, "VS. a year of commits", "sans", 15, INK, 'font-weight="700"')
        + _text(424, 59, "Every square is a day of contributions - the ghosts are still chasing", "sans", 12, MUTED)
        + f'<rect x="20" y="{header + 10}" width="{width + pad + 8}" height="{height + 20}" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>'
        + f'<svg class="game" x="{pad + 4}" y="{header + 20}" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" overflow="visible">{inner}</svg>'
    )
    return _svg(canvas_w, canvas_h, "Pac-Man eating a year of GitHub contributions", body, css)


def main() -> int:
    if not SOURCE.exists():
        print(f"Warning: {SOURCE} not found; skipping Pac-Man theming", file=sys.stderr)
        return 0
    game = SOURCE.read_text(encoding="utf-8")
    if MARKER in game:
        print(f"{SOURCE} is already themed; skipping")
        return 0
    themed = theme(game)
    for output in OUTPUTS:
        output.write_text(themed, encoding="utf-8")
        print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
