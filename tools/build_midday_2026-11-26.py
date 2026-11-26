#!/usr/bin/env python3
import re
p="index.html"
html=open(p,encoding="utf-8").read()
def block_span(html,id_attr,tag="div"):
    m=re.search(r'(<%s[^>]*id="%s"[^>]*>)'%(tag,re.escape(id_attr)),html)
    if not m: raise SystemExit(f"not found {id_attr}")
    start=m.end(); depth=1; pat=re.compile(r'</?%s\b[^>]*>'%tag)
    for mm in pat.finditer(html,start):
        if mm.group(0).startswith('</'):
            depth-=1
            if depth==0: return start,mm.start()
        elif not mm.group(0).endswith('/>'): depth+=1
    raise SystemExit("unbalanced")
def replace_block(html,id_attr,new_inner,tag="div"):
    s,e=block_span(html,id_attr,tag); return html[:s]+new_inner+html[e:]
def sub(pattern,repl,html,flags=0,label=""):
    new,n=re.subn(pattern,lambda _: repl,html,count=1,flags=flags)
    if n==0: raise SystemExit(f"pattern not found: {label or pattern[:90]}")
    return new

html=sub(r'<meta name="fg-edition" content="2026-11-26-morning">','<meta name="fg-edition" content="2026-11-26-midday">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Midday Edition — published 12:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> 🦃 Thanksgiving Day: partly sunny, 63°; tonight mostly cloudy, low 47°; no restrictions on SR-49, SR-88, SR-124 or SR-104 — one CHP incident in the beat: a no-injury hit-and-run on SR-49 at Miller Way (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Thanksgiving midday in the foothills — the trots are run, the roads still carry no restrictions, and the one mark on the day is a no-injury hit-and-run on SR-49 at Miller Way <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Midday on Thanksgiving, and the holiday&#8217;s morning business is done: the <b>Jackson Turkey Trot at Lake Tabeaud (8:00 AM)</b> and the <b>Sutter Creek Turkey Trot at Cribbs Field (9:00 AM)</b> have run, and <b>Preschool Story Time at the Jackson Library (10:30 AM)</b> has wrapped — the three events the database carried for today, all of them morning affairs. The roads picture is nearly as clean as the morning&#8217;s: <b>no National Weather Service alert is in effect</b> for the Fiddletown point, and <b>Caltrans&#8217; midday reports list no restrictions on SR-49, SR-88, SR-124, or SR-104</b> — no closures, no chain control. The one new item is on the CHP board: a <b>hit-and-run with no injuries on northbound SR-49 at Miller Way, logged 11:16 AM</b> (see the Safety Wire) — drive the highway stretch with care. <b>This afternoon:</b> partly sunny, high near 63, easing to around 57. <b>Tonight:</b> mostly cloudy, low near 47. Tomorrow is Black Friday, foothills style — wine-country sales across Plymouth and Shenandoah, Sutter Creek Plaid Friday, and Jackson&#8217;s Christmas Delights opening (see The Week Ahead). <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>CHP — a no-injury hit-and-run on SR-49 at Miller Way, logged late morning.</b> The Stockton center&#8217;s board, updated <b>12:30 PM</b>, holds two incidents. The one in the beat: a <b>hit-and-run, no injuries, on <a href="https://maps.apple.com/?q=SR-49%20%2F%20Miller%20Way%2C%20Amador%20County%2C%20CA">SR-49 / Miller Way</a> (northbound SR-49, Amador area), logged 11:16 AM</b>. The other is out of the beat: a traffic hazard on I-580 W at the Corral Hollow Rd on-ramp (Tracy), logged 11:14 AM. There is <b>no chain control</b> on the board.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 12:30 PM PT, Nov 26</p></div>
    <div class="item"><p><b>Roads — still clear on every route the paper checks.</b> Caltrans&#8217; midday reports list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four, the same clear picture as this morning.</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, checked 12:30 PM PT, Nov 26</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a fair afternoon, a cloudier night.</b> At the midday check (12:30 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>This afternoon:</b> partly sunny, high near 63, temperatures falling to around 57. <b>Tonight:</b> mostly cloudy, low near 47. The weekend turns: a slight chance of rain late Saturday night, then rain likely Sunday (see the Outlook panel in the Lead).</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 12:30 PM PT, Nov 26</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the midday check.</b> No fire incident in the beat appears on the CHP board at midday. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 12:30 PM PT, Nov 26</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>Thanksgiving morning — a short, good list\.</b>.*?</p>','<p><b>Thanksgiving midday — the day&#8217;s list has run its course, all of it this morning.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>three in-beat events spanned today</b>, listed below as cards, verified against the feed at midday and unchanged from the morning edition. All three were morning affairs and have wrapped: the <b>Jackson Turkey Trot at Lake Tabeaud, 8:00 AM</b>, the <b>Sutter Creek Turkey Trot at Cribbs Field, 9:00 AM</b>, and <b>Preschool Story Time at the Jackson Library, 10:30 AM</b>. Nothing else in the database remains on today&#8217;s calendar — the rest of Thanksgiving belongs to the tables. <b>Tomorrow, Fri Nov 27 — Black Friday, foothills style, in the database:</b> wine-country Black Friday sales across Plymouth and Shenandoah (Bella Grace&#8217;s Black Friday at the Cave, 9:00 AM; Avio and Black Snake at 11:00 AM; Iron Hub, Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Golden Leaves), Sutter Creek Plaid Friday, and Jackson&#8217;s Christmas Delights opening with the Festival of Trees at 6:00 PM (see The Week Ahead).</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

html=sub(r'<div class="item"><p><b>Today, Thu Nov 26 — Thanksgiving Day:</b>.*?</div>','<div class="item"><p><b>Today, Thu Nov 26 — Thanksgiving Day, the rest of the day:</b> the morning&#8217;s three database events have run — <b>Jackson Turkey Trot</b>, Lake Tabeaud, 8:00 AM · <b>Sutter Creek Turkey Trot</b>, Cribbs Field, 9:00 AM · <b>Preschool Story Time</b>, Jackson Library, 10:30 AM — and nothing further is on today&#8217;s calendar in the database; see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>',html,flags=re.S,label="week today")

html=sub(r'The desk re-checked the home crossing this morning — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; morning web report lists no restrictions on SR-88, and the CHP CAD board \(updated 6:01 AM today\) holds no incidents at all \(see the Safety Wire\)\.','The desk re-checked the home crossing at midday — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; midday web report lists no restrictions on SR-88, and the CHP CAD board (updated 12:30 PM today) holds no SR-88 incident (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 6:01 AM today\)','(CHP CAD + Caltrans, 12:30 PM today)',html,label="carson row")

open(p,"w",encoding="utf-8").write(html)
print("midday build ok",len(html))
