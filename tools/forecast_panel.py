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

DAY PAGES (Dave, Nov 16, 2026): each panel column links to a full day page,
wx-<YYYY-MM-DD>.html in the repo root — an hour-by-hour breakdown for that date
(hourly temperature, precipitation chance by hour, conditions, wind), the day's
high/low and NWS narrative, sunrise/sunset computed for the Fiddletown point,
noteworthy flags (frost, thunderstorms, fog, gusty wind) read off the hourly
data, and any NWS alert overlapping the date. The same run generates the five
pages and prunes day pages outside the current five. The alerts fetch is
best-effort: if it fails the pages still generate, without the alerts block.
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
HOURLY_URL = "https://api.weather.gov/gridpoints/STO/66,60/forecast/hourly"
ALERTS_URL = "https://api.weather.gov/alerts/active?point=38.5035,-120.7574"
LAT, LON = 38.5035, -120.7574
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
a.fc-day{color:inherit;text-decoration:none;-webkit-tap-highlight-color:transparent}
a.fc-day:active{background:rgba(184,134,11,.10)}
.fc-more{font-family:-apple-system,sans-serif;font-size:9.5px;color:var(--muted,#6b6252);margin-top:2px}
.fc-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
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
                   "pop": pop, "date": start.date(),
                   "detail": p.get("detailedForecast", ""), "detail_night": "",
                   "wind": p.get("windSpeed", ""), "wind_dir": p.get("windDirection", "")}
            days.append(cur)
        else:
            if cur is not None and cur["lo"] is None and start.date() in (cur["date"],):
                cur["lo"] = p["temperature"]
                cur["detail_night"] = p.get("detailedForecast", "")
                if pop is not None:
                    cur["pop"] = max(cur["pop"] or 0, pop)
            elif cur is None:
                # Edition built in the evening: first column is tonight.
                days.append({"label": "Tonight", "cond": p["shortForecast"],
                             "kind": icon_kind(p.get("icon", ""), False),
                             "hi": None, "lo": p["temperature"],
                             "pop": pop, "date": start.date(),
                             "detail": "", "detail_night": p.get("detailedForecast", ""),
                             "wind": p.get("windSpeed", ""), "wind_dir": p.get("windDirection", "")})
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
        s = f'{d["label"]}: {d["cond"].lower()}'
        if d["hi"] is not None:
            s += f', high {d["hi"]}'
        if d["lo"] is not None:
            s += f', low {d["lo"]}'
        if d["pop"]:
            s += f', {d["pop"]}% chance of precipitation'
        spoken.append(s)
        href = f'wx-{d["date"].isoformat()}.html'
        cols.append(
            f'<a class="fc-day" href="{href}" aria-label="{s}. Hour-by-hour forecast.">'
            f'<div class="fc-name">{d["label"]}</div>{icon(d["kind"])}'
            f'<div class="fc-cond">{d["cond"]}</div><div class="fc-temps">{temps}</div>'
            f'<div class="fc-pop">{pop}</div><div class="fc-more">hour by hour ›</div></a>')
    aria = "Five-day forecast for Fiddletown — " + ". ".join(spoken) + "."
    return (
        "<!-- FORECAST:BEGIN — generated by tools/forecast_panel.py from the National Weather "
        "Service forecast at edition time; do not hand-edit (regenerate instead) -->\n"
        f'<div class="fc-panel">\n'
        f'<p class="fc-sr">{aria} Tap a day for its hour-by-hour forecast.</p>\n'
        f'<div class="fc-head"><span class="fc-title">The Outlook — Five Days</span>'
        f'<span class="fc-src">National Weather Service · {stamp}</span></div>\n'
        f'<div class="fc-days">{"".join(cols)}</div>\n</div>\n'
        "<!-- FORECAST:END -->")


# --- Day pages (Dave, Nov 16, 2026): one wx-<date>.html per panel day ---------
import math
from datetime import timedelta, timezone

def sun_times(d):
    """Sunrise/sunset for the Fiddletown point (NOAA approximation, ±~2 min)."""
    N = d.timetuple().tm_yday
    lng_hour = LON / 15.0
    def calc(sunrise):
        t = N + (((6 if sunrise else 18) - lng_hour) / 24.0)
        M = (0.9856 * t) - 3.289
        L = (M + 1.916 * math.sin(math.radians(M)) + 0.020 * math.sin(math.radians(2 * M)) + 282.634) % 360
        RA = math.degrees(math.atan(0.91764 * math.tan(math.radians(L)))) % 360
        RA += (math.floor(L / 90) * 90 - math.floor(RA / 90) * 90)
        RA /= 15.0
        sin_dec = 0.39782 * math.sin(math.radians(L))
        cos_dec = math.cos(math.asin(sin_dec))
        cos_h = (math.cos(math.radians(90.833)) - sin_dec * math.sin(math.radians(LAT))) / (cos_dec * math.cos(math.radians(LAT)))
        H = ((360 - math.degrees(math.acos(cos_h))) if sunrise else math.degrees(math.acos(cos_h))) / 15.0
        T = H + RA - 0.06571 * t - 6.622
        UT = (T - lng_hour) % 24
        base = datetime(d.year, d.month, d.day, tzinfo=timezone.utc) + timedelta(hours=UT)
        return base.astimezone(PT)
    return calc(True), calc(False)

def _max_mph(s):
    nums = [int(x) for x in re.findall(r"\d+", s or "")]
    return max(nums) if nums else 0

def _fmt_hour(dt):
    return dt.strftime("%-I %p").replace("AM", "AM").replace("PM", "PM")

WX_STYLE = """<style>
:root{--bg:#f7f1e3;--paper:#fffdf6;--text:#1c1917;--muted:#6b6259;--border:#d8cdb4;--ink:#1c1917;--accent:#8a1f1f;--gold:#b8860b;--rain:#4a7fa5}
@media (prefers-color-scheme: dark){:root{--bg:#141210;--paper:#1e1b18;--text:#ece5d8;--muted:#a89f92;--border:#3d362e;--ink:#ece5d8;--accent:#e0685f;--gold:#e3b341;--rain:#7fb0d6}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:Georgia,'Times New Roman',serif;line-height:1.5}
.wrap{max-width:760px;margin:0 auto;padding:0 14px 40px}
.topbar{position:sticky;top:0;background:var(--paper);border-bottom:2px solid var(--ink);padding:8px 14px;display:flex;justify-content:space-between;align-items:center;z-index:10}
.topbar .brand{font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:12.5px}
.topbar a,.backlink{color:var(--accent);text-decoration:none;font-family:-apple-system,sans-serif;font-size:13px;font-weight:600}
.kicker{font-family:-apple-system,sans-serif;font-size:11.5px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin:22px 0 2px}
h1{font-size:30px;line-height:1.15;margin:0 0 4px}
.sub{color:var(--muted);font-size:14px;margin:0 0 14px}
.card{background:var(--paper);border:1px solid var(--border);border-radius:4px;padding:14px 16px;margin:0 0 14px}
.bigtemps{font-size:34px;margin:2px 0 6px}
.bigtemps .lo{color:var(--muted)}
.detail{font-size:15.5px;margin:6px 0}
.meta{font-family:-apple-system,sans-serif;font-size:12px;color:var(--muted)}
.alert{border:2px solid var(--accent);border-radius:4px;padding:10px 14px;margin:0 0 14px;background:var(--paper)}
.alert b{color:var(--accent)}
.notes li{margin:4px 0}
table.wx{width:100%;border-collapse:collapse;font-size:13.5px}
table.wx th{font-family:-apple-system,sans-serif;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:left;border-bottom:2px solid var(--ink);padding:4px 6px}
table.wx td{border-bottom:1px solid var(--border);padding:5px 6px;vertical-align:top}
table.wx td.t{font-weight:700;white-space:nowrap}
table.wx td.temp{font-weight:700;white-space:nowrap}
table.wx td.pop{color:var(--rain);white-space:nowrap}
table.wx td.wind{white-space:nowrap;color:var(--muted);font-size:12.5px}
tr.wx-now td{background:rgba(184,134,11,.13)}
.nowtag{font-family:-apple-system,sans-serif;font-size:10px;font-weight:800;letter-spacing:.06em;color:var(--gold);text-transform:uppercase}
.wxh{font-family:-apple-system,sans-serif;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:16px 0 2px}
.wxchart{width:100%;height:auto;display:block}
.wxchart text{font-family:-apple-system,sans-serif;fill:var(--muted)}
.daynav{display:flex;justify-content:space-between;gap:10px;font-family:-apple-system,sans-serif;font-size:13.5px;font-weight:600;margin:18px 0 6px}
.daynav a{color:var(--accent);text-decoration:none}
.foot{border-top:3px double var(--ink);margin-top:22px;padding-top:10px}
</style>"""

BEACON = '<script async src="https://visitor-counter.dave-5d7.workers.dev/beacon.js" data-site="fiddletown-gazette"></script>'


# --- Charts (Dave, Nov 16, 2026): inline SVG from the same hourly data --------
# The NWS hourly feed for this point carries NO per-hour precipitation amounts
# and NO gust figures (verified Nov 16, 2026) — the precipitation chart is the
# probability by hour, and the wind chart is sustained speed; the builders use
# windGust the day the feed starts carrying it.
def _cx(h):
    return 30 + (h + 0.5) * 13.5

def _hour_ticks(y):
    out = []
    for h in (0, 3, 6, 9, 12, 15, 18, 21):
        lab = {0: "12a", 3: "3a", 6: "6a", 9: "9a", 12: "12p", 15: "3p", 18: "6p", 21: "9p"}[h]
        out.append(f'<text x="{_cx(h):.0f}" y="{y}" font-size="8" text-anchor="middle">{lab}</text>')
    return "".join(out)

def _slots(hours):
    return {h["_dt"].hour: h for h in hours}

def _temp_scale(temps, top, bottom):
    lo, hi = min(temps) - 2, max(temps) + 2
    return lambda v: top + (hi - v) / (hi - lo) * (bottom - top), lo, hi

def chart_glance(slots, sr, ss):
    hrs = sorted(slots)
    temps = [slots[h]["temperature"] for h in hrs]
    y, tlo, thi = _temp_scale(temps, 16, 84)
    parts = ['<svg class="wxchart" viewBox="0 0 360 118" role="img" aria-label="Day at a glance: temperature line over precipitation bars, with sunrise and sunset marked.">']
    for h in hrs:
        pop = (slots[h].get("probabilityOfPrecipitation") or {}).get("value")
        if pop:
            bh = pop / 100 * 44
            parts.append(f'<rect x="{_cx(h)-4.5:.1f}" y="{88-bh:.1f}" width="9" height="{bh:.1f}" fill="var(--rain)" opacity="0.55"/>')
    parts.append('<line x1="30" y1="88" x2="354" y2="88" stroke="var(--border)"/>')
    for dt, lab in ((sr, "sunrise"), (ss, "sunset")):
        fx = 30 + (dt.hour + dt.minute / 60) / 24 * 324
        parts.append(f'<line x1="{fx:.1f}" y1="12" x2="{fx:.1f}" y2="88" stroke="var(--gold)" stroke-dasharray="2 3" opacity="0.8"/>')
        parts.append(f'<text x="{min(max(fx, 34), 326):.0f}" y="9" font-size="6.5" text-anchor="middle">{lab}</text>')
    pts = " ".join(f"{_cx(h):.1f},{y(slots[h]['temperature']):.1f}" for h in hrs)
    parts.append(f'<polyline points="{pts}" fill="none" stroke="var(--gold)" stroke-width="2"/>')
    hi_h = max(hrs, key=lambda h: slots[h]["temperature"])
    lo_h = min(hrs, key=lambda h: slots[h]["temperature"])
    parts.append(f'<circle cx="{_cx(hi_h):.1f}" cy="{y(slots[hi_h][chr(39) and 'temperature']):.1f}" r="2.6" fill="var(--accent)"/>')
    parts.append(f'<text x="{_cx(hi_h):.0f}" y="{y(slots[hi_h]['temperature'])-5:.0f}" font-size="9" font-weight="700" text-anchor="middle" fill="var(--text)">{slots[hi_h]["temperature"]}°</text>')
    parts.append(f'<circle cx="{_cx(lo_h):.1f}" cy="{y(slots[lo_h]['temperature']):.1f}" r="2.6" fill="var(--rain)"/>')
    parts.append(f'<text x="{_cx(lo_h):.0f}" y="{y(slots[lo_h]['temperature'])+11:.0f}" font-size="9" font-weight="700" text-anchor="middle" fill="var(--text)">{slots[lo_h]["temperature"]}°</text>')
    parts.append(_hour_ticks(102))
    parts.append('</svg>')
    return "".join(parts)

def chart_temp(slots):
    hrs = sorted(slots)
    temps = [slots[h]["temperature"] for h in hrs]
    y, tlo, thi = _temp_scale(temps, 16, 98)
    hi_v, lo_v = max(temps), min(temps)
    mid_v = round((hi_v + lo_v) / 2)
    parts = ['<svg class="wxchart" viewBox="0 0 360 130" role="img" aria-label="Temperature curve across the day.">']
    for v in (hi_v, mid_v, lo_v):
        parts.append(f'<line x1="30" y1="{y(v):.1f}" x2="354" y2="{y(v):.1f}" stroke="var(--border)" stroke-dasharray="1 3"/>')
        parts.append(f'<text x="26" y="{y(v)+3:.0f}" font-size="8.5" text-anchor="end">{v}°</text>')
    pts = " ".join(f"{_cx(h):.1f},{y(slots[h]['temperature']):.1f}" for h in hrs)
    area = f"M{_cx(hrs[0]):.1f},98 L" + " L".join(f"{_cx(h):.1f},{y(slots[h]['temperature']):.1f}" for h in hrs) + f" L{_cx(hrs[-1]):.1f},98 Z"
    parts.append(f'<path d="{area}" fill="var(--gold)" opacity="0.16"/>')
    parts.append(f'<polyline points="{pts}" fill="none" stroke="var(--gold)" stroke-width="2.2"/>')
    hi_h = max(hrs, key=lambda h: slots[h]["temperature"])
    lo_h = min(hrs, key=lambda h: slots[h]["temperature"])
    def _hlab(h):
        return slots[h]["_dt"].strftime("%-I %p")
    parts.append(f'<circle cx="{_cx(hi_h):.1f}" cy="{y(hi_v):.1f}" r="3.2" fill="var(--accent)"/>')
    parts.append(f'<text x="{min(max(_cx(hi_h), 62), 298):.0f}" y="{max(y(hi_v)-7, 9):.0f}" font-size="9.5" font-weight="700" text-anchor="middle" fill="var(--text)">High {hi_v}° · {_hlab(hi_h)}</text>')
    parts.append(f'<circle cx="{_cx(lo_h):.1f}" cy="{y(lo_v):.1f}" r="3.2" fill="var(--rain)"/>')
    parts.append(f'<text x="{min(max(_cx(lo_h), 62), 298):.0f}" y="{min(y(lo_v)+13, 110):.0f}" font-size="9.5" font-weight="700" text-anchor="middle" fill="var(--text)">Low {lo_v}° · {_hlab(lo_h)}</text>')
    parts.append(_hour_ticks(114))
    parts.append('</svg>')
    return "".join(parts)

def chart_precip(slots):
    parts = ['<svg class="wxchart" viewBox="0 0 360 112" role="img" aria-label="Precipitation probability by hour.">']
    for v, lab in ((100, "100%"), (50, "50%"), (0, "0")):
        yy = 84 - v / 100 * 58
        parts.append(f'<line x1="30" y1="{yy:.1f}" x2="354" y2="{yy:.1f}" stroke="var(--border)" stroke-dasharray="1 3"/>')
        parts.append(f'<text x="26" y="{yy+3:.0f}" font-size="8" text-anchor="end">{lab}</text>')
    best_h, best_v = None, -1
    for h in sorted(slots):
        pop = (slots[h].get("probabilityOfPrecipitation") or {}).get("value")
        if pop is None:
            continue
        if pop > best_v:
            best_v, best_h = pop, h
        if pop > 0:
            bh = pop / 100 * 58
            parts.append(f'<rect x="{_cx(h)-4.5:.1f}" y="{84-bh:.1f}" width="9" height="{bh:.1f}" fill="var(--rain)"/>')
    if best_h is not None and best_v > 0:
        parts.append(f'<text x="{_cx(best_h):.0f}" y="{84 - best_v/100*58 - 4:.0f}" font-size="9" font-weight="700" text-anchor="middle" fill="var(--text)">{best_v}%</text>')
    parts.append(_hour_ticks(98))
    parts.append('</svg>')
    return "".join(parts)

def chart_wind(slots):
    speeds = {h: _max_mph(slots[h].get("windSpeed", "")) for h in slots}
    gusts = {h: _max_mph(slots[h].get("windGust") or "") for h in slots}
    top_v = max([10] + list(speeds.values()) + list(gusts.values()))
    top_v = int(math.ceil(top_v / 10.0) * 10)
    parts = ['<svg class="wxchart" viewBox="0 0 360 112" role="img" aria-label="Wind speed by hour, sustained, with gusts where the forecast carries them.">']
    for v in (top_v, top_v // 2, 0):
        yy = 84 - v / top_v * 58
        parts.append(f'<line x1="30" y1="{yy:.1f}" x2="354" y2="{yy:.1f}" stroke="var(--border)" stroke-dasharray="1 3"/>')
        parts.append(f'<text x="26" y="{yy+3:.0f}" font-size="8" text-anchor="end">{v}</text>')
    for h in sorted(slots):
        s = speeds[h]
        if s > 0:
            bh = s / top_v * 58
            parts.append(f'<rect x="{_cx(h)-4.5:.1f}" y="{84-bh:.1f}" width="9" height="{bh:.1f}" fill="var(--muted)" opacity="0.75"/>')
    gpts = [(h, gusts[h]) for h in sorted(slots) if gusts[h] > 0]
    if gpts:
        pts = " ".join(f"{_cx(h):.1f},{84 - g/top_v*58:.1f}" for h, g in gpts)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="var(--accent)" stroke-width="1.6" stroke-dasharray="4 2"/>')
        for h, g in gpts:
            parts.append(f'<circle cx="{_cx(h):.1f}" cy="{84 - g/top_v*58:.1f}" r="2.2" fill="var(--accent)"/>')
    parts.append(_hour_ticks(98))
    parts.append('</svg>')
    return "".join(parts)

def day_page(d, hours, day_alerts, stamp, prev_href, next_href, today):
    date = d["date"]
    sr, ss = sun_times(date)
    daylen = ss - sr
    dl = f"{daylen.seconds // 3600} hours {(daylen.seconds % 3600) // 60} minutes"
    temps = [h["temperature"] for h in hours]
    hi = d["hi"] if d["hi"] is not None else (max(temps) if temps else None)
    lo = d["lo"] if d["lo"] is not None else (min(temps) if temps else None)
    # --- noteworthy flags read off the hourly data ---
    notes = []
    if lo is not None and lo <= 36 and hours:
        coldest = min(hours, key=lambda h: h["temperature"])
        notes.append(f"<b>Frost likely.</b> Temperatures bottom out near {lo}° around {_fmt_hour(coldest['_dt'])} — cover tender plants and mind icy patches on shaded roads at first light.")
    thunder = [h for h in hours if "thunderstorm" in h["shortForecast"].lower()]
    if thunder:
        notes.append(f"<b>Thunderstorms possible</b> from about {_fmt_hour(thunder[0]['_dt'])} to {_fmt_hour(thunder[-1]['_dt'])} — when thunder roars, go indoors.")
    fog = [h for h in hours if "fog" in h["shortForecast"].lower()]
    if fog:
        notes.append(f"<b>Fog</b> in the picture from about {_fmt_hour(fog[0]['_dt'])} to {_fmt_hour(fog[-1]['_dt'])} — slow down in the hollows and on the bridges.")
    if hours:
        windiest = max(hours, key=lambda h: _max_mph(h.get("windSpeed", "")))
        gust = _max_mph(windiest.get("windGust") or "")
        if _max_mph(windiest.get("windSpeed", "")) >= 20 or gust >= 30:
            g = f", gusting to {gust} mph" if gust else ""
            notes.append(f"<b>Gusty.</b> Winds build to {windiest.get('windSpeed','')} from the {windiest.get('windDirection','')} around {_fmt_hour(windiest['_dt'])}{g}.")
        wettest = max(hours, key=lambda h: (h.get("probabilityOfPrecipitation") or {}).get("value") or 0)
        wv = (wettest.get("probabilityOfPrecipitation") or {}).get("value") or 0
        if wv >= 80:
            notes.append(f"<b>Precipitation is near-certain</b> at its peak — a {wv}% chance in the hour around {_fmt_hour(wettest['_dt'])}.")
    notes_html = ""
    if notes:
        notes_html = '<div class="card"><h2 style="margin-top:0">Noteworthy</h2><ul class="notes">' + "".join(f"<li>{n}</li>" for n in notes) + "</ul></div>"
    alerts_html = ""
    for a in day_alerts:
        alerts_html += (f'<div class="alert"><b>⚠ {a["event"]}</b> — {a["headline"]}'
                        f'<br><span class="meta">In effect until {a["expires"]} · National Weather Service</span></div>')
    now_hour = datetime.now(PT).replace(minute=0, second=0, microsecond=0) if date == today else None
    rows = []
    for h in hours:
        pop = (h.get("probabilityOfPrecipitation") or {}).get("value")
        pop_s = f"{pop}%" if pop is not None else "—"
        wind = f'{h.get("windDirection","")} {h.get("windSpeed","")}'.strip()
        gust = h.get("windGust")
        if gust:
            wind += f" · G {gust}"
        cls = ' class="wx-now"' if (now_hour is not None and h["_dt"].replace(minute=0, second=0, microsecond=0) == now_hour) else ""
        tag = ' <span class="nowtag">Now</span>' if cls else ""
        rows.append(f'<tr{cls}><td class="t">{_fmt_hour(h["_dt"])}{tag}</td><td class="temp">{h["temperature"]}°</td>'
                    f'<td class="pop">{pop_s}</td><td>{h["shortForecast"]}</td><td class="wind">{wind}</td></tr>')
    nav = ['<a href="index.html">← Front page</a>']
    mid = ""
    if prev_href:
        mid += f'<a href="{prev_href[0]}">← {prev_href[1]}</a> '
    if next_href:
        mid += f'<a href="{next_href[0]}">{next_href[1]} →</a>'
    nav_html = f'<div class="daynav"><span>{nav[0]}</span><span>{mid}</span></div>'
    slots = _slots(hours)
    if slots:
        maxpop = max(((h.get("probabilityOfPrecipitation") or {}).get("value") or 0) for h in hours)
        dry_note = '<p class="meta">No precipitation expected — the chance reads 0% in every hour.</p>' if maxpop == 0 else ""
        charts_html = ('<div class="card"><h2 style="margin-top:0">The Day in Charts</h2>'
            '<h3 class="wxh">Day at a Glance — temperature over precipitation</h3>' + chart_glance(slots, sr, ss)
            + '<h3 class="wxh">Temperature</h3>' + chart_temp(slots)
            + '<h3 class="wxh">Precipitation Chance by Hour</h3>' + chart_precip(slots) + dry_note
            + '<h3 class="wxh">Wind — sustained speed, mph</h3>' + chart_wind(slots)
            + '<p class="meta">Charts drawn from the same National Weather Service hourly forecast as the table below. The hourly feed carries no per-hour precipitation amounts and no gust figures for this point — amounts, when the Weather Service states them, appear in the narrative above.</p></div>')
    else:
        charts_html = ""
    detail_night = f'<p class="detail"><b>Tonight:</b> {d["detail_night"]}</p>' if d.get("detail_night") else ""
    partial = " Showing the rest of today — the hourly forecast begins at the current hour." if (date == today and 0 < len(hours) < 24) else ""
    detail_day = f'<p class="detail">{d["detail"]}</p>' if d.get("detail") else ""
    wind_line = f' · Wind {d["wind_dir"]} {d["wind"]}' if d.get("wind") else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{date.strftime('%A, %B %-d')} Weather — Fiddletown · The Fiddletown Gazette</title>
<meta name="description" content="Hour-by-hour National Weather Service forecast for Fiddletown, California — {date.strftime('%A, %B %-d, %Y')}: temperatures, precipitation by hour, wind, sunrise and sunset.">
{WX_STYLE}
</head>
<body>
<div class="topbar"><span class="brand">🗞️ The Fiddletown Gazette</span><a href="index.html">Front page →</a></div>
<div class="wrap">
<p class="kicker">🌦️ The Weather Desk — Hour by Hour</p>
<h1>{date.strftime('%A, %B %-d, %Y')}</h1>
<p class="sub">Fiddletown, California · National Weather Service, Sacramento</p>
{alerts_html}
<div class="card">
<div class="bigtemps">{(str(hi) + '°') if hi is not None else ''}{(' <span class="lo">/ ' + str(lo) + '°</span>') if lo is not None else ''}</div>
{detail_day}{detail_night}
<p class="meta">☀️ Sunrise {sr.strftime('%-I:%M %p')} · 🌇 Sunset {ss.strftime('%-I:%M %p')} · {dl} of daylight{wind_line}</p>
</div>
{charts_html}{notes_html}
<div class="card">
<h2 style="margin-top:0">Hour by Hour</h2>
<table class="wx"><tr><th>Hour</th><th>Temp</th><th>Precip</th><th>Conditions</th><th>Wind</th></tr>
{"".join(rows)}
</table>
<p class="meta">Precipitation is the National Weather Service's probability for that hour. Hours are Pacific Time.{partial}</p>
</div>
{nav_html}
<div class="foot">
<p class="meta">Source: National Weather Service forecast for the Fiddletown point (Sacramento office, gridpoint 66,60) · Page generated {stamp} by the Gazette weather desk · <a class="backlink" href="index.html#the-lead">Back to the five-day outlook</a></p>
</div>
</div>
{BEACON}
</body>
</html>
"""

def build_day_pages(days, hourly_periods, alerts, stamp):
    by_date = {}
    for h in hourly_periods:
        dt = datetime.fromisoformat(h["startTime"]).astimezone(PT)
        h = dict(h)
        h["_dt"] = dt
        by_date.setdefault(dt.date(), []).append(h)
    today = datetime.now(PT).date()
    names = {d["date"]: d["date"].strftime("%a") for d in days}
    written = []
    for i, d in enumerate(days):
        date = d["date"]
        day_alerts = []
        for a in alerts:
            try:
                onset = datetime.fromisoformat(a["onset"].replace("Z", "+00:00")).astimezone(PT) if a.get("onset") else None
                expires = datetime.fromisoformat(a["expires"].replace("Z", "+00:00")).astimezone(PT) if a.get("expires") else None
            except Exception:
                continue
            day_start = datetime(date.year, date.month, date.day, tzinfo=PT)
            day_end = day_start + timedelta(days=1)
            if (onset is None or onset < day_end) and (expires is None or expires > day_start):
                day_alerts.append({"event": a.get("event", "Weather alert"),
                                   "headline": a.get("headline", ""),
                                   "expires": expires.strftime("%a %-I:%M %p") if expires else "further notice"})
        prev_href = (f'wx-{days[i-1]["date"].isoformat()}.html', names[days[i-1]["date"]]) if i > 0 else None
        next_href = (f'wx-{days[i+1]["date"].isoformat()}.html', names[days[i+1]["date"]]) if i < len(days) - 1 else None
        html = day_page(d, by_date.get(date, []), day_alerts, stamp, prev_href, next_href, today)
        fn = REPO / f"wx-{date.isoformat()}.html"
        fn.write_text(html, encoding="utf-8")
        written.append(fn.name)
    keep = set(written)
    for old in REPO.glob("wx-*.html"):
        if old.name not in keep and re.fullmatch(r"wx-\d{4}-\d{2}-\d{2}\.html", old.name):
            old.unlink()
    return written


def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    dry = "--dry-run" in sys.argv
    data = fetch_json(FORECAST_URL)
    hourly = fetch_json(HOURLY_URL)["properties"]["periods"]
    try:
        alerts = [f["properties"] for f in fetch_json(ALERTS_URL).get("features", [])]
    except Exception:
        alerts = []  # best-effort: pages still generate without the alerts block
    gen = data["properties"].get("generatedAt") or data["properties"].get("updateTime")
    stamp = datetime.fromisoformat(gen.replace("Z", "+00:00")).astimezone(PT).strftime("%a %b %-d, %-I:%M %p PT")
    days = build_days(data["properties"]["periods"])
    panel = render(days, stamp)
    if dry:
        print(panel)
        return
    written = build_day_pages(days, hourly, alerts, stamp)
    html = INDEX.read_text(encoding="utf-8")
    if 'id="forecast-panel-style"' in html:
        html = re.sub(r'<style id="forecast-panel-style">.*?</style>', lambda m: STYLE, html, count=1, flags=re.S)
    else:
        html = html.replace("</head>", STYLE + "\n</head>", 1)
    if "<!-- FORECAST:BEGIN" in html:
        html = re.sub(r"<!-- FORECAST:BEGIN.*?<!-- FORECAST:END -->", panel, html, flags=re.S)
    else:
        m = re.search(r"(<!-- /LEAD:HEADLINE --></h2>\n)", html)
        if not m:
            sys.exit("ERROR: no FORECAST markers and no lead headline anchor found; index.html untouched.")
        html = html.replace(m.group(1), m.group(1) + panel + "\n", 1)
    INDEX.write_text(html, encoding="utf-8")
    print(f"Forecast panel spliced into index.html (NWS generated {stamp}); day pages: {', '.join(written)}.")

if __name__ == "__main__":
    main()
