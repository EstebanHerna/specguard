from __future__ import annotations

import html
from pathlib import Path

from specguard.models import AuditReport

GREEN = "#4c1"
YELLOW = "#dfb317"
RED = "#e05d44"
LABEL_BG = "#555"
LABEL_TEXT = "traceability"


def _color_for(score: float) -> str:
    if score >= 90:
        return GREEN
    if score >= 70:
        return YELLOW
    return RED


def _char_width(text: str) -> int:
    return 6 * len(text) + 10


def write_badge(report: AuditReport, path: Path) -> None:
    score_text = f"{report.score:.1f}%"
    color = _color_for(report.score)
    label = html.escape(LABEL_TEXT)
    value = html.escape(score_text)
    label_width = _char_width(LABEL_TEXT)
    value_width = _char_width(score_text)
    total_width = label_width + value_width

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="{LABEL_BG}"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_width / 2}" y="14">{label}</text>
    <text x="{label_width + value_width / 2}" y="14">{value}</text>
  </g>
</svg>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
