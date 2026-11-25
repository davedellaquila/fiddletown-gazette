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

html=sub(r'<meta name="fg-edition" content="2026-11-25-morning">','<meta name="fg-edition" content="2026-11-25-midday">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Midday Edition — published 12:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> ☀️ Sunny today, high 63°; mostly cloudy tonight, low 46°; roads clear — no restrictions on SR-49, SR-88, SR-124 or SR-104; no NWS alert (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Midday, the day before Thanksgiving — roads still clear on every route the paper checks, and tonight&#8217;s Friendsgivings in Plymouth and Placerville are the day&#8217;s remaining business <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Midday finds the foothills sunny and quiet on the day before Thanksgiving. The morning&#8217;s clear picture holds at every midday check: <b>no National Weather Service alert is in effect</b> for the Fiddletown point; the <b>CHP Stockton board (updated 12:30 PM) holds two incidents, neither in the beat and no chain control anywhere</b>; and <b>Caltrans&#8217; 12:30 PM reports list no restrictions on SR-49, SR-88, SR-124, or SR-104</b>. The afternoon runs on a short clock: <b>Preschool Story Time at the Plymouth Library is at 1:00 PM</b>, and the <b>Baked in Amador Thanksgiving preorder pickup closes at 3:00 PM</b> in Volcano — its final day. Tonight is the double Friendsgiving from the database: <b>dinner at the Plymouth Hotel Kitchen &amp; Bar at 6:30 PM</b> and the <b>Friendsgiving Show at The Green Room Social Club in Placerville at 7:00 PM</b>, with <b>Amador All Stars</b> at Feist Wines in Drytown and <b>Luka&#8217;s box-dinner pickup</b> in Jackson. The forecast has eased a touch since morning: <b>this afternoon stays sunny, high near 63</b> with temperatures falling to about 56; <b>tonight turns mostly cloudy, low near 46</b>; and <b>Thanksgiving Day now reads partly sunny, high near 62</b> for the turkey trots in Jackson and Sutter Creek. <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>Roads — still clear on every route the paper checks.</b> Caltrans&#8217; midday reports (12:30 PM) list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four, the same clear picture as this morning.</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, as of 12:30 PM PT, Nov 25</p></div>
    <div class="item"><p><b>CHP board — nothing in the beat at midday.</b> The Stockton center&#8217;s board, updated <b>12:30 PM</b>, holds two incidents: a <b>no-injury collision on I-205 E at the W Grant Line Rd off-ramp (Tracy), logged 11:39 AM</b>, and the standing <b>assist-with-construction on SR-4 at Stanley Rd</b> in the Stockton area. Nothing names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Volcano, or Pine Grove, and there is <b>no chain control</b> on the board.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 12:30 PM PT, Nov 25</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a sunny afternoon, a cloudier night than the morning called for.</b> At the midday check (12:30 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>This afternoon:</b> sunny, high near 63, temperatures falling to about 56. <b>Tonight:</b> mostly cloudy, low near 46 — cloudier and a touch warmer than the morning&#8217;s partly-cloudy, 44 call. <b>Thanksgiving Day:</b> partly sunny, high near 62. The next weather to watch is days out — rain is expected Sunday (see the Outlook panel in the Lead).</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 12:30 PM PT, Nov 25</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the midday check.</b> No fire incident in the beat appears on the CHP board at midday. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 12:30 PM PT, Nov 25</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

# Today intro midday
s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>The night before Thanksgiving, and the foothills are out\.</b>.*?</p>','<p><b>Midday, the day before Thanksgiving — the afternoon is short and the evening is full.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>six in-beat events span today</b>, listed below as cards, verified against the feed at midday and unchanged from the morning edition. Still ahead: <b>Preschool Story Time at the Plymouth Library at 1:00 PM</b> and the <b>final Baked in Amador preorder pickup in Volcano, which closes at 3:00 PM</b>. Tonight brings the double Friendsgiving — <b>dinner at the Plymouth Hotel</b> (6:30 PM) and the <b>Friendsgiving Show in Placerville</b> (7:00 PM) — with <b>Amador All Stars</b> at Feist Wines in Drytown and <b>Luka&#8217;s box-dinner pickup</b> in Jackson. <b>Tomorrow, Thu Nov 26 — Thanksgiving Day, in the database:</b> the Jackson Turkey Trot at Lake Tabeaud, 8:00 AM; the Sutter Creek Turkey Trot at Cribbs Field, 9:00 AM; and Preschool Story Time at the Jackson Library, 10:30 AM (see The Week Ahead).</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

html=sub(r'<div class="item"><p><b>Today, Wed Nov 25 — the night before:</b>.*?</div>','<div class="item"><p><b>Today, Wed Nov 25 — the rest of the day:</b> <b>Preschool Story Time</b>, Plymouth Library, 1:00 PM, free · <b>Baked in Amador preorder pickup</b> finishes at 3:00 PM, Volcano · <b>Luka&#8217;s Thanksgiving box-dinner pickup</b>, by appointment, Jackson · <b>Amador All Stars</b> at Feist Wines, Drytown · <b>Friendsgiving 2026 — Plymouth Hotel Kitchen &amp; Bar</b>, 6:30 PM · <b>Friendsgiving Show</b>, The Green Room Social Club, Placerville, 7:00 PM — see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 25</p></div>',html,flags=re.S,label="week today")

# Sierra passes intro midday
html=sub(r'The desk re-checked the home crossing this morning — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 6:02 AM web report lists no restrictions on SR-88, and the CHP CAD board \(read 6:01 AM today\) holds no SR-88 incident \(see the Safety Wire\)\.','The desk re-checked the home crossing at midday — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 12:30 PM web report lists no restrictions on SR-88, and the CHP CAD board (updated 12:30 PM today) holds no SR-88 incident (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 12:31 PM today\)','(CHP CAD + Caltrans, 12:30 PM today)',html,label="carson row")

open(p,"w",encoding="utf-8").write(html)
print("midday build ok",len(html))
