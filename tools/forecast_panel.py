#!/usr/bin/env python3
"""Generate the front page's five-day FORECAST PANEL for The Fiddletown Gazette.

Dave's feature (Nov 5, 2026): a visual multi-day forecast at the top of the front page,
generated at edition-render time from the SAME National Weather Service forecast the
editions write their weather prose from — never a static image with baked-in numbers.

Usage:
    python3 tools/forecast_panel.py            # fetch NWS + splice panel into index.html
    python3 tools/forecast_panel.py --dry-run  # print the panel HTML, change nothing

The panel is spliced between <!-- FORECAST:BEGIN --> and <!-- FORECAST:END --> markers
in index.html; on first run (no markers) it inserts right after the lead headline.
The panel's <style id="forecast-panel-style"> block is inserted before </head> once.
If the NWS fetch fails, the script exits nonzero and leaves index.html UNTOUCHED —
the previous panel stands (editions note the stale timestamp, per PUBLISHING.md).
"""
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"
FORECAST_URL = "https://api.weather.gov/gridpoints/STO/66,60/forecast"  # Fiddletown point 38.5035,-120.7574
UA = {"User-Agent": "GazetteBuddy/1.0 (dave@dellaquila.com)"}
PT = ZoneInfo("America/Los_Angeles")
DAYS = 5

GOLD = "#b8860b"
INK = "#3a3f45"
CLOUD = "#93a3b1"
RAIN = "#4a7fa5"

# --- Drawn weather icons (inline SVG, viewBox 0 0 48 48) — no emoji, per Dave's spec ---
def _sun(cx, cy, r):
    rays = ""
    import math
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x1, y1 = cx + (r + 3.5) * math.cos(rad), cy + (r + 3.5) * math.sin(rad)
        x2, y2 = cx + (r + 7.5) * math.cos(rad), cy + (r + 7.5) * math.sin(rad)
        rays += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
    return (f'<g stroke="{GOLD}" stroke-width="2.4" stroke-linecap="round" fill="none">{rays}</g>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GOLD}"/>')

MOON = (f'<path d="M33 6a17.5 17.5 0 1 0 9 24.6A14 14 0 0 1 33 6Z" fill="{GOLD}"/>')

def _cloud(dx=0, dy=0, fill=CLOUD, scale=1.0):
    return (f'<g transform="translate({dx} {dy}) scale({scale})">'
            f'<path d="M13 37a8.5 8.5 0 0 1-.8-16.9 12.5 12.5 0 0 1 24-2.3A9 9 0 0 1 35 37Z" fill="{fill}"/></g>')

def icon(kind):
    if kind == "sun":
        return f'<svg viewBox="0 0 48 48" aria-hidden="true">{_sun(24, 24, 8)}</svg>'
    if kind == "moon":
        return f'<svg viewBox="0 0 48 48" aria-hidden="true">{MOON}</svg>'
    if kind == "partly-day":
        return f'<svg viewBox="0 0 48 48" aria-hidden="true">{_sun(15, 14, 5.5)}{_cloud(6, 8)}</svg>'
    if kind == "partly-night":
        return (f'<svg viewBox="0 0 48 48" aria-hidden="true">'
                f'<path d="M20 4a11 11 0 1 0 5.6 15.4A8.6 8.6 0 0 1 20 4Z" fill="{GOLD}"/>{_cloud(6, 10)}</svg>')
    if kind == "mostly-cloudy":
        return f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(-4, -6, "#b6c1cb", 0.82)}{_cloud(5, 5)}</svg>'
    if kind == "overcast":
        return f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, 2, "#7e8fa0")}</svg>'
    if kind == "cloud":
        return f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, 2)}</svg>'
    if kind == "rain":
        drops = "".join(f'<line x1="{x}" y1="38" x2="{x-2}" y2="45"/>' for x in (17, 25, 33))
        return (f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, -3)}'
                f'<g stroke="{RAIN}" stroke-width="2.6" stroke-linecap="round">{drops}</g></svg>')
    if kind == "showers":
        drops = "".join(f'<line x1="{x}" y1="39" x2="{x-1.5}" y2="43.5"/>' for x in (19, 29))
        return (f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, -3)}'
                f'<g stroke="{RAIN}" stroke-width="2.6" stroke-linecap="round">{drops}</g></svg>')
    if kind == "thunder":
        return (f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, -5)}'
                f'<polygon points="26,32 19.5,43 24,43 21.5,47.5 30,37 25.5,37" fill="{GOLD}"/></svg>')
    if kind == "snow":
        flakes = "".join(
            f'<g stroke="{RAIN}" stroke-width="1.8" stroke-linecap="round">'
            f'<line x1="{x-3}" y1="42" x2="{x+3}" y2="42"/><line x1="{x}" y1="39" x2="{x}" y2="45"/></g>'
            for x in (17, 25, 33))
        return f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, -4)}{flakes}</svg>'
    if kind == "fog":
        lines = "".join(f'<line x1="13" y1="{y}" x2="35" y2="{y}"/>' for y in (39, 44))
        return (f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, -5)}'
                f'<g stroke="{CLOUD}" stroke-width="2.4" stroke-linecap="round">{lines}</g></svg>')
    return f'<svg viewBox="0 0 48 48" aria-hidden="true">{_cloud(0, 2)}</svg>'

def icon_kind(nws_icon_url, is_day):
    """Map an NWS icon URL (…/day/skc, …/night/rain,80/…) to a drawn-icon kind."""
    m = re.search(r"/icons/land/(?:day|night)/([^?]+)", nws_icon_url or "")
    code = m.group(1).split("/")[0].split(",")[0] if m else ""
    base = {
        "skc": "sun" if is_day else "moon",
        "few": "partly-day" if is_day else "partly-night",
        "sct": "partly-day" if is_day else "partly-night",
        "bkn": "mostly-cloudy",
        "ovc": "overcast",
        "cloudy": "cloud",
        "rain": "rain",
        "rain_showers": "showers",
        "hi_shwrs": "showers",
        "tsra": "thunder",
        "snow": "snow",
        "fog": "fog",
        "haze": "fog",
        "wind_skc": "sun" if is_day else "moon",
        "wind_few": "partly-day" if is_day else "partly-night",
        "wind_sct": "partly-day" if is_day else "partly-night",
        "wind_bkn": "mostly-cloudy",
        "wind_ovc": "overcast",
    }
    return base.get(code, "cloud")

STYLE = """<style id="forecast-panel-style">
/* Forecast panel (Dave, Nov 5, 2026): visual five-day outlook at the top of the front page,
   generated at edition time from the NWS forecast by tools/forecast_panel.py — standing element,
   preserved/regenerated by every edition. Phone-first: five flex columns, no horizontal scroll. */
.fc-panel{border-top:3px double var(--ink,#2b2b2b);border-bottom:1px solid var(--border,#d8cfba);padding:10px 2px 12px;margin:12px 0 6px}
.fc-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
.fc-title{font-family:Georgia,'Times New Roman',serif;font-size:13px;font-weight:700;letter-spacing:.16em;text-transform:uppercase}
.fc-src{font-family:-apple-system,sans-serif;font-size:10.5px;color:var(--muted,#6b6252)}
.fc-days{display:flex;gap:2px;margin-top:8px}
.fc-day{flex:1 1 0;min-width:0;text-align:center;padding:4px 1px 0}
.fc-day + .fc-day{border-left:1px solid var(--border,#d8cfba)}
.fc-name{font-family:-apple-system,sans-serif;font-size:11.5px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.fc-day svg{width:34px;height:34px;display:block;margin:3px auto 1px}
.fc-cond{font-size:11px;line-height:1.25;min-height:2.5em}
.fc-temps{font-family:Georgia,'Times New Roman',serif;font-size:16px;margin-top:2px;white-space:nowrap}
.fc-hi{font-weight:700}
.fc-lo{color:var(--muted,#6b6252)}
.fc-pop{font-family:-apple-system,sans-serif;font-size:10.5px;color:#4a7fa5;min-height:1.25em;margin-top:1px}
@media (max-width:380px){.fc-day svg{width:28px;height:28px}.fc-temps{font-size:14px}.fc-name{font-size:10px}.fc-cond{font-size:10px}}
</style>"""

def build_days(periods):
    """Group NWS periods into day entries: [{label, cond, kind, hi, lo, pop}]."""
    days = []
    cur = None
    for p in periods:
        start = datetime.fromisoformat(p["startTime"])
        pop = (p.get("probabilityOfPrecipitation") or {}).get("value")
        if p["isDaytime"]:
            cur = {"label": start.strftime("%a"), "cond": p["shortForecast"],
                   "kind": icon_kind(p.get("icon", ""), True),
                   "hi": p["temperature"], "lo": None,
                   "pop": pop, "date": start.date()}
            days.append(cur)
        else:
            if cur is not None and cur["lo"] is None and start.date() in (cur["date"],):
                cur["lo"] = p["temperature"]
                if pop is not None:
                    cur["pop"] = max(cur["pop"] or 0, pop)
            elif cur is None:
                # Edition built in the evening: first column is tonight.
                days.append({"label": "Tonight", "cond": p["shortForecast"],
                             "kind": icon_kind(p.get("icon", ""), False),
                             "hi": None, "lo": p["temperature"],
                             "pop": pop, "date": start.date()})
                cur = days[-1]
        if len(days) >= DAYS and cur is not None and cur["lo"] is not None:
            break
    days = days[:DAYS]
    if days and days[0]["label"] not in ("Tonight",):
        days[0]["label"] = "Today"
    return days

def render(days, stamp):
    cols, spoken = [], []
    for d in days:
        temps = ""
        if d["hi"] is not None:
            temps += f'<span class="fc-hi">{d["hi"]}°</span>'
        if d["hi"] is not None and d["lo"] is not None:
            temps += ' <span class="fc-lo">/</span> '
        if d["lo"] is not None:
            temps += f'<span class="fc-lo">{d["lo"]}°</span>'
        pop = f'Precip {d["pop"]}%' if d["pop"] else ("Dry" if d["pop"] == 0 else "")
        cols.append(
            f'<div class="fc-day"><div class="fc-name">{d["label"]}</div>{icon(d["kind"])}'
            f'<div class="fc-cond">{d["cond"]}</div><div class="fc-temps">{temps}</div>'
            f'<div class="fc-pop">{pop}</div></div>')
        s = f'{d["label"]}: {d["cond"].lower()}'
        if d["hi"] is not None:
            s += f', high {d["hi"]}'
        if d["lo"] is not None:
            s += f', low {d["lo"]}'
        if d["pop"]:
            s += f', {d["pop"]}% chance of precipitation'
        spoken.append(s)
    aria = "Five-day forecast for Fiddletown — " + ". ".join(spoken) + "."
    return (
        "<!-- FORECAST:BEGIN — generated by tools/forecast_panel.py from the National Weather "
        "Service forecast at edition time; do not hand-edit (regenerate instead) -->\n"
        f'<div class="fc-panel" role="img" aria-label="{aria}">\n'
        f'<div class="fc-head"><span class="fc-title">The Outlook — Five Days</span>'
        f'<span class="fc-src">National Weather Service · {stamp}</span></div>\n'
        f'<div class="fc-days">{"".join(cols)}</div>\n</div>\n'
        "<!-- FORECAST:END -->")

def main():
    dry = "--dry-run" in sys.argv
    req = urllib.request.Request(FORECAST_URL, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    gen = data["properties"].get("generatedAt") or data["properties"].get("updateTime")
    stamp = datetime.fromisoformat(gen.replace("Z", "+00:00")).astimezone(PT).strftime("%a %b %-d, %-I:%M %p PT")
    panel = render(build_days(data["properties"]["periods"]), stamp)
    if dry:
        print(panel)
        return
    html = INDEX.read_text(encoding="utf-8")
    if 'id="forecast-panel-style"' not in html:
        html = html.replace("</head>", STYLE + "\n</head>", 1)
    if "<!-- FORECAST:BEGIN" in html:
        html = re.sub(r"<!-- FORECAST:BEGIN.*?<!-- FORECAST:END -->", panel, html, flags=re.S)
    else:
        m = re.search(r"(<!-- /LEAD:HEADLINE --></h2>\n)", html)
        if not m:
            sys.exit("ERROR: no FORECAST markers and no lead headline anchor found; index.html untouched.")
        html = html.replace(m.group(1), m.group(1) + panel + "\n", 1)
    INDEX.write_text(html, encoding="utf-8")
    print(f"Forecast panel spliced into index.html (NWS generated {stamp}).")

if __name__ == "__main__":
    main()
