#!/usr/bin/env python3
"""Build a self-contained SVG of public GitHub commit search activity."""

from __future__ import annotations

import datetime as dt
import html
import json
import math
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from generate_manga_assets import EASE, INK, PAPER, RED, WHITE, _speed_lines, _svg, _text, _tone


USERNAME = "mouadziyani"
OUTPUT = Path("dist/activity-graph.svg")
API_URL = "https://api.github.com/search/commits"


def month_windows(today: dt.date) -> list[tuple[dt.date, dt.date]]:
    """Return the current and preceding eleven calendar month date ranges."""
    first = today.replace(day=1)
    starts = []
    year, month = first.year, first.month
    for _ in range(12):
        starts.append(dt.date(year, month, 1))
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    starts.reverse()
    return [
        (start, starts[index + 1] - dt.timedelta(days=1) if index < 11 else today)
        for index, start in enumerate(starts)
    ]


def _request_count(start: dt.date, end: dt.date, token: str | None, opener=urlopen) -> int:
    query = f"author:{USERNAME} author-date:{start.isoformat()}..{end.isoformat()}"
    url = f"{API_URL}?{urlencode({'q': query, 'per_page': '1'})}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "mouadziyani-profile-activity-graph",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)

    for attempt in range(3):
        try:
            with opener(request, timeout=20) as response:
                payload = json.load(response)
            if payload.get("incomplete_results"):
                raise RuntimeError("GitHub returned incomplete commit search results")
            count = payload.get("total_count")
            if not isinstance(count, int) or count < 0:
                raise ValueError("GitHub returned an invalid total_count")
            return count
        except HTTPError as error:
            if attempt == 2 or (error.code < 500 and error.code != 429):
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        if attempt < 2:
            time.sleep(2**attempt)
    raise RuntimeError("GitHub API request failed")


def fetch_monthly_counts(
    token: str | None = None,
    today: dt.date | None = None,
    opener=urlopen,
) -> tuple[list[str], list[int]]:
    today = today or dt.date.today()
    windows = month_windows(today)
    labels = [start.strftime("%b %y") for start, _ in windows]
    counts = [_request_count(start, end, token, opener) for start, end in windows]
    return labels, counts


def _nice_step(maximum: int) -> int:
    raw = max(maximum, 1) / 4
    magnitude = 1
    while magnitude * 10 <= raw:
        magnitude *= 10
    for factor in (1, 2, 5, 10):
        step = factor * magnitude
        if step >= raw:
            return step
    return magnitude * 10


def _burst(cx: float, cy: float, outer: float, inner: float, spikes: int = 12) -> str:
    """Spiky manga impact burst as polygon points."""
    points = []
    for index in range(spikes * 2):
        radius = outer if index % 2 == 0 else inner
        angle = math.pi * index / spikes - math.pi / 2
        points.append(f"{cx + radius * math.cos(angle):.1f},{cy + radius * math.sin(angle):.1f}")
    return " ".join(points)


def render_svg(labels: list[str], counts: list[int], unavailable: bool = False) -> str:
    """Render the 12-month commit graph as an anime "power level" panel."""
    if len(labels) != 12 or (not unavailable and len(counts) != 12):
        raise ValueError("The activity graph requires twelve monthly buckets")

    left, right, top, bottom = 78, 892, 178, 332
    plot_width, plot_height = right - left, bottom - top
    maximum = max(counts, default=0) if not unavailable else 0
    step = _nice_step(maximum)
    axis_max = max(step * 4, ((maximum + step - 1) // step) * step)
    if maximum * 5 > axis_max * 4:  # keep the peak burst clear of the title
        axis_max += step
    panel = "4,6 986,2 988,384 2,388"
    css = (
        "".join(f".b{i}{{animation:grow .8s {EASE} {0.3 + i * 0.07:.2f}s both}}" for i in range(12))
        + ".bar{transform-box:fill-box;transform-origin:50% 100%}"
        f".peak{{animation:pop .5s {EASE} 1.4s both,pulse 1.6s ease-in-out 2s infinite;transform-box:fill-box;transform-origin:center}}"
        f".title{{animation:slam .6s {EASE} both;transform-box:fill-box;transform-origin:center}}"
        f".bubble{{animation:pop .5s {EASE} .9s both;transform-box:fill-box;transform-origin:20% 100%}}"
        ".spin{transform-origin:480px 260px;animation:spin 80s linear infinite}"
        "@keyframes grow{from{transform:scaleY(0)}}"
        "@keyframes slam{from{transform:scale(2.2);opacity:0}}"
        "@keyframes pop{0%{transform:scale(0);opacity:0}70%{transform:scale(1.1)}}"
        "@keyframes pulse{50%{transform:scale(1.1) rotate(-4deg)}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    parts = [
        f"<defs>{_tone('toneLight', PAPER)}"
        f'<clipPath id="panel"><polygon points="{panel}"/></clipPath>'
        '<radialGradient id="fade" cx="480" cy="260" r="560" gradientUnits="userSpaceOnUse">'
        '<stop offset="0.2" stop-color="#000"/><stop offset="0.9" stop-color="#fff"/></radialGradient>'
        '<mask id="edge"><rect width="1000" height="400" fill="url(#fade)"/></mask></defs>',
        f'<polygon points="{panel}" fill="{RED}" transform="translate(10 8)"/>',
        f'<polygon points="{panel}" fill="{INK}"/>',
        '<g clip-path="url(#panel)">'
        f'<g mask="url(#edge)"><g class="spin">{_speed_lines(480, 260, 760, 80, WHITE, 0.16)}</g></g>'
        '<rect width="1000" height="400" fill="url(#toneLight)" opacity=".1"/></g>',
        f'<polygon points="{panel}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>',
        f'<rect x="24" y="22" width="166" height="26" fill="{RED}"/>',
        _text(34, 40, "CH. 05 · TRAINING LOG", "sans", 12, WHITE, 'font-weight="700" letter-spacing="1.5"'),
        '<g class="title">'
        + _text(30, 106, "POWER LEVEL", "sfx", 60, RED, 'letter-spacing="2"')
        + _text(25, 101, "POWER LEVEL", "sfx", 60, WHITE, f'letter-spacing="2" stroke="{INK}" stroke-width="2" paint-order="stroke"')
        + "</g>",
        _text(28, 130, "Public commits, last 12 months - GitHub commit search by author date, not official contribution totals", "sans", 13, PAPER, 'fill-opacity=".72"'),
        "".join(_text(950, 220 + 66 * i, ch, "jp", 60, RED, 'text-anchor="middle"') for i, ch in enumerate("修行")),
    ]

    total = sum(counts) if not unavailable else 0
    shout = "SIGNAL LOST!" if unavailable else f"TOTAL POWER: {total}!"
    parts.append(
        '<g class="bubble">'
        f'<polygon points="652,86 618,116 680,94" fill="{WHITE}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
        f'<ellipse cx="790" cy="62" rx="178" ry="42" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
        f'<polygon points="650,82 684,92 676,74" fill="{WHITE}"/>'
        + _text(790, 52, "The scouter is reading...", "sans", 13, INK, 'font-weight="700" text-anchor="middle"')
        + _text(790, 82, shout, "sfx", 28, RED, 'text-anchor="middle" letter-spacing="1"')
        + "</g>"
    )

    for value in range(0, axis_max + 1, step):
        y = bottom - plot_height * value / axis_max
        line = f'stroke="{PAPER}" stroke-width="3"' if value == 0 else f'stroke="{PAPER}" stroke-opacity=".2" stroke-width="1.5" stroke-dasharray="6 6"'
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" {line}/>')
        parts.append(_text(left - 12, round(y + 5, 1), str(value), "sfx", 15, PAPER, 'text-anchor="end" fill-opacity=".6"'))

    middle = round(top + plot_height / 2, 1)
    if unavailable:
        parts.append(_text((left + right) / 2, middle, "Activity data unavailable - retry on the next refresh", "sfx", 26, RED, 'text-anchor="middle" letter-spacing="1"'))
    else:
        slot = plot_width / len(labels)
        bar_width = min(38, slot * 0.54)
        if maximum == 0:
            parts.append(_text((left + right) / 2, middle, "No matching public commits in this period", "sfx", 26, PAPER, 'text-anchor="middle" letter-spacing="1"'))
        peak_index = counts.index(maximum) if maximum else -1
        for index, (label, count) in enumerate(zip(labels, counts)):
            center = left + slot * (index + 0.5)
            bar_height = plot_height * count / axis_max
            if count:
                x, y = center - bar_width / 2, bottom - bar_height
                parts.append(
                    f'<g class="bar b{index}">'
                    f'<rect x="{x + 6:.1f}" y="{y + 6:.1f}" width="{bar_width:.1f}" height="{max(bar_height - 6, 0):.1f}" fill="#7A1018"/>'
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{RED}" stroke="{WHITE}" stroke-width="2.5">'
                    f"<title>{html.escape(label)}: {count} public commits</title></rect>"
                    f'<rect x="{x + 5:.1f}" y="{y + 5:.1f}" width="4" height="{max(bar_height - 10, 0):.1f}" fill="{WHITE}" fill-opacity=".45"/>'
                    + ("" if index == peak_index else _text(round(center, 1), round(y - 10, 1), str(count), "sfx", 18, WHITE, 'text-anchor="middle"'))
                    + "</g>"
                )
                if index == peak_index:
                    cy = round(y - 30, 1)
                    parts.append(
                        '<g class="peak">'
                        f'<polygon points="{_burst(center, cy, 32, 21)}" fill="{WHITE}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
                        + _text(round(center, 1), round(cy + 8, 1), str(count), "sfx", 24, RED, 'text-anchor="middle"')
                        + _text(round(center + 30, 1), round(cy - 8, 1), "MAX!", "sfx", 18, RED, f'stroke="{INK}" stroke-width="4" paint-order="stroke" transform="rotate(-12 {center + 30:.1f} {cy - 8:.1f})"')
                        + "</g>"
                    )
            parts.append(_text(round(center, 1), bottom + 26, label.upper(), "sfx", 17, PAPER, 'text-anchor="middle" letter-spacing="1"'))

    return _svg(1000, 400, "Public commit activity for the last twelve months", "".join(parts), css)


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        labels, counts = fetch_monthly_counts(os.environ.get("GITHUB_TOKEN"))
        svg = render_svg(labels, counts)
        print(f"Generated {OUTPUT} from twelve monthly GitHub commit-search counts.")
    except Exception as error:  # Keep Pac-Man publishing usable during API outages.
        labels = [start.strftime("%b %y") for start, _ in month_windows(dt.date.today())]
        svg = render_svg(labels, [], unavailable=True)
        print(f"Warning: could not retrieve complete activity data: {error}", file=sys.stderr)
    OUTPUT.write_text(svg, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
