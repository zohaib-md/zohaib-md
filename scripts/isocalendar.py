#!/usr/bin/env python3
"""Render a metrics-style 3D isometric contribution calendar as SVG."""

from __future__ import annotations

import json
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

USER = "zohaib-md"
LEVEL_COLORS = {
    0: "#ebedf0",
    1: "#9be9a8",
    2: "#40c463",
    3: "#30a14e",
    4: "#216e39",
}

ICONS = {
    "calendar": "M4.75 0a.75.75 0 01.75.75V2h5V.75a.75.75 0 011.5 0V2h1.25c.966 0 1.75.784 1.75 1.75v10.5A1.75 1.75 0 0113.25 16H2.75A1.75 1.75 0 011 14.25V3.75C1 2.784 1.784 2 2.75 2H4V.75A.75.75 0 014.75 0zm0 3.5h8.5a.25.25 0 01.25.25V6h-11V3.75a.25.25 0 01.25-.25h2zm-2.25 4v6.75c0 .138.112.25.25.25h10.5a.25.25 0 00.25-.25V7.5h-11z",
    "streaks": "M7.75 14A1.75 1.75 0 016 12.25v-8.5C6 2.784 6.784 2 7.75 2h6.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0114.25 14h-6.5zm-.25-1.75c0 .138.112.25.25.25h6.5a.25.25 0 00.25-.25v-8.5a.25.25 0 00-.25-.25h-6.5a.25.25 0 00-.25.25v8.5zM4.9 3.508a.75.75 0 01-.274 1.025.25.25 0 00-.126.217v6.5a.25.25 0 00.126.217.75.75 0 01-.752 1.298A1.75 1.75 0 013 11.25v-6.5c0-.649.353-1.214.874-1.516a.75.75 0 011.025.274zM1.625 5.533a.75.75 0 10-.752-1.299A1.75 1.75 0 000 5.75v4.5c0 .649.353 1.214.874 1.515a.75.75 0 10.752-1.298.25.25 0 01-.126-.217v-4.5a.25.25 0 01.126-.217z",
    "flame": "M7.998 14.5c2.832 0 5-1.98 5-4.5 0-1.463-.68-2.19-1.879-3.383l-.036-.037c-1.013-1.008-2.3-2.29-2.834-4.434-.322.256-.63.579-.864.953-.432.696-.621 1.58-.046 2.73.473.947.67 2.284-.278 3.232-.61.61-1.545.84-2.403.633a2.788 2.788 0 01-1.436-.874A3.21 3.21 0 003 10c0 2.53 2.164 4.5 4.998 4.5zM9.533.753C9.496.34 9.16.009 8.77.146 7.035.75 4.34 3.187 5.997 6.5c.344.689.285 1.218.003 1.5-.419.419-1.54.487-2.04-.832-.173-.454-.659-.762-1.035-.454C2.036 7.44 1.5 8.702 1.5 10c0 3.512 2.998 6 6.498 6s6.5-2.5 6.5-6c0-2.137-1.128-3.26-2.312-4.438-1.19-1.184-2.436-2.425-2.653-4.81z",
    "sparkle": "M8.5.75a.75.75 0 00-1.5 0v5.19L4.391 3.33a.75.75 0 10-1.06 1.061L5.939 7H.75a.75.75 0 000 1.5h5.19l-2.61 2.609a.75.75 0 101.061 1.06L7 9.561v5.189a.75.75 0 001.5 0V9.56l2.609 2.61a.75.75 0 101.06-1.061L9.561 8.5h5.189a.75.75 0 000-1.5H9.56l2.61-2.609a.75.75 0 00-1.061-1.06L8.5 5.939V.75z",
    "perday": "M10.5 7.75a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zm1.43.75a4.002 4.002 0 01-7.86 0H.75a.75.75 0 110-1.5h3.32a4.001 4.001 0 017.86 0h3.32a.75.75 0 110 1.5h-3.32z",
    "up": "M7.823 1.677L4.927 4.573A.25.25 0 005.104 5H7.25v3.236a.75.75 0 101.5 0V5h2.146a.25.25 0 00.177-.427L8.177 1.677a.25.25 0 00-.354 0zM13.75 11a.75.75 0 000 1.5h.5a.75.75 0 000-1.5h-.5zm-3.75.75a.75.75 0 01.75-.75h.5a.75.75 0 010 1.5h-.5a.75.75 0 01-.75-.75zM7.75 11a.75.75 0 000 1.5h.5a.75.75 0 000-1.5h-.5zM4 11.75a.75.75 0 01.75-.75h.5a.75.75 0 010 1.5h-.5a.75.75 0 01-.75-.75zM1.75 11a.75.75 0 000 1.5h.5a.75.75 0 000-1.5h-.5z",
    "avg": "M10.896 2H8.75V.75a.75.75 0 00-1.5 0V2H5.104a.25.25 0 00-.177.427l2.896 2.896a.25.25 0 00.354 0l2.896-2.896A.25.25 0 0010.896 2zM8.75 15.25a.75.75 0 01-1.5 0V14H5.104a.25.25 0 01-.177-.427l2.896-2.896a.25.25 0 01.354 0l2.896 2.896a.25.25 0 01-.177.427H8.75v1.25zm-6.5-6.5a.75.75 0 000-1.5h-.5a.75.75 0 000 1.5h.5zM6 8a.75.75 0 01-.75.75h-.5a.75.75 0 010-1.5h.5A.75.75 0 016 8zm2.25.75a.75.75 0 000-1.5h-.5a.75.75 0 000 1.5h.5zM12 8a.75.75 0 01-.75.75h-.5a.75.75 0 010-1.5h.5A.75.75 0 0112 8zm2.25.75a.75.75 0 000-1.5h-.5a.75.75 0 000 1.5h.5z",
}


def fetch_contributions(user: str) -> list[dict]:
    url = f"https://github-contributions-api.jogruber.de/v4/{user}"
    req = urllib.request.Request(url, headers={"User-Agent": "isocalendar.py"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    return data["contributions"]


def window_days(contributions: list[dict]) -> list[dict]:
    today = datetime.now(timezone.utc).date()
    start = date(today.year - 1, today.month, today.day)
    start -= timedelta(days=start.weekday() + 1 if start.weekday() != 6 else 0)
    by_date = {c["date"]: c for c in contributions}
    days = []
    d = start
    while d <= today:
        key = d.isoformat()
        item = by_date.get(key, {"date": key, "count": 0, "level": 0})
        days.append(item)
        d += timedelta(days=1)
    return days


def stats(days: list[dict]) -> tuple[int, int, int, str]:
    current = best = run = 0
    counts = []
    for day in days:
        n = int(day["count"])
        counts.append(n)
        if n:
            run += 1
            current = run
            best = max(best, run)
        else:
            run = 0
            current = 0
    highest = max(counts) if counts else 0
    avg = f"{(sum(counts) / len(counts)):.2f}".replace(".00", "")
    avg = avg.rstrip("0").rstrip(".") if "." in avg else avg
    return current, best, highest, avg


def icon(name: str, x: float, y: float, fill: str) -> str:
    return (
        f'<path transform="translate({x:.1f},{y:.1f})" fill="{fill}" '
        f'fill-rule="evenodd" d="{ICONS[name]}"/>'
    )


def render(days: list[dict]) -> str:
    current, best, highest, avg = stats(days)
    reference = max((int(d["count"]) for d in days), default=1) or 1
    size = 6

    weeks: list[list[dict]] = []
    for i in range(0, len(days), 7):
        weeks.append(days[i : i + 7])

    cubes = []
    for i, week in enumerate(weeks):
        cubes.append(f'<g transform="translate({i * 1.7}, {i})">')
        for j, day in enumerate(week):
            count = int(day["count"])
            ratio = count / reference if reference else 0
            color = LEVEL_COLORS.get(int(day.get("level", 0)), LEVEL_COLORS[0])
            cubes.append(
                f'<g transform="translate({j * -1.7}, {j + (1 - ratio) * size})">'
                f'<path fill="{color}" d="M1.7,2 0,1 1.7,0 3.4,1 z"/>'
                f'<path fill="{color}" filter="url(#brightness1)" '
                f'd="M0,1 1.7,2 1.7,{2 + ratio * size} 0,{1 + ratio * size} z"/>'
                f'<path fill="{color}" filter="url(#brightness2)" '
                f'd="M1.7,2 3.4,1 3.4,{1 + ratio * size} 1.7,{2 + ratio * size} z"/>'
                f"</g>"
            )
        cubes.append("</g>")

    def plural(n: int, word: str) -> str:
        return f"{n} {word}" if n == 1 else f"{n} {word}s"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="330" viewBox="0 0 480 330" role="img" aria-label="3D isometric contribution calendar">
  <style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif; }}
  </style>
  <rect width="480" height="330" fill="#0d1117"/>
  {icon("calendar", 8, 10, "#58a6ff")}
  <text x="30" y="23" font-size="16" fill="#58a6ff">Contributions calendar</text>

  {icon("streaks", 300, 48, "#58a6ff")}
  <text x="322" y="61" font-size="14" fill="#58a6ff">Commits streaks</text>
  {icon("flame", 308, 72, "#8b949e")}
  <text x="330" y="85" font-size="13" fill="#c9d1d9">Current streak {plural(current, "day")}</text>
  {icon("sparkle", 308, 94, "#8b949e")}
  <text x="330" y="107" font-size="13" fill="#c9d1d9">Best streak {plural(best, "day")}</text>

  {icon("perday", 300, 124, "#58a6ff")}
  <text x="322" y="137" font-size="14" fill="#58a6ff">Commits per day</text>
  {icon("up", 308, 148, "#8b949e")}
  <text x="330" y="161" font-size="13" fill="#c9d1d9">Highest in a day at {highest}</text>
  {icon("avg", 308, 170, "#8b949e")}
  <text x="330" y="183" font-size="13" fill="#c9d1d9">Average per day at ~{avg}</text>

  <filter id="brightness1">
    <feComponentTransfer>
      <feFuncR type="linear" slope="0.6"/>
      <feFuncG type="linear" slope="0.6"/>
      <feFuncB type="linear" slope="0.6"/>
    </feComponentTransfer>
  </filter>
  <filter id="brightness2">
    <feComponentTransfer>
      <feFuncR type="linear" slope="0.2"/>
      <feFuncG type="linear" slope="0.2"/>
      <feFuncB type="linear" slope="0.2"/>
    </feComponentTransfer>
  </filter>
  <g transform="translate(8, 40) scale(4) translate(12, 0)">
    {"".join(cubes)}
  </g>
</svg>
'''


def main() -> None:
    days = window_days(fetch_contributions(USER))
    out = Path("assets/metrics.isocalendar.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(days), encoding="utf-8")
    print(f"wrote {out}  ({len(days)} days)")


if __name__ == "__main__":
    main()
