#!/usr/bin/env python3
"""Build a self-contained SVG of public GitHub commit search activity."""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from generate_manga_assets import EASE, INK, MUTED, PAPER, RED, WHITE, _svg, _text, _tone


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


def render_svg(labels: list[str], counts: list[int], unavailable: bool = False) -> str:
    """Render the 12-month commit graph as a manga panel matching the profile art."""
    if len(labels) != 12 or (not unavailable and len(counts) != 12):
        raise ValueError("The activity graph requires twelve monthly buckets")

    left, right, top, bottom = 84, 962, 116, 268
    plot_width, plot_height = right - left, bottom - top
    maximum = max(counts, default=0) if not unavailable else 0
    step = _nice_step(maximum)
    axis_max = max(step * 4, ((maximum + step - 1) // step) * step)
    css = (
        "".join(f".b{i}{{animation:grow .8s {EASE} {0.2 + i * 0.06:.2f}s both}}" for i in range(12))
        + ".bar{transform-box:fill-box;transform-origin:50% 100%}"
        "@keyframes grow{from{transform:scaleY(0)}}"
    )
    parts = [
        f"<defs>{_tone('tone', INK)}</defs>",
        f'<rect x="12" y="12" width="986" height="314" fill="{RED}"/>',
        f'<rect x="4" y="4" width="986" height="314" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>',
        '<rect x="4" y="4" width="986" height="314" fill="url(#tone)" opacity=".1"/>',
        f'<polygon points="20,22 338,16 330,64 26,68" fill="{INK}"/>',
        _text(40, 54, "COMMIT POWER LEVELS", "sfx", 30, WHITE, 'letter-spacing="1.5"'),
        _text(360, 40, "Public commits · last 12 months", "sans", 15, INK, 'font-weight="700"'),
        _text(360, 59, "GitHub commit search by author date - not official contribution totals", "sans", 12, MUTED),
        f'<rect x="20" y="84" width="962" height="224" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>',
    ]

    for tick in range(5):
        value = (axis_max * tick) // 4
        y = bottom - plot_height * tick / 4
        dash = "" if tick == 0 else ' stroke-dasharray="6 6" stroke-opacity=".25"'
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{INK}" stroke-width="{3 if tick == 0 else 1.5}"{dash}/>')
        parts.append(_text(left - 12, round(y + 5, 1), str(value), "sfx", 15, MUTED, 'text-anchor="end"'))

    middle = round(top + plot_height / 2, 1)
    if unavailable:
        parts.append(_text((left + right) / 2, middle, "Activity data unavailable - retry on the next refresh", "sfx", 24, RED, 'text-anchor="middle" letter-spacing="1"'))
    else:
        slot = plot_width / len(labels)
        bar_width = min(40, slot * 0.56)
        if maximum == 0:
            parts.append(_text((left + right) / 2, middle, "No matching public commits in this period", "sfx", 24, MUTED, 'text-anchor="middle" letter-spacing="1"'))
        for index, (label, count) in enumerate(zip(labels, counts)):
            center = left + slot * (index + 0.5)
            bar_height = plot_height * count / axis_max
            if count:
                x, y = center - bar_width / 2, bottom - bar_height
                peak = count == maximum
                parts.append(
                    f'<g class="bar b{index}">'
                    f'<rect x="{x + 5:.1f}" y="{y + 5:.1f}" width="{bar_width:.1f}" height="{max(bar_height - 5, 0):.1f}" fill="{INK}"/>'
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{RED}" stroke="{INK}" stroke-width="3">'
                    f"<title>{html.escape(label)}: {count} public commits</title></rect>"
                    + _text(round(center, 1), round(y - 9, 1), str(count), "sfx", 18, RED if peak else INK, 'text-anchor="middle"')
                    + "</g>"
                )
            parts.append(_text(round(center, 1), bottom + 24, label.upper(), "sfx", 16, INK, 'text-anchor="middle" letter-spacing="1"'))

    parts.append(_text(44, (top + bottom) / 2, "COMMITS", "sfx", 15, INK, f'text-anchor="middle" letter-spacing="2" transform="rotate(-90 44 {(top + bottom) / 2})"'))
    body = "".join(parts)
    return _svg(1000, 330, "Public commit activity for the last twelve months", body, css)


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
