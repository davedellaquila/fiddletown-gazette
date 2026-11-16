#!/usr/bin/env python3
"""Moon data for the Gazette weather day pages' Almanac card (Dave, Nov 16, 2026).

Run with the sky desk's venv python (~/workspace/briefings/.venv-sky/bin/python),
which has skyfield; the ephemeris (de421.bsp) is the briefings desk's cached copy —
no network needed. tools/forecast_panel.py calls this once per run for all five
panel dates and reads JSON on stdout:

    {"2026-11-16": {"moonrise": "7:42 AM", "moonset": "6:05 PM",
                    "phase": "Waxing gibbous", "illum": 78}, ...}

A missing moonrise/moonset key means the event does not fall on that local date.
On any failure this script exits nonzero and the day pages print their Almanac
card with the sun rows only (forecast_panel.py treats moon data as best-effort).
"""
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from skyfield.api import Loader, wgs84
from skyfield import almanac

LAT, LON = 38.5035, -120.7574
PT = ZoneInfo("America/Los_Angeles")
EPH_DIR = os.path.expanduser("~/workspace/briefings/ephemeris")

def phase_name(angle):
    a = angle % 360.0
    if a < 1.8 or a >= 358.2:
        return "New Moon"
    if a < 88.2:
        return "Waxing Crescent"
    if a < 91.8:
        return "First Quarter"
    if a < 178.2:
        return "Waxing Gibbous"
    if a < 181.8:
        return "Full Moon"
    if a < 268.2:
        return "Waning Gibbous"
    if a < 271.8:
        return "Last Quarter"
    return "Waning Crescent"

def main():
    dates = sys.argv[1:]
    if not dates:
        sys.exit("usage: almanac_moon.py YYYY-MM-DD [YYYY-MM-DD ...]")
    load = Loader(EPH_DIR)
    ts = load.timescale()
    eph = load("de421.bsp")
    earth, moon = eph["earth"], eph["moon"]
    topos = wgs84.latlon(LAT, LON)

    observer = earth + topos

    def moon_up(t):
        alt = observer.at(t).observe(moon).apparent().altaz()[0].degrees
        return alt > -0.583  # upper limb + refraction, the almanac convention

    moon_up.step_days = 0.02

    out = {}
    for ds in dates:
        d = datetime.strptime(ds, "%Y-%m-%d").date()
        start = datetime(d.year, d.month, d.day, tzinfo=PT)
        end = start + timedelta(days=1)
        t0, t1 = ts.from_datetime(start), ts.from_datetime(end)
        times, states = almanac.find_discrete(t0, t1, moon_up)
        rec = {}
        for t, now_up in zip(times, states):
            local = t.utc_datetime().astimezone(PT)
            label = local.strftime("%-I:%M %p")
            if now_up and "moonrise" not in rec:
                rec["moonrise"] = label  # state after the crossing is UP: it rose
            if not now_up and "moonset" not in rec:
                rec["moonset"] = label  # state after the crossing is DOWN: it set
        noon = ts.from_datetime(start + timedelta(hours=12))
        ang = float(almanac.moon_phase(eph, noon).degrees)
        import math
        rec["phase"] = phase_name(ang)
        rec["illum"] = round((1 - math.cos(math.radians(ang))) / 2 * 100)
        out[ds] = rec
    print(json.dumps(out))

if __name__ == "__main__":
    main()
