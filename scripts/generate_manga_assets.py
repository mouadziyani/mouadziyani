#!/usr/bin/env python3
"""Build the manga-style SVG panels used by the profile README.

The look follows mouadziyani.com: paper white, ink black and one red accent,
with screentone, speed lines, speech bubbles and chapter title cards.
Every SVG is self-contained (embedded font and image) so GitHub can render it.
"""

from __future__ import annotations

import base64
import math
import textwrap
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "src" / "svg"
FONT = ROOT / "src" / "fonts" / "Bangers-subset.woff2"
PORTRAIT = ROOT / "src" / "img" / "mouad-portrait.jpg"

PAPER = "#F3EFE6"
WHITE = "#FFFDF8"
INK = "#121212"
MUTED = "#45423D"
RED = "#D92632"

SFX = "'MZBangers','Bangers',Impact,'Arial Black',sans-serif"
SANS = "'Space Grotesk',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif"
JP = "'Yu Gothic','Hiragino Kaku Gothic ProN','Noto Sans JP','Noto Sans CJK JP','Meiryo',sans-serif"
EASE = "cubic-bezier(.22,1,.36,1)"


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _style(extra: str = "") -> str:
    return (
        "<style>"
        f"@font-face{{font-family:'MZBangers';src:url(data:font/woff2;base64,{_b64(FONT)}) format('woff2')}}"
        f".sfx{{font-family:{SFX}}}.sans{{font-family:{SANS}}}.jp{{font-family:{JP};font-weight:900}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        f"{extra}</style>"
    )


def _tone(pattern_id: str, color: str, size: int = 7, radius: float = 1.15) -> str:
    """Screentone dot pattern."""
    return (
        f'<pattern id="{pattern_id}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">'
        f'<circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="{color}"/></pattern>'
    )


def _speed_lines(cx: float, cy: float, radius: float, count: int, color: str, opacity: float) -> str:
    """Radial manga speed lines as thin wedges around a centre point."""
    wedges = []
    for index in range(count):
        angle = 2 * math.pi * index / count
        spread = math.pi / count * 0.35
        x1, y1 = cx + radius * math.cos(angle - spread), cy + radius * math.sin(angle - spread)
        x2, y2 = cx + radius * math.cos(angle + spread), cy + radius * math.sin(angle + spread)
        wedges.append(f"M{cx:.0f} {cy:.0f}L{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}Z")
    return f'<path d="{"".join(wedges)}" fill="{color}" fill-opacity="{opacity}"/>'


def _svg(width: int, height: int, title: str, body: str, css: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title>{_style(css)}{body}</svg>\n"
    )


def _text(x: float, y: float, content: str, cls: str, size: float, fill: str, extra: str = "") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" {extra}>{escape(content)}</text>'


def render_hero() -> str:
    panel_a = "24,24 560,24 480,576 24,576"
    panel_b = "580,24 976,24 976,330 536,330"
    panel_c = "530,350 976,350 976,576 500,576"
    css = (
        f".pa{{animation:inL .8s {EASE} both}}.pb{{animation:inT .8s {EASE} .15s both}}"
        f".pc{{animation:inR .8s {EASE} .3s both}}"
        f".title{{animation:slam .6s {EASE} .6s both;transform-box:fill-box;transform-origin:center}}"
        f".bubble{{animation:pop .5s {EASE} 1.1s both;transform-box:fill-box;transform-origin:70% 0%}}"
        f".don{{animation:slam .45s {EASE} 1.5s both,pulse 1.6s ease-in-out 2.2s infinite;transform-box:fill-box;transform-origin:center}}"
        ".spin{transform-origin:250px 290px;animation:spin 70s linear infinite}"
        ".blink{animation:blink 1.2s steps(2) infinite}"
        "@keyframes inL{from{transform:translateX(-70px);opacity:0}}"
        "@keyframes inT{from{transform:translateY(-60px);opacity:0}}"
        "@keyframes inR{from{transform:translateX(70px);opacity:0}}"
        "@keyframes slam{from{transform:scale(2.6);opacity:0}}"
        "@keyframes pop{0%{transform:scale(0);opacity:0}70%{transform:scale(1.08)}}"
        "@keyframes pulse{50%{transform:scale(1.08) rotate(-2deg)}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        "@keyframes blink{50%{opacity:0}}"
    )
    defs = (
        "<defs>"
        f"{_tone('tone', INK)}{_tone('toneLight', PAPER)}"
        f'<clipPath id="clipA"><polygon points="{panel_a}"/></clipPath>'
        f'<clipPath id="clipB"><polygon points="{panel_b}"/></clipPath>'
        f'<clipPath id="clipC"><polygon points="{panel_c}"/></clipPath>'
        '<filter id="ink"><feColorMatrix type="saturate" values="0"/>'
        '<feComponentTransfer><feFuncR type="linear" slope="1.3" intercept="-0.12"/>'
        '<feFuncG type="linear" slope="1.3" intercept="-0.12"/><feFuncB type="linear" slope="1.3" intercept="-0.12"/>'
        "</feComponentTransfer></filter>"
        '<radialGradient id="fade" cx="250" cy="290" r="420" gradientUnits="userSpaceOnUse">'
        '<stop offset="0.38" stop-color="#000"/><stop offset="0.75" stop-color="#fff"/></radialGradient>'
        '<mask id="edge"><rect width="1000" height="600" fill="url(#fade)"/></mask>'
        "</defs>"
    )
    a = (
        '<g class="pa">'
        f'<polygon points="{panel_a}" fill="{INK}"/>'
        '<g clip-path="url(#clipA)">'
        f'<image x="-150" y="24" width="828" height="552" preserveAspectRatio="xMidYMid slice" filter="url(#ink)" '
        f'href="data:image/jpeg;base64,{_b64(PORTRAIT)}"/>'
        f'<g mask="url(#edge)"><g class="spin">{_speed_lines(250, 290, 760, 90, WHITE, 0.55)}</g></g>'
        "</g>"
        f'<polygon points="{panel_a}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        f'<rect x="40" y="40" width="132" height="30" fill="{RED}"/>'
        + _text(52, 62, "CH. 00 · PROLOGUE", "sans", 13, WHITE, 'font-weight="700" letter-spacing="1.5"')
        + "</g>"
    )
    b = (
        '<g class="pb">'
        f'<polygon points="{panel_b}" fill="{WHITE}"/>'
        '<g clip-path="url(#clipB)">'
        f'<circle cx="905" cy="95" r="92" fill="{RED}"/>'
        f'<rect x="700" y="160" width="300" height="200" fill="url(#tone)" opacity=".22"/>'
        "</g>"
        f'<polygon points="{panel_b}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        + _text(600, 70, "A MOUAD ZIYANI PRODUCTION", "sans", 13, INK, 'font-weight="700" letter-spacing="4"')
        + '<g class="title">'
        + _text(598, 130, "THE", "sfx", 44, RED, 'letter-spacing="3"')
        + _text(596, 226, "DEVELOPER", "sfx", 88, RED, 'letter-spacing="1"')
        + _text(590, 220, "DEVELOPER", "sfx", 88, INK, f'letter-spacing="1" stroke="{WHITE}" stroke-width="2" paint-order="stroke"')
        + "</g>"
        + f'<rect x="586" y="246" width="130" height="8" fill="{RED}"/>'
        + _text(576, 292, "Full-Stack Web & Mobile Developer", "sans", 19, INK, 'font-weight="700"')
        + "</g>"
    )
    c = (
        '<g class="pc">'
        f'<polygon points="{panel_c}" fill="{INK}"/>'
        f'<g clip-path="url(#clipC)"><rect x="500" y="350" width="480" height="230" fill="url(#toneLight)" opacity=".14"/></g>'
        f'<polygon points="{panel_c}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
        + _text(545, 398, "VOL. 01 — THE YOUCODE ARC", "sfx", 28, RED, 'letter-spacing="1.5"')
        + _text(545, 436, "Java · Spring Boot · PHP · Laravel", "sans", 16, PAPER, 'font-weight="600"')
        + _text(545, 462, "JavaScript · React · React Native", "sans", 16, PAPER, 'font-weight="600"')
        + _text(545, 496, "Oujda, Morocco — YouCode Nador · UM6P", "sans", 14, PAPER, 'fill-opacity=".72"')
        + '<g class="blink">' + _text(545, 548, "READ THE STORY ▼", "sfx", 22, WHITE, 'letter-spacing="2"') + "</g>"
        + "".join(_text(928, 410 + 58 * i, ch, "jp", 52, RED, 'text-anchor="middle"') for i, ch in enumerate("開発者"))
        + "</g>"
    )
    bubble = (
        '<g class="bubble">'
        f'<polygon points="300,452 352,392 336,456" fill="{WHITE}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
        f'<ellipse cx="250" cy="494" rx="212" ry="54" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
        + _text(250, 487, "A hard problem isn't the end of the story.", "sans", 15, INK, 'font-weight="700" text-anchor="middle"')
        + _text(250, 515, "IT'S MY NEXT TRAINING ARC!", "sfx", 25, RED, 'text-anchor="middle" letter-spacing="1"')
        + "</g>"
    )
    don = (
        '<g class="don">'
        + _text(468, 352, "ドン!", "jp", 76, RED, f'text-anchor="middle" stroke="{INK}" stroke-width="10" paint-order="stroke" stroke-linejoin="round" transform="rotate(-12 468 330)"')
        + "</g>"
    )
    body = defs + f'<rect width="1000" height="600" fill="{PAPER}"/>' + a + b + c + bubble + don
    return _svg(1000, 600, "The Developer — a Mouad Ziyani production", body, css)


CHAPTERS = [
    ("01", "ORIGIN STORY", "物語", "Every hero has a first chapter."),
    ("02", "POWER LEVELS", "能力", "The tools behind the work."),
    ("03", "STORY ARCS", "作品", "Ideas, brought to life."),
    ("04", "THE JOURNEY", "旅路", "Always building. Always learning."),
    ("05", "TRAINING LOG", "修行", "Every commit is another rep."),
    ("FINAL", "START A CONVERSATION", "終章", "Let's build something meaningful."),
]


def render_chapter(number: str, title: str, kanji: str, subtitle: str) -> str:
    label = "FINAL" if number == "FINAL" else f"CH. {number}"
    css = (
        f".strip{{animation:inL .7s {EASE} both}}.kanji{{animation:fade 1s ease .4s both}}"
        "@keyframes inL{from{transform:translateX(-90px);opacity:0}}"
        "@keyframes fade{from{opacity:0;transform:translateY(12px)}}"
    )
    body = (
        "<defs>"
        f"{_tone('tone', PAPER)}"
        '<linearGradient id="g" x1="0" x2="1"><stop offset="0.55" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>'
        '<mask id="m"><rect width="1000" height="120" fill="url(#g)"/></mask>'
        "</defs>"
        '<g class="strip">'
        f'<polygon points="16,16 996,10 992,116 12,116" fill="{RED}"/>'
        f'<polygon points="4,6 986,0 982,106 0,106" fill="{INK}"/>'
        f'<rect width="1000" height="110" fill="url(#tone)" opacity=".28" mask="url(#m)"/>'
        f'<polygon points="0,6 178,4 150,106 0,106" fill="{RED}"/>'
        + _text(84, 70, label, "sfx", 38, WHITE, 'text-anchor="middle" letter-spacing="1.5"')
        + _text(184, 64, title, "sfx", 50, WHITE, 'letter-spacing="2.5"')
        + _text(186, 91, subtitle, "sans", 15, PAPER, 'fill-opacity=".72" font-weight="500"')
        + "</g>"
        + '<g class="kanji">' + _text(962, 86, kanji, "jp", 70, RED, f'text-anchor="end" stroke="{INK}" stroke-width="3" paint-order="stroke"') + "</g>"
    )
    return _svg(1000, 120, f"{label} — {title.title()}", body, css)


CHARACTER = [
    ("NAME", "Mouad Ziyani"),
    ("CLASS", "Full-Stack Web & Mobile Developer"),
    ("BASE", "Oujda, Morocco"),
    ("GUILD", "YouCode Nador · UM6P"),
    ("WEAPON OF CHOICE", "Clean, efficient code"),
    ("CURRENT ARC", "Modular backends with Spring Modulith"),
    ("SPECIAL MOVE", "Turning ideas into working products"),
    ("STATUS", "Open to collaborations"),
]


def render_character() -> str:
    css = (
        f".card{{animation:up .7s {EASE} both}}"
        f".stamp{{animation:stamp .4s {EASE} 1s both;transform-box:fill-box;transform-origin:center}}"
        "@keyframes up{from{transform:translateY(40px);opacity:0}}"
        "@keyframes stamp{from{transform:scale(2.4) rotate(-10deg);opacity:0}}"
    )
    fields = []
    for index, (label, value) in enumerate(CHARACTER):
        x = 44 if index < 4 else 524
        y = 104 + 60 * (index % 4)
        fields.append(_text(x, y, label, "sfx", 19, RED, 'letter-spacing="2"'))
        fields.append(_text(x, y + 25, value, "sans", 18, INK, 'font-weight="700"'))
    bio = "The first chapter began with simple curiosity. Each new technology is another training arc, each bug another boss to defeat."
    bio_lines = "".join(
        _text(44, 368 + 22 * i, line, "sans", 15, MUTED, 'font-style="italic"')
        for i, line in enumerate(textwrap.wrap(bio, 78))
    )
    body = (
        f"<defs>{_tone('tone', INK)}</defs>"
        '<g class="card">'
        f'<rect x="12" y="12" width="984" height="404" fill="{INK}"/>'
        f'<rect x="4" y="4" width="984" height="404" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="4" y="4" width="984" height="44" fill="{INK}"/>'
        + _text(24, 34, "CHARACTER FILE  ·  No. 001", "sans", 14, PAPER, 'font-weight="700" letter-spacing="4"')
        + _text(966, 36, "人物", "jp", 22, RED, 'text-anchor="end"')
        + f'<rect x="760" y="48" width="228" height="290" fill="url(#tone)" opacity=".12"/>'
        + f'<line x1="24" y1="338" x2="968" y2="338" stroke="{INK}" stroke-width="2" stroke-dasharray="8 6"/>'
        + "".join(fields)
        + bio_lines
        + "</g>"
        + '<g class="stamp" transform="rotate(-9 860 375)">'
        + f'<rect x="760" y="348" width="200" height="54" fill="none" stroke="{RED}" stroke-width="4"/>'
        + _text(860, 386, "LEVELING UP", "sfx", 32, RED, 'text-anchor="middle" letter-spacing="2"')
        + "</g>"
    )
    return _svg(1000, 420, "Character file: Mouad Ziyani", body, css)


POWERS = [
    ("面", "INTERFACE", "FRONT-END", ["HTML", "CSS", "JavaScript", "React", "Tailwind CSS"]),
    ("理", "LOGIC", "BACK-END", ["Java", "Spring Boot", "PHP", "Laravel"]),
    ("携", "MOTION", "MOBILE", ["React Native"]),
    ("蔵", "MEMORY", "DATABASES", ["MySQL", "PostgreSQL"]),
    ("道", "FLOW", "DEVOPS", ["Docker", "Git", "GitHub", "Figma", "Postman"]),
]
EXPLORING = ["Vue", "Node.js", "Python", "MongoDB", "Angular", "C"]


def render_powers() -> str:
    css = (
        "".join(f".c{i}{{animation:drop .6s {EASE} {i * 0.12:.2f}s both}}" for i in range(len(POWERS)))
        + f".bar{{animation:inL .8s {EASE} .7s both}}"
        "@keyframes drop{from{transform:translateY(-40px);opacity:0}}"
        "@keyframes inL{from{transform:translateX(-60px);opacity:0}}"
    )
    cards = []
    for index, (kanji, element, title, tools) in enumerate(POWERS):
        x = 20 + index * 195
        cx = x + 90
        tool_text = "".join(
            _text(cx, 232 + 25 * i, tool, "sans", 15, INK, 'font-weight="700" text-anchor="middle"')
            for i, tool in enumerate(tools)
        )
        cards.append(
            f'<g class="c{index}">'
            f'<rect x="{x + 6}" y="26" width="180" height="340" fill="{INK}"/>'
            f'<rect x="{x}" y="20" width="180" height="340" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{x}" y="20" width="180" height="120" fill="url(#tone)" opacity=".16"/>'
            f'<circle cx="{cx}" cy="80" r="42" fill="{RED}" stroke="{INK}" stroke-width="3"/>'
            + _text(cx, 98, kanji, "jp", 48, WHITE, 'text-anchor="middle"')
            + _text(cx, 160, f"ELEMENT · {element}", "sans", 10, MUTED, 'font-weight="700" letter-spacing="2" text-anchor="middle"')
            + _text(cx, 194, title, "sfx", 32, INK, 'text-anchor="middle" letter-spacing="1.5"')
            + f'<line x1="{x + 30}" y1="206" x2="{x + 150}" y2="206" stroke="{RED}" stroke-width="3"/>'
            + tool_text
            + "</g>"
        )
    pills, px = [], 392
    for tool in EXPLORING:
        width = len(tool) * 9 + 28
        pills.append(
            f'<rect x="{px}" y="406" width="{width}" height="32" rx="16" fill="none" stroke="{PAPER}" stroke-width="2"/>'
            + _text(px + width / 2, 427, tool, "sans", 14, PAPER, 'font-weight="700" text-anchor="middle"')
        )
        px += width + 10
    bar = (
        '<g class="bar">'
        f'<rect x="26" y="392" width="960" height="60" fill="{RED}"/>'
        f'<rect x="20" y="386" width="960" height="60" fill="{INK}"/>'
        + _text(40, 428, "修行中", "jp", 24, RED)
        + _text(122, 428, "CURRENTLY EXPLORING", "sfx", 28, WHITE, 'letter-spacing="1.5"')
        + "".join(pills)
        + "</g>"
    )
    body = f"<defs>{_tone('tone', INK)}</defs>" + "".join(cards) + bar
    return _svg(1000, 460, "Power levels: technical toolkit", body, css)


ARCS = [
    ("01", "AFFILIATE PLATFORM", "affiliatelink", "affiliatelink",
     "A modular affiliate marketing platform built with Spring Boot and Spring Modulith.",
     ["Java", "Spring Boot", "Spring Modulith", "PostgreSQL"]),
    ("02", "CLICK TRACKING", "ClickTrack", "ClickTrack",
     "A Spring MVC API that lets publishers create tracking links and follow their clicks.",
     ["Java", "Spring MVC"]),
    ("03", "MEDICAL API", "teleexpertise", "TeleExpertise",
     "A REST API for medical tele-expertise, secured with Basic Auth and powered by the Stream API.",
     ["Java", "JAX-RS", "Hibernate"]),
    ("04", "CLINIC APP", "gestion-clinique-tele-expertise", "Clinique Expertise",
     "Patient intake, vital signs and doctor consultations — started on JDBC, migrated to JPA.",
     ["Jakarta EE", "JPA", "Hibernate"]),
]


def render_arc(number: str, kind: str, title: str, description: str, stack: list[str]) -> str:
    css = (
        f".card{{animation:up .7s {EASE} both}}"
        f".slash{{animation:slash .9s {EASE} .3s both}}"
        "@keyframes up{from{transform:translateY(36px);opacity:0}}"
        "@keyframes slash{from{transform:translateX(-420px);opacity:0}}"
    )
    title_size = min(46, 290 / (len(title) * 0.47))
    desc = "".join(
        _text(26, 150 + 22 * i, line, "sans", 15, INK, 'font-weight="500"')
        for i, line in enumerate(textwrap.wrap(description, 52)[:3])
    )
    tags, tx = [], 26
    for tool in stack:
        width = len(tool) * 7.6 + 22
        tags.append(
            f'<rect x="{tx:.1f}" y="218" width="{width:.1f}" height="28" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
            + _text(round(tx + width / 2, 1), 237, tool, "sans", 12.5, INK, 'font-weight="700" text-anchor="middle"')
        )
        tx += width + 8
    body = (
        f"<defs>{_tone('tone', PAPER)}"
        '<clipPath id="top"><rect x="4" y="4" width="474" height="110"/></clipPath></defs>'
        '<g class="card">'
        f'<rect x="12" y="12" width="474" height="284" fill="{INK}"/>'
        f'<rect x="4" y="4" width="474" height="284" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
        '<g clip-path="url(#top)">'
        f'<rect x="4" y="4" width="474" height="110" fill="{INK}"/>'
        f'<rect x="4" y="4" width="474" height="110" fill="url(#tone)" opacity=".18"/>'
        f'<polygon class="slash" points="372,4 412,4 342,114 302,114" fill="{RED}"/>'
        + _text(468, 112, number, "sfx", 120, "none", f'text-anchor="end" stroke="{PAPER}" stroke-width="2" stroke-opacity=".75"')
        + "</g>"
        + _text(26, 38, f"ARC {number} / {kind}", "sans", 12, RED, 'font-weight="700" letter-spacing="3"')
        + _text(26, 94, title, "sfx", round(title_size, 1), WHITE, 'letter-spacing="1.5"')
        + f'<line x1="4" y1="114" x2="478" y2="114" stroke="{INK}" stroke-width="4"/>'
        + desc
        + "".join(tags)
        + f'<polygon points="330,256 474,256 474,288 316,288" fill="{RED}"/>'
        + _text(398, 280, "READ THE ARC →", "sfx", 21, WHITE, 'text-anchor="middle" letter-spacing="1.5"')
        + "</g>"
    )
    return _svg(490, 300, f"Arc {number}: {title} — {description}", body, css)


def render_next_time() -> str:
    css = f".n{{animation:inR .8s {EASE} both}}@keyframes inR{{from{{transform:translateX(80px);opacity:0}}}}"
    body = (
        f"<defs>{_tone('tone', INK)}</defs>"
        '<g class="n">'
        f'<rect x="10" y="10" width="986" height="76" fill="{RED}"/>'
        f'<rect x="4" y="4" width="986" height="76" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="700" y="6" width="288" height="72" fill="url(#tone)" opacity=".2"/>'
        f'<rect x="4" y="4" width="200" height="76" fill="{INK}"/>'
        + _text(104, 54, "次回予告", "jp", 30, RED, 'text-anchor="middle"')
        + _text(228, 52, "NEXT TIME: MORE ARCS IN PRODUCTION…", "sfx", 32, INK, 'letter-spacing="1.5"')
        + _text(966, 52, "ALL REPOS →", "sfx", 24, RED, 'text-anchor="end" letter-spacing="1.5"')
        + "</g>"
    )
    return _svg(1000, 90, "Next time: more arcs in production — explore all repositories", body, css)


JOURNEY = [
    ("2025 — 2027", "Java Full-Stack Developer", "YouCode, Nador",
     "Comprehensive training in Java full-stack web development."),
    ("2025", "Full-Stack Development", "Atlantic", "Web development basics."),
    ("2022 — 2025", "Computer Engineering Studies", "Faculty of Science, Oujda",
     "Python, C, algorithms, web basics, computer architecture and operating systems."),
    ("2022", "High School Diploma", "Technical High School", "Focus on mathematics B."),
]


def render_journey() -> str:
    css = (
        "".join(f".r{i}{{animation:inR .7s {EASE} {i * 0.15:.2f}s both}}" for i in range(len(JOURNEY)))
        + ".blink{animation:blink 1.2s steps(2) infinite}"
        "@keyframes inR{from{transform:translateX(60px);opacity:0}}"
        "@keyframes blink{50%{opacity:0}}"
    )
    rows = [
        f'<rect x="12" y="12" width="986" height="434" fill="{RED}"/>'
        f'<rect x="4" y="4" width="986" height="434" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="4" y="4" width="986" height="434" fill="url(#tone)" opacity=".1"/>',
        f'<line x1="112" y1="40" x2="112" y2="420" stroke="{INK}" stroke-width="4" stroke-dasharray="10 8"/>',
    ]
    for index, (years, title, place, detail) in enumerate(JOURNEY):
        y = 20 + index * 106
        current = index == 0
        rows.append(
            f'<g class="r{index}">'
            f'<polygon points="20,{y + 22} 204,{y + 16} 196,{y + 70} 26,{y + 74}" fill="{RED if current else INK}"/>'
            + _text(112, y + 54, years, "sfx", 26, WHITE, 'text-anchor="middle" letter-spacing="1"')
            + f'<rect x="238" y="{y + 6}" width="746" height="88" fill="{INK}"/>'
            + f'<rect x="232" y="{y}" width="746" height="88" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>'
            + _text(252, y + 34, title.upper(), "sfx", 28, INK, 'letter-spacing="1.5"')
            + _text(252, y + 57, place, "sans", 14, RED, 'font-weight="700"')
            + _text(252, y + 77, detail, "sans", 14, MUTED)
            + ('<g class="blink">' + _text(958, y + 32, "● CURRENT ARC", "sfx", 18, RED, 'text-anchor="end" letter-spacing="1.5"') + "</g>" if current else "")
            + "</g>"
        )
    body = f"<defs>{_tone('tone', INK)}</defs>" + "".join(rows)
    return _svg(1000, 450, "The journey: experience and education", body, css)


def render_finale() -> str:
    css = (
        f".arrow{{animation:inR 1s {EASE} .2s both}}"
        f".end{{animation:stamp .5s {EASE} 1.1s both;transform-box:fill-box;transform-origin:center}}"
        ".spin{transform-origin:500px 120px;animation:spin 90s linear infinite}"
        "@keyframes inR{from{transform:translateX(700px)}}"
        "@keyframes stamp{from{transform:scale(2.5) rotate(20deg);opacity:0}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    body = (
        f"<defs>{_tone('tone', INK)}"
        '<clipPath id="frame"><rect x="4" y="4" width="986" height="222"/></clipPath></defs>'
        f'<rect x="12" y="12" width="986" height="222" fill="{RED}"/>'
        f'<rect x="4" y="4" width="986" height="222" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>'
        '<g clip-path="url(#frame)">'
        f'<g class="spin">{_speed_lines(500, 120, 700, 70, INK, 0.12)}</g>'
        f'<rect x="4" y="4" width="986" height="222" fill="url(#tone)" opacity=".12"/>'
        "</g>"
        '<g class="arrow">'
        f'<polygon points="48,112 138,46 138,78 660,78 660,148 138,148 138,180" fill="#E9D8A6" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
        + _text(400, 132, "TO BE CONTINUED", "sfx", 54, INK, 'text-anchor="middle" letter-spacing="3"')
        + "</g>"
        + '<g class="end">'
        + f'<circle cx="826" cy="112" r="78" fill="{RED}" stroke="{INK}" stroke-width="5"/>'
        + _text(826, 146, "完", "jp", 92, WHITE, 'text-anchor="middle"')
        + "</g>"
        + _text(497, 212, "Story & code: Mouad Ziyani  ·  Drawn on location in Oujda, Morocco", "sans", 13, MUTED, 'text-anchor="middle" font-weight="600"')
    )
    return _svg(1000, 240, "To be continued", body, css)


def build() -> dict[str, str]:
    """Return every asset as {filename: svg}."""
    assets = {
        "hero.svg": render_hero(),
        "character.svg": render_character(),
        "powers.svg": render_powers(),
        "next-time.svg": render_next_time(),
        "journey.svg": render_journey(),
        "finale.svg": render_finale(),
    }
    for number, title, kanji, subtitle in CHAPTERS:
        assets[f"chapter-{number.lower()}.svg"] = render_chapter(number, title, kanji, subtitle)
    for number, kind, _repo, title, description, stack in ARCS:
        assets[f"arc-{number}.svg"] = render_arc(number, kind, title, description, stack)
    return assets


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, svg in build().items():
        (OUTPUT_DIR / name).write_text(svg, encoding="utf-8")
        print(f"Wrote {OUTPUT_DIR / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
