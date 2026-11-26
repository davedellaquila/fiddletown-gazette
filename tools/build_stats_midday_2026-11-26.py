#!/usr/bin/env python3
import re
p="stats.html"
s=open(p,encoding="utf-8").read()
def sub(pattern,repl,html,flags=0,label=""):
    new,n=re.subn(pattern,lambda _: repl,html,count=1,flags=flags)
    if n==0: raise SystemExit(f"pattern not found: {label}")
    return new

s=sub(r'Figures as of Thu Nov 26, 2026, about 6:00 AM PT\.','Figures as of Thu Nov 26, 2026, about 12:30 PM PT.',s,label="stamp")
s=sub(r'<div class="num" id="st-total">234</div>','<div class="num" id="st-total">236</div>',s,label="total")
s=sub(r'<div class="num" id="st-today">1</div>','<div class="num" id="st-today">3</div>',s,label="today")
s=sub(r'<div class="num">78</div><div class="what"><b>Editions published</b>','<div class="num">79</div><div class="what"><b>Editions published</b>',s,label="editions")
s=sub(r'<div class="bar-row"><span class="bar-label">Thu Nov 26</span><span class="bar-track"><span class="bar-fill partial" style="width:2%"></span></span><span class="bar-num">1</span></div>','<div class="bar-row"><span class="bar-label">Thu Nov 26</span><span class="bar-track"><span class="bar-fill partial" style="width:7%"></span></span><span class="bar-num">3</span></div>',s,label="today bar")
# Weather & Roads
s=sub(r'A forecast, not a measurement: NWS, via the Morning Edition \(Thu night, Nov 26\)','A forecast, not a measurement: NWS, via the Midday Edition (Thu night, Nov 26)',s,label="low")
s=sub(r'<b>Restrictions on the foothill routes this morning</b><span>Caltrans, 6:02 AM, Thu Nov 26:','<b>Restrictions on the foothill routes at midday</b><span>Caltrans, 12:30 PM, Thu Nov 26:',s,label="restrictions")
s=sub(r'The table as carried in the Morning Edition \(Thu Nov 26\) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear this morning;','The table as carried in the Midday Edition (Thu Nov 26) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear at midday;',s,label="passes wording")
# Accidents & the Wire
s=sub(r'<div class="num">0</div><div class="what"><b>Incidents on the CHP board at the morning read</b><span>6:01 AM, Thu Nov 26 — the Stockton board is empty: no incidents at all, in the beat or anywhere on it</span>','<div class="num">2</div><div class="what"><b>Incidents on the CHP board at the midday read</b><span>12:30 PM, Thu Nov 26 — a hit-and-run with no injuries on SR-49 at Miller Way (Amador area, logged 11:16 AM) and a traffic hazard on I-580 W at Corral Hollow Rd (Tracy); no chain control on the board</span>',s,label="chp count")
s=sub(r'<div class="num">0</div><div class="what"><b>Collisions in the beat today</b><span>None — the morning board holds no incident at all, in the beat or anywhere \(Thu Nov 26\)</span>','<div class="num">1</div><div class="what"><b>Collisions in the beat today</b><span>One — the SR-49 / Miller Way hit-and-run, no injuries, on the midday board (Thu Nov 26); the morning board held none</span>',s,label="beat collisions")
s=sub(r'gone from the CHP board at the morning read and still off it this morning \(Thu Nov 26\)','gone from the CHP board at the morning read and still off it at midday (Thu Nov 26)',s,label="dogs")
# Wine & Around Town — Tasting Room lead corrected to date order (Nov 27 Black Friday first)
s=sub(r'Special winery events across the Shenandoah Valley — the Drytown Cellars holiday open house \(Sat–Sun Dec 12–13\) leads the rail','Special winery events across the Shenandoah Valley — Iron Hub&#8217;s Black Friday at the winery (Fri Nov 27) leads the rail, in date order',s,label="tasting lead")
open(p,"w",encoding="utf-8").write(s)
print("stats ok",len(s))
