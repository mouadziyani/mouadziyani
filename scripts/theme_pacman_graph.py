#!/usr/bin/env python3
"""Re-skin the generated Pac-Man contribution game as an anime boss-battle panel.

abozanona/pacman-contribution-graph only ships GitHub/GitLab colour themes, so
this rewrites its light SVG into the profile palette (paper, ink, one red) and
stages it like the hero art: ink panel, speed lines, slammed title, kanji. Both light and dark outputs get the
same panel, matching the rest of the profile art.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from generate_manga_assets import EASE, INK, MUTED, PAPER, RED, SFX, WHITE, _speed_lines, _svg, _text, _tone


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
    """Return the game recoloured and staged as an anime boss-battle panel."""
    opening = re.match(r'\s*<svg\b[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"[^>]*>', game)
    if not opening:
        raise ValueError("Unexpected Pac-Man SVG: no sized root element")
    width, height = int(opening.group(1)), int(opening.group(2))
    inner = recolor(game[opening.end():].rsplit("</svg>", 1)[0])
    inner = inner.replace(' rx="5"', f' rx="2" stroke="{INK}" stroke-opacity=".12"')

    board_x, board_y = 40, 114
    canvas_w, canvas_h = width + 84, height + 196
    panel_r, panel_b = canvas_w - 14, canvas_h - 14
    panel = f"4,8 {panel_r},4 {panel_r + 2},{panel_b - 4} 2,{panel_b}"
    board_r, board_b = board_x + width + 16, board_y + height + 14
    cx, cy = canvas_w / 2, canvas_h / 2
    bubble_x, bubble_y = board_r - 190, board_b + 28
    css = (
        f".game text{{font-family:{SFX};font-size:13px;letter-spacing:1px}}"
        f".title{{animation:slam .6s {EASE} both;transform-box:fill-box;transform-origin:center}}"
        f".vs{{animation:slam .5s {EASE} .4s both,pulse 1.6s ease-in-out 1.2s infinite;transform-box:fill-box;transform-origin:center}}"
        f".bubble{{animation:pop .5s {EASE} 1s both;transform-box:fill-box;transform-origin:30% 0%}}"
        ".shake{animation:shake .25s steps(2) infinite}"
        f".spin{{transform-origin:{cx:.0f}px {cy:.0f}px;animation:spin 90s linear infinite}}"
        "@keyframes slam{from{transform:scale(2.2);opacity:0}}"
        "@keyframes pop{0%{transform:scale(0);opacity:0}70%{transform:scale(1.08)}}"
        "@keyframes pulse{50%{transform:scale(1.12) rotate(-4deg)}}"
        "@keyframes shake{50%{transform:translate(2px,-1px)}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    body = (
        f'<g id="{MARKER}"/>'
        f"<defs>{_tone('toneLight', PAPER)}"
        f'<clipPath id="panel"><polygon points="{panel}"/></clipPath></defs>'
        f'<polygon points="{panel}" fill="{RED}" transform="translate(10 8)"/>'
        f'<polygon points="{panel}" fill="{INK}"/>'
        '<g clip-path="url(#panel)">'
        f'<g class="spin">{_speed_lines(cx, cy, canvas_w, 110, WHITE, 0.14)}</g>'
        f'<rect width="{canvas_w}" height="{canvas_h}" fill="url(#toneLight)" opacity=".1"/></g>'
        f'<polygon points="{panel}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        # Header: red tag, slammed title, VS badge, sound effect and kanji.
        '<polygon points="20,24 220,18 206,82 26,86" fill="{RED}"/>'.replace("{RED}", RED)
        + _text(118, 64, "BOSS BATTLE", "sfx", 32, WHITE, 'text-anchor="middle" letter-spacing="1.5"')
        + '<g class="title">'
        + _text(250, 80, "PAC-MAN", "sfx", 60, RED, 'letter-spacing="2"')
        + _text(245, 75, "PAC-MAN", "sfx", 60, WHITE, f'letter-spacing="2" stroke="{INK}" stroke-width="2" paint-order="stroke"')
        + "</g>"
        + '<g class="vs">'
        + f'<circle cx="480" cy="56" r="30" fill="{RED}" stroke="{WHITE}" stroke-width="3"/>'
        + _text(480, 68, "VS", "sfx", 32, WHITE, 'text-anchor="middle"')
        + "</g>"
        + '<g class="title">'
        + _text(530, 80, "THE COMMIT GRID", "sfx", 60, RED, 'letter-spacing="2"')
        + _text(525, 75, "THE COMMIT GRID", "sfx", 60, WHITE, f'letter-spacing="2" stroke="{INK}" stroke-width="2" paint-order="stroke"')
        + "</g>"
        + '<g class="shake">'
        + _text(canvas_w - 170, 72, "ゴゴゴ", "jp", 40, RED, f'text-anchor="end" stroke="{INK}" stroke-width="6" paint-order="stroke" transform="rotate(-8 {canvas_w - 240} 60)"')
        + "</g>"
        + _text(canvas_w - 36, 80, "決戦", "jp", 60, RED, 'text-anchor="end"')
        # Arena: the game board on a white page with an ink drop shadow.
        + f'<rect x="{board_x - 10}" y="{board_y - 10}" width="{board_r - board_x + 10}" height="{board_b - board_y + 10}" fill="{RED}"/>'
        + f'<rect x="{board_x - 16}" y="{board_y - 16}" width="{board_r - board_x + 10}" height="{board_b - board_y + 10}" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
        + f'<svg class="game" x="{board_x - 6}" y="{board_y - 4}" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" overflow="visible">{inner}</svg>'
        # Footer: caption and speech bubble.
        + _text(28, board_b + 34, "Every square is a day of contributions - eat the commits, dodge the ghosts", "sans", 13, PAPER, 'fill-opacity=".72"')
        + '<g class="bubble">'
        + f'<polygon points="{bubble_x - 40},{bubble_y - 14} {bubble_x - 70},{bubble_y - 40} {bubble_x - 16},{bubble_y - 22}" fill="{WHITE}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
        + f'<ellipse cx="{bubble_x}" cy="{bubble_y}" rx="176" ry="26" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
        + f'<polygon points="{bubble_x - 44},{bubble_y - 14} {bubble_x - 64},{bubble_y - 34} {bubble_x - 12},{bubble_y - 20}" fill="{WHITE}"/>'
        + _text(bubble_x, bubble_y + 9, "EVERY COMMIT IS ANOTHER REP!", "sfx", 24, RED, 'text-anchor="middle" letter-spacing="1"')
        + "</g>"
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
