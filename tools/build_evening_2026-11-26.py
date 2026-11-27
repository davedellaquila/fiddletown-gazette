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

html=sub(r'<meta name="fg-edition" content="2026-11-26-midday">','<meta name="fg-edition" content="2026-11-26-evening">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Evening Edition — published 5:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> 🦃 Thanksgiving evening: mostly cloudy, low 47°; Friday mostly cloudy, 63°; roads clear — no restrictions on SR-49, SR-88, SR-124 or SR-104, and the CHP board is empty at the evening read; no NWS alert (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Thanksgiving evening in the foothills — the tables are full, the roads are clear on every route the paper checks, and the CHP board that carried a hit-and-run at midday is empty tonight <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Evening on Thanksgiving, and the day closes clean. The morning&#8217;s three database events have long since run — the <b>Jackson Turkey Trot at Lake Tabeaud (8:00 AM)</b>, the <b>Sutter Creek Turkey Trot at Cribbs Field (9:00 AM)</b>, and <b>Preschool Story Time at the Jackson Library (10:30 AM)</b> — and nothing else remains on today&#8217;s calendar in the database; the rest of the day belongs to the tables. The safety picture improved through the afternoon: at the evening check, <b>no National Weather Service alert is in effect</b> for the Fiddletown point; <b>Caltrans&#8217; 5:26 PM reports list no restrictions on SR-49, SR-88, SR-124, or SR-104</b> — no closures, no chain control; and the <b>CHP Stockton board, updated 5:26 PM, holds zero incidents</b> — the no-injury hit-and-run on SR-49 at Miller Way that the midday board carried has cleared (see the Safety Wire). <b>Tonight:</b> mostly cloudy, low near 47. <b>Friday:</b> mostly cloudy, high near 63 — Black Friday, foothills style, with wine-country sales across Plymouth and Shenandoah, Sutter Creek Plaid Friday, and Jackson&#8217;s Christmas Delights opening (see The Week Ahead). No weather event ran today; there are no storm totals to close out. The next weather to watch is Sunday, when rain is likely with showers and thunderstorms (see the Outlook panel). <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>CHP board — empty at the evening read; the midday hit-and-run has cleared.</b> The Stockton center&#8217;s board, updated <b>5:26 PM</b>, holds <b>zero incidents</b> — none in the beat, none anywhere on the board, and <b>no chain control</b>. The one incident the midday board carried — a hit-and-run with no injuries on northbound SR-49 at Miller Way, logged 11:16 AM — is gone from the board tonight.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 5:26 PM PT, Nov 26</p></div>
    <div class="item"><p><b>Roads — clear on every route the paper checks, into the night.</b> Caltrans&#8217; evening reports (5:26 PM) list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four.</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, as of 5:26 PM PT, Nov 26</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a cloudy night, a mostly cloudy Friday.</b> At the evening check (5:26 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Tonight:</b> mostly cloudy, low near 47. <b>Friday:</b> mostly cloudy, high near 63. No weather event ran today, so there are no totals to close out; the weekend turn is Sunday — rain likely, then showers and thunderstorms (see the Outlook panel in the Lead).</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 5:26 PM PT, Nov 26</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the evening check.</b> No fire incident in the beat appears on the CHP board this evening — the board is empty. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 5:26 PM PT, Nov 26</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>Thanksgiving midday —.*?</p>','<p><b>Thanksgiving evening — the day&#8217;s list ran this morning, and the tables have the rest of it.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>three in-beat events spanned today</b>, listed below as cards, verified against the feed this evening and unchanged from the morning and midday editions. All three were morning affairs and have wrapped: the <b>Jackson Turkey Trot at Lake Tabeaud, 8:00 AM</b>, the <b>Sutter Creek Turkey Trot at Cribbs Field, 9:00 AM</b>, and <b>Preschool Story Time at the Jackson Library, 10:30 AM</b>. Nothing else in the database remains on today&#8217;s calendar. <b>Tomorrow, Fri Nov 27 — Black Friday, foothills style, in the database:</b> wine-country Black Friday sales across Plymouth and Shenandoah (Bella Grace&#8217;s Black Friday at the Cave, 9:00 AM; Avio and Black Snake at 11:00 AM; Iron Hub, Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Golden Leaves), Sutter Creek Plaid Friday, and Jackson&#8217;s Christmas Delights opening with the Festival of Trees at 6:00 PM (see The Week Ahead).</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

html=sub(r'<div class="item"><p><b>Today, Thu Nov 26 — Thanksgiving Day, the rest of the day:</b>.*?</div>','<div class="item"><p><b>Today, Thu Nov 26 — Thanksgiving Day, evening:</b> the morning&#8217;s three database events have run — <b>Jackson Turkey Trot</b>, Lake Tabeaud, 8:00 AM · <b>Sutter Creek Turkey Trot</b>, Cribbs Field, 9:00 AM · <b>Preschool Story Time</b>, Jackson Library, 10:30 AM — and nothing further is on today&#8217;s calendar in the database; see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>',html,flags=re.S,label="week today")

html=sub(r'The desk re-checked the home crossing at midday — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; midday web report lists no restrictions on SR-88, and the CHP CAD board \(updated 12:30 PM today\) holds no SR-88 incident \(see the Safety Wire\)\.','The desk re-checked the home crossing this evening — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 5:26 PM web report lists no restrictions on SR-88, and the CHP CAD board (updated 5:26 PM today) holds zero incidents at all (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 12:30 PM today\)','(CHP CAD + Caltrans, 5:26 PM today)',html,label="carson row")

html=sub(r'<p><b>Viewing note \(honest\):</b>.*?</p>','<p><b>Viewing note (honest, evening check):</b> tonight is <b>mostly cloudy, low near 47</b> — so expect the Moon and Saturn to show through gaps rather than hold steady, and faint stars and meteors are a poor bet. If a gap opens around 8 PM, Saturn high in the south is the prize, with the bright gibbous Moon low in the east. Dress warm; the ridge cools fast after sunset.</p>',html,flags=re.S,label="star note")

open(p,"w",encoding="utf-8").write(html)
print("evening build ok",len(html))
