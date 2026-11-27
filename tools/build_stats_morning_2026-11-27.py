#!/usr/bin/env python3
import re
p="stats.html"
s=open(p,encoding="utf-8").read()
def sub(pattern,repl,html,flags=0,label=""):
    new,n=re.subn(pattern,lambda _: repl,html,count=1,flags=flags)
    if n==0: raise SystemExit(f"pattern not found: {label}")
    return new

s=sub(r'Figures as of Thu Nov 26, 2026, about 5:30 PM PT\.','Figures as of Fri Nov 27, 2026, about 6:00 AM PT.',s,label="stamp")
s=sub(r'<div class="num" id="st-total">242</div>','<div class="num" id="st-total">250</div>',s,label="total")
s=sub(r'<div class="num" id="st-today">9</div>','<div class="num" id="st-today">0</div>',s,label="today")
s=sub(r'Window: Nov 15 – Nov 26, 2026','Window: Nov 15 – Nov 27, 2026',s,label="window")
s=sub(r'<span>Thu Nov 26, as of the stamp above</span>','<span>Fri Nov 27, as of the stamp above</span>',s,label="today span")
s=sub(r'<div class="num">80</div><div class="what"><b>Editions published</b>','<div class="num">81</div><div class="what"><b>Editions published</b>',s,label="editions")
s=sub(r'Sat Oct 31 – Thu Nov 26, 2026 · morning, midday, and evening','Sat Oct 31 – Fri Nov 27, 2026 · morning, midday, and evening',s,label="editions span")
s=sub(r'<div class="bar-row"><span class="bar-label">Thu Nov 26</span><span class="bar-track"><span class="bar-fill partial" style="width:22%"></span></span><span class="bar-num">9</span></div>',
      '<div class="bar-row"><span class="bar-label">Thu Nov 26</span><span class="bar-track"><span class="bar-fill" style="width:41%"></span></span><span class="bar-num">17</span></div><div class="bar-row"><span class="bar-label">Fri Nov 27</span><span class="bar-track"><span class="bar-fill partial" style="width:0%"></span></span><span class="bar-num">0</span></div>',s,label="readers bars")
# Weather & Roads
s=sub(r'<div class="num">9h 47m</div><div class="what"><b>Daylight today</b><span>Sunrise 6:56 AM · sunset 4:43 PM · Thu Nov 26</span></div>','<div class="num">9h 46m</div><div class="what"><b>Daylight today</b><span>Sunrise 6:57 AM · sunset 4:43 PM · Fri Nov 27</span></div>',s,label="daylight")
s=sub(r'<div class="num">5h 05m</div>','<div class="num">5h 06m</div>',s,label="daylight lost")
s=sub(r'<div class="num">47°</div><div class="what"><b>Tonight&#8217;s forecast low</b><span>A forecast, not a measurement: NWS, via the Evening Edition \(Thu night, Nov 26\) — mostly cloudy, low near 47, rising to around 49 overnight</span>','<div class="num">50°</div><div class="what"><b>Tonight&#8217;s forecast low</b><span>A forecast, not a measurement: NWS, via the Morning Edition (Fri night, Nov 27) — mostly cloudy, low near 50, rising to around 52 overnight</span>',s,label="low")
s=sub(r'<b>Restrictions on the foothill routes this evening</b><span>Caltrans, 5:26 PM, Thu Nov 26: SR-49, SR-88, SR-124 and SR-104 all report no restrictions — no closures, no one-way control, and no chain control</span>','<b>Restrictions on the foothill routes this morning</b><span>Caltrans, 6:02 AM, Fri Nov 27: SR-49, SR-88, SR-124 and SR-104 all report no restrictions — no closures, no one-way control, and no chain control</span>',s,label="restrictions")
s=sub(r'The table as carried in the Evening Edition \(Thu Nov 26\) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear this evening;','The table as carried in the Morning Edition (Fri Nov 27) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear this morning;',s,label="passes wording")
# Accidents & the Wire
s=sub(r'<div class="num">0</div><div class="what"><b>Incidents on the CHP board at the evening read</b><span>5:26 PM, Thu Nov 26 — the Stockton board is empty: no incidents at all, in the beat or anywhere on it; no chain control</span>','<div class="num">1</div><div class="what"><b>Incidents on the CHP board at the morning read</b><span>6:04 AM, Fri Nov 27 — one incident on the whole Stockton board: a traffic hazard on SR-26 at Jack Tone Rd, west of the beat; nothing in the beat, and no chain control</span>',s,label="chp count")
s=sub(r'<div class="num">1</div><div class="what"><b>Collisions in the beat today</b><span>One — the SR-49 / Miller Way hit-and-run, no injuries, on the midday board \(Thu Nov 26\); it had cleared by the evening read, when the board was empty</span>','<div class="num">0</div><div class="what"><b>Collisions in the beat today</b><span>None — the morning board&#8217;s only incident is the SR-26 traffic hazard west of the beat (Fri Nov 27)</span>',s,label="beat collisions")
s=sub(r'gone from the CHP board at the morning read and still off it this evening \(Thu Nov 26\)','gone from the CHP board at the morning read and still off it this morning (Fri Nov 27)',s,label="dogs")
# Wine & Around Town — counted from the new front page
s=sub(r'Counted from today&#8217;s paper \(Thu Nov 26\)','Counted from today&#8217;s paper (Fri Nov 27)',s,label="counted-from date")
s=sub(r'<div class="num">3</div><div class="what"><b>Events in Today in the Foothills</b><span>Today&#8217;s cards, Thu Nov 26 — Thanksgiving Day: the Jackson and Sutter Creek turkey trots in the morning and Preschool Story Time at the Jackson Library</span></div>','<div class="num">16</div><div class="what"><b>Events in Today in the Foothills</b><span>Today&#8217;s cards, Fri Nov 27 — Black Friday: Bella Grace&#8217;s cave sale at 9:00 AM leads a dozen winery sales, Sutter Creek runs Plaid Friday, and Jackson&#8217;s Christmas Delights opens tonight</span></div>',s,label="today count")
# Fun Ledger
s=sub(r'<div class="num">11</div><div class="what"><b>Road Markers of the Day featured so far</b><span>No\. 11 — the Original Amador Mine, Amador City — ran today \(Thu Nov 26\); No\. 10 was the Keystone Mine</span></div>','<div class="num">12</div><div class="what"><b>Road Markers of the Day featured so far</b><span>No. 12 — the Marguerite Mine &#8220;Quartz Rock,&#8221; Auburn — ran today (Fri Nov 27); No. 11 was the Original Amador Mine</span></div>',s,label="markers ledger")
s=sub(r'<div class="num">13</div><div class="what"><b>Zen sayings published</b>','<div class="num">14</div><div class="what"><b>Zen sayings published</b>',s,label="zen ledger")
s=sub(r'<div class="num">27</div><div class="what"><b>Daily jokes told</b>','<div class="num">28</div><div class="what"><b>Daily jokes told</b>',s,label="jokes ledger")
s=sub(r'<div class="num">27</div><div class="what"><b>Days of publication</b><span>Sat Oct 31 – Thu Nov 26, 2026 — three editions a day and counting</span></div>','<div class="num">28</div><div class="what"><b>Days of publication</b><span>Sat Oct 31 – Fri Nov 27, 2026 — three editions a day and counting</span></div>',s,label="days ledger")
open(p,"w",encoding="utf-8").write(s)
print("stats ok",len(s))
