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


USERNAME = "mouadziyani"
OUTPUT = Path("dist/activity-graph.svg")
API_URL = "https://api.github.com/search/commits"
WIDTH = 960
HEIGHT = 300


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
    """Render a readable, standalone 12-month monthly commit graph."""
    if len(labels) != 12 or (not unavailable and len(counts) != 12):
        raise ValueError("The activity graph requires twelve monthly buckets")

    left, right, top, bottom = 76, 936, 70, 228
    plot_width, plot_height = right - left, bottom - top
    maximum = max(counts, default=0) if not unavailable else 0
    step = _nice_step(maximum)
    axis_max = max(step * 4, ((maximum + step - 1) // step) * step)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        '<title id="title">Public commit activity for the last twelve months</title>',
        '<desc id="desc">Monthly counts from GitHub commit search by author date. This is not GitHub official contribution data.</desc>',
        '<rect width="100%" height="100%" rx="8" fill="#0d1117"/>',
        '<rect x="0.5" y="0.5" width="959" height="299" rx="8" fill="none" stroke="#30363d"/>',
        '<text x="28" y="30" fill="#f0f6fc" font-family="system-ui,Segoe UI,sans-serif" font-size="17" font-weight="600">Public commit activity - last 12 months</text>',
        '<text x="28" y="50" fill="#8b949e" font-family="system-ui,Segoe UI,sans-serif" font-size="11">GitHub commit search, grouped by author date - not official contribution totals</text>',
    ]

    for tick in range(5):
        value = (axis_max * tick) // 4
        y = bottom - plot_height * tick / 4
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#30363d" stroke-width="1"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" fill="#8b949e" font-family="system-ui,Segoe UI,sans-serif" font-size="10">{value}</text>')

    if unavailable:
        parts.append(f'<text x="{(left + right) / 2}" y="{top + plot_height / 2:.1f}" text-anchor="middle" fill="#c9d1d9" font-family="system-ui,Segoe UI,sans-serif" font-size="14">Activity data unavailable - retry on the next refresh</text>')
    else:
        slot = plot_width / len(labels)
        bar_width = min(34, slot * 0.56)
        if maximum == 0:
            parts.append(f'<text x="{(left + right) / 2}" y="{top + plot_height / 2:.1f}" text-anchor="middle" fill="#8b949e" font-family="system-ui,Segoe UI,sans-serif" font-size="12">No matching public commits in this period</text>')
        for index, (label, count) in enumerate(zip(labels, counts)):
            center = left + slot * (index + 0.5)
            bar_height = plot_height * count / axis_max
            if count:
                x, y = center - bar_width / 2, bottom - bar_height
                parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="3" fill="#a78bfa"><title>{html.escape(label)}: {count} public commits</title></rect>')
            parts.append(f'<text x="{center:.1f}" y="{bottom + 19}" text-anchor="middle" fill="#8b949e" font-family="system-ui,Segoe UI,sans-serif" font-size="10">{html.escape(label)}</text>')

    parts.extend([
        f'<text x="18" y="{(top + bottom) / 2:.1f}" transform="rotate(-90 18 {(top + bottom) / 2:.1f})" text-anchor="middle" fill="#c9d1d9" font-family="system-ui,Segoe UI,sans-serif" font-size="11">Public commits</text>',
        '<text x="506" y="278" text-anchor="middle" fill="#8b949e" font-family="system-ui,Segoe UI,sans-serif" font-size="10">Month (GitHub search results; public repositories only)</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        labels, counts = fetch_monthly_counts(os.environ.get("GITHUB_TOKEN"))
        svg = render_svg(labels, counts)
        print(f"Generated {OUTPUT} from twelve monthly GitHub commit-search counts.")
    except Exception as error:  # Keep the snake publishing job usable during API outages.
        labels = [start.strftime("%b %y") for start, _ in month_windows(dt.date.today())]
        svg = render_svg(labels, [], unavailable=True)
        print(f"Warning: could not retrieve complete activity data: {error}", file=sys.stderr)
    OUTPUT.write_text(svg, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
