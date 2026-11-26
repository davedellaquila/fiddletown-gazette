#!/usr/bin/env python3
import re
p="stats.html"
s=open(p,encoding="utf-8").read()
def sub(pattern,repl,html,flags=0,label=""):
    new,n=re.subn(pattern,lambda _: repl,html,count=1,flags=flags)
    if n==0: raise SystemExit(f"pattern not found: {label}")
    return new

s=sub(r'Figures as of Wed Nov 25, 2026, about 5:30 PM PT\.','Figures as of Thu Nov 26, 2026, about 6:00 AM PT.',s,label="stamp")
s=sub(r'<div class="num" id="st-total">228</div>','<div class="num" id="st-total">234</div>',s,label="total")
s=sub(r'<div class="num" id="st-today">13</div>','<div class="num" id="st-today">1</div>',s,label="today")
s=sub(r'Window: Nov 15 – Nov 25, 2026','Window: Nov 15 – Nov 26, 2026',s,label="window")
s=sub(r'<span>Wed Nov 25, as of the stamp above</span>','<span>Thu Nov 26, as of the stamp above</span>',s,label="today span")
s=sub(r'<div class="num">77</div><div class="what"><b>Editions published</b>','<div class="num">78</div><div class="what"><b>Editions published</b>',s,label="editions")
s=sub(r'Sat Oct 31 – Wed Nov 25, 2026 · morning, midday, and evening','Sat Oct 31 – Thu Nov 26, 2026 · morning, midday, and evening',s,label="editions span")
s=sub(r'<div class="num" id="st-thumbs">1</div>','<div class="num" id="st-thumbs">0</div>',s,label="thumbs")
# Visitors chart: close Wed Nov 25 at 17 (Analytics Buddy canonical), add Thu Nov 26 partial
s=sub(r'<div class="bar-row"><span class="bar-label">Wed Nov 25</span><span class="bar-track"><span class="bar-fill partial" style="width:32%"></span></span><span class="bar-num">13</span></div>',
      '<div class="bar-row"><span class="bar-label">Wed Nov 25</span><span class="bar-track"><span class="bar-fill" style="width:41%"></span></span><span class="bar-num">17</span></div><div class="bar-row"><span class="bar-label">Thu Nov 26</span><span class="bar-track"><span class="bar-fill partial" style="width:2%"></span></span><span class="bar-num">1</span></div>',s,label="readers bars")
# Weather & Roads
s=sub(r'<div class="num">9h 48m</div><div class="what"><b>Daylight today</b><span>Sunrise 6:55 AM · sunset 4:44 PM · Wed Nov 25</span></div>','<div class="num">9h 47m</div><div class="what"><b>Daylight today</b><span>Sunrise 6:56 AM · sunset 4:43 PM · Thu Nov 26</span></div>',s,label="daylight")
s=sub(r'<div class="num">5h 04m</div>','<div class="num">5h 05m</div>',s,label="daylight lost")
s=sub(r'<div class="num">46°</div><div class="what"><b>Tonight&#8217;s forecast low</b><span>A forecast, not a measurement: NWS, via the Evening Edition \(Wed night, Nov 25\) — mostly cloudy, low near 46, rising to around 48 overnight</span>','<div class="num">47°</div><div class="what"><b>Tonight&#8217;s forecast low</b><span>A forecast, not a measurement: NWS, via the Morning Edition (Thu night, Nov 26) — mostly cloudy, low near 47, rising to around 49 overnight</span>',s,label="low")
s=sub(r'<b>Restrictions on the foothill routes this evening</b><span>Caltrans, 5:26 PM, Wed Nov 25: SR-49, SR-88, SR-124 and SR-104 all report no restrictions — no closures, no one-way control, and no chain control</span>','<b>Restrictions on the foothill routes this morning</b><span>Caltrans, 6:02 AM, Thu Nov 26: SR-49, SR-88, SR-124 and SR-104 all report no restrictions — no closures, no one-way control, and no chain control</span>',s,label="restrictions")
s=sub(r'The table as carried in the Evening Edition \(Wed Nov 25\) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear this evening;','The table as carried in the Morning Edition (Thu Nov 26) — 21 crossings, Morgan Summit to Tioga; statuses last fully read Thu–Fri, except SR-88, re-checked clear this morning;',s,label="passes wording")
# Accidents & the Wire
s=sub(r'<div class="num">2</div><div class="what"><b>Incidents on the CHP board at the evening read</b><span>5:26 PM, Wed Nov 25 — a no-injury collision on SR-26 at Dirt Rd \(San Andreas area\) and an assist-with-construction on SR-4 at Stanley Rd \(Stockton area\); none of them in the Fiddletown beat</span>','<div class="num">0</div><div class="what"><b>Incidents on the CHP board at the morning read</b><span>6:01 AM, Thu Nov 26 — the Stockton board is empty: no incidents at all, in the beat or anywhere on it</span>',s,label="chp count")
s=sub(r'<span>None — the evening board holds no incident in the beat at all \(Wed Nov 25\)</span>','<span>None — the morning board holds no incident at all, in the beat or anywhere (Thu Nov 26)</span>',s,label="beat collisions")
s=sub(r'gone from the CHP board at the morning read and still off it at the evening read \(Wed Nov 25\)','gone from the CHP board at the morning read and still off it this morning (Thu Nov 26)',s,label="dogs")
# Wine & Around Town — counted from the new front page
s=sub(r'Counted from today&#8217;s paper \(Wed Nov 25\)','Counted from today&#8217;s paper (Thu Nov 26)',s,label="counted-from date")
s=sub(r'<div class="num">5</div><div class="what"><b>Items in Around Town</b><span>Restaurants, galleries, and town news — the Friendsgiving shout-out for Dylan Punturo leads; his show is tonight, Wed Nov 25</span></div>','<div class="num">3</div><div class="what"><b>Items in Around Town</b><span>Restaurants, galleries, and town news — Volcano&#8217;s holiday galleries lead; the spent Thanksgiving-eve items (the Friendsgiving shout-out and Luka&#8217;s pickup) retired with their day</span></div>',s,label="around count")
s=sub(r'<div class="num">6</div><div class="what"><b>Events in Today in the Foothills</b><span>Today&#8217;s cards, Wed Nov 25 — Preschool Story Time at the Plymouth Library leads the afternoon, and a double Friendsgiving \(the Plymouth Hotel dinner and the Placerville show\) closes the night</span></div>','<div class="num">3</div><div class="what"><b>Events in Today in the Foothills</b><span>Today&#8217;s cards, Thu Nov 26 — Thanksgiving Day: the Jackson and Sutter Creek turkey trots in the morning and Preschool Story Time at the Jackson Library</span></div>',s,label="today count")
s=sub(r'<div class="num">Ends today</div><div class="what"><b>Thanksgiving pickup at Baked in Amador</b><span>Final pickup Wed Nov 25, 11:00 AM–3:00 PM, in Volcano; the order book closed Sun Nov 22</span></div>','<div class="num">Sat Nov 28</div><div class="what"><b>Next Sourdough Breakfast at Baked in Amador</b><span>The standing Saturday breakfast returns Sat Nov 28, 8:00–11:00 AM, in Volcano; the Thanksgiving preorder run closed Wed Nov 25</span></div>',s,label="baked stat")
# Fun Ledger
s=sub(r'<div class="num">10</div><div class="what"><b>Road Markers of the Day featured so far</b><span>No\. 10 — the Keystone Mine, Amador City — ran today \(Wed Nov 25\); No\. 9 was the Imperial Hotel</span></div>','<div class="num">11</div><div class="what"><b>Road Markers of the Day featured so far</b><span>No. 11 — the Original Amador Mine, Amador City — ran today (Thu Nov 26); No. 10 was the Keystone Mine</span></div>',s,label="markers ledger")
s=sub(r'<div class="num">12</div><div class="what"><b>Zen sayings published</b>','<div class="num">13</div><div class="what"><b>Zen sayings published</b>',s,label="zen ledger")
s=sub(r'<div class="num">26</div><div class="what"><b>Daily jokes told</b>','<div class="num">27</div><div class="what"><b>Daily jokes told</b>',s,label="jokes ledger")
s=sub(r'<div class="num">26</div><div class="what"><b>Days of publication</b><span>Sat Oct 31 – Wed Nov 25, 2026 — three editions a day and counting</span></div>','<div class="num">27</div><div class="what"><b>Days of publication</b><span>Sat Oct 31 – Thu Nov 26, 2026 — three editions a day and counting</span></div>',s,label="days ledger")
open(p,"w",encoding="utf-8").write(s)
print("stats ok",len(s))
