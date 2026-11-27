#!/usr/bin/env python3
import re
p="stats.html"
s=open(p,encoding="utf-8").read()
def sub(pattern,repl,html,flags=0,label=""):
    new,n=re.subn(pattern,lambda _: repl,html,count=1,flags=flags)
    if n==0: raise SystemExit(f"pattern not found: {label}")
    return new

s=sub(r'Figures as of Fri Nov 27, 2026, about 6:00 AM PT\.','Figures as of Fri Nov 27, 2026, about 12:30 PM PT.',s,label="stamp")
s=sub(r'<div class="num" id="st-total">250</div>','<div class="num" id="st-total">253</div>',s,label="total")
s=sub(r'<div class="num" id="st-today">0</div>','<div class="num" id="st-today">3</div>',s,label="today")
s=sub(r'<div class="num">81</div><div class="what"><b>Editions published</b>','<div class="num">82</div><div class="what"><b>Editions published</b>',s,label="editions")
s=sub(r'<div class="bar-row"><span class="bar-label">Fri Nov 27</span><span class="bar-track"><span class="bar-fill partial" style="width:0%"></span></span><span class="bar-num">0</span></div>','<div class="bar-row"><span class="bar-label">Fri Nov 27</span><span class="bar-track"><span class="bar-fill partial" style="width:7%"></span></span><span class="bar-num">3</span></div>',s,label="today bar")
# Weather & Roads
s=sub(r'A forecast, not a measurement: NWS, via the Morning Edition \(Fri night, Nov 27\)','A forecast, not a measurement: NWS, via the Midday Edition (Fri night, Nov 27)',s,label="low")
s=sub(r'<b>Restrictions on the foothill routes this morning</b><span>Caltrans, 6:02 AM, Fri Nov 27:','<b>Restrictions on the foothill routes at midday</b><span>Caltrans, 12:30 PM, Fri Nov 27:',s,label="restrictions")
s=sub(r'The table as carried in the Morning Edition \(Fri Nov 27\) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear this morning;','The table as carried in the Midday Edition (Fri Nov 27) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear at midday;',s,label="passes wording")
# Accidents & the Wire
s=sub(r'<div class="num">1</div><div class="what"><b>Incidents on the CHP board at the morning read</b><span>6:04 AM, Fri Nov 27 — one incident on the whole Stockton board: a traffic hazard on SR-26 at Jack Tone Rd, west of the beat; nothing in the beat, and no chain control</span>','<div class="num">0</div><div class="what"><b>Incidents on the CHP board at the midday read</b><span>12:30 PM, Fri Nov 27 — the Stockton board is empty: no incidents at all, in the beat or anywhere on it; the morning&#8217;s SR-26 traffic hazard has cleared, and no chain control is listed</span>',s,label="chp count")
s=sub(r'<div class="num">0</div><div class="what"><b>Collisions in the beat today</b><span>None — the morning board&#8217;s only incident is the SR-26 traffic hazard west of the beat \(Fri Nov 27\)</span>','<div class="num">0</div><div class="what"><b>Collisions in the beat today</b><span>None — the midday board is empty, and the morning board&#8217;s only incident was the SR-26 traffic hazard west of the beat (Fri Nov 27)</span>',s,label="beat collisions")
s=sub(r'gone from the CHP board at the morning read and still off it this morning \(Fri Nov 27\)','gone from the CHP board at the morning read and still off it at midday (Fri Nov 27)',s,label="dogs")
open(p,"w",encoding="utf-8").write(s)
print("stats ok",len(s))
