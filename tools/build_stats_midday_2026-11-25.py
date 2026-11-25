#!/usr/bin/env python3
import re
p="stats.html"
s=open(p,encoding="utf-8").read()
def sub(pattern,repl,html,flags=0,label=""):
    new,n=re.subn(pattern,lambda _: repl,html,count=1,flags=flags)
    if n==0: raise SystemExit(f"pattern not found: {label}")
    return new

s=sub(r'Figures as of Wed Nov 25, 2026, about 6:00 AM PT\.','Figures as of Wed Nov 25, 2026, about 12:30 PM PT.',s,label="stamp")
s=sub(r'<div class="num" id="st-total">217</div>','<div class="num" id="st-total">225</div>',s,label="total")
s=sub(r'<div class="num" id="st-today">2</div>','<div class="num" id="st-today">10</div>',s,label="today")
s=sub(r'<div class="num">75</div><div class="what"><b>Editions published</b>','<div class="num">76</div><div class="what"><b>Editions published</b>',s,label="editions")
s=sub(r'<div class="num" id="st-thumbs">0</div>','<div class="num" id="st-thumbs">1</div>',s,label="thumbs")
s=sub(r'<div class="bar-row"><span class="bar-label">Wed Nov 25</span><span class="bar-track"><span class="bar-fill partial" style="width:5%"></span></span><span class="bar-num">2</span></div>','<div class="bar-row"><span class="bar-label">Wed Nov 25</span><span class="bar-track"><span class="bar-fill partial" style="width:24%"></span></span><span class="bar-num">10</span></div>',s,label="today bar")
s=sub(r'👍 per section, all-time — 22 👍 across 17 sections','👍 per section, all-time — 23 👍 across 18 sections',s,label="votes header")
# add Talk of the Table row after Week Ahead row in sections chart
s=sub(r'(<div class="bar-row"><span class="bar-label" style="flex-basis:210px">The Week Ahead</span><span class="bar-track"><span class="bar-fill" style="width:33%"></span></span><span class="bar-num">1</span></div>)',r'\1<div class="bar-row"><span class="bar-label" style="flex-basis:210px">🧺 Talk of the Table</span><span class="bar-track"><span class="bar-fill" style="width:33%"></span></span><span class="bar-num">1</span></div>',s,label="talk row")
# Weather & Roads
s=sub(r'<div class="num">44°</div><div class="what"><b>Tonight&#8217;s forecast low</b><span>A forecast, not a measurement: NWS, via this morning&#8217;s paper \(Wed night, Nov 25\) — partly cloudy, low ne[^<]*</span>','<div class="num">46°</div><div class="what"><b>Tonight&#8217;s forecast low</b><span>A forecast, not a measurement: NWS, via the Midday Edition (Wed night, Nov 25) — mostly cloudy, low near 46, rising to around 48 overnight</span>',s,label="low")
s=sub(r'<div class="num">None</div><div class="what"><b>Restrictions on the foothill routes this morning</b><span>Caltrans, 6:02 AM, Wed Nov 25: SR-49, SR-88, SR-124 and SR-104 all report no restrictions — no closures, no on[^<]*</span>','<div class="num">None</div><div class="what"><b>Restrictions on the foothill routes at midday</b><span>Caltrans, 12:30 PM, Wed Nov 25: SR-49, SR-88, SR-124 and SR-104 all report no restrictions — no closures, no one-way control, and no chain control</span>',s,label="restrictions")
s=sub(r'The table as carried in this morning&#8217;s paper \(Wed Nov 25\)','The table as carried in the Midday Edition (Wed Nov 25)',s,label="passes wording")
# Accidents & the Wire — replace whole card stats via targeted subs
s=sub(r'<div class="num">1</div><div class="what"><b>Incident on the CHP board at the morning read</b><span>6:01 AM, Wed Nov 25 — a single assist-with-construction on SR-4 at Stanley Rd, in the Stockton area; nothing i[^<]*</span>','<div class="num">2</div><div class="what"><b>Incidents on the CHP board at the midday read</b><span>12:30 PM, Wed Nov 25 — a no-injury collision on I-205 E at W Grant Line Rd (Tracy) and an assist-with-construction on SR-4 at Stanley Rd (Stockton area); none of them in the Fiddletown beat</span>',s,label="chp count")
s=sub(r'<div class="num">0</div><div class="what"><b>Collisions in the beat today</b><span>None — the morning board holds no incident in the beat at all \(Wed Nov 25\)</span>','<div class="num">0</div><div class="what"><b>Collisions in the beat today</b><span>None — the midday board holds no incident in the beat at all (Wed Nov 25)</span>',s,label="beat collisions")
s=sub(r'Logged Tue Nov 24 at 5:09 PM — two large dogs in the roadway at Bell Rd; gone from the CHP board at this morni[^<]*','Logged Tue Nov 24 at 5:09 PM — two large dogs in the roadway at Bell Rd; gone from the CHP board at the morning read and still off it at midday (Wed Nov 25)',s,label="dogs")
open(p,"w",encoding="utf-8").write(s)
print("stats ok",len(s))
