"""SVG badge generator for README."""

from __future__ import annotations

GRADE_BADGE_COLORS = {
    "A": "#4c1",
    "B": "#97CA00",
    "C": "#dfb317",
    "D": "#fe7d37",
    "F": "#e05d44",
}

_BADGE_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="136" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="136" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h63v20H0z"/>
    <path fill="{color}" d="M63 0h73v20H63z"/>
    <path fill="url(#b)" d="M0 0h136v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,sans-serif" font-size="11">
    <text x="31.5" y="15" fill="#010101" fill-opacity=".3">debtx</text>
    <text x="31.5" y="14">debtx</text>
    <text x="99.5" y="15" fill="#010101" fill-opacity=".3">{grade} | {score}/100</text>
    <text x="99.5" y="14">{grade} | {score}/100</text>
  </g>
</svg>"""


def generate_badge(grade: str, vibe_score: int, output_path: str) -> None:
    color = GRADE_BADGE_COLORS.get(grade, "#9f9f9f")
    svg = _BADGE_TEMPLATE.format(color=color, grade=grade, score=vibe_score)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
