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

html=sub(r'<meta name="fg-edition" content="2026-11-27-morning">','<meta name="fg-edition" content="2026-11-27-midday">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Midday Edition — published 12:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> 🛍️ Black Friday in the foothills: mostly cloudy, 63°; tonight mostly cloudy, low 50°; roads clear — no restrictions on SR-49, SR-88, SR-124 or SR-104; the CHP Stockton board is empty at midday; no NWS alert (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Black Friday at midday — the wine sales are in full swing, the CHP board has gone quiet, and tonight Jackson lights its Christmas Delights <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Midday on Black Friday, and the foothills are shopping: <b>Bella Grace&#8217;s 20-year Black Friday sale at the Plymouth wine cave (9:00 AM)</b> is under way, the 11:00 AM sales at <b>Avio, Black Snake, and Iron Hub</b> have opened, all-day sales run at <b>Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Amador Cellars, and Golden Leaves</b>, and <b>Sutter Creek&#8217;s Plaid Friday</b> fills its Main Street. The roads have gone quieter than the morning found them: the <b>CHP Stockton board, updated 12:30 PM, is empty</b> — the morning&#8217;s SR-26 traffic hazard west of the beat has cleared — <b>Caltrans lists no restrictions on SR-49, SR-88, SR-124, or SR-104</b>, and <b>no National Weather Service alert is in effect</b> for the Fiddletown point. <b>This afternoon:</b> mostly cloudy, high near 63, easing to around 58. <b>Tonight:</b> mostly cloudy, low near 50 — and the season turns on in Jackson: <b>Christmas Delights opens with the Festival of Trees at 6:00 PM</b>, the Tunnel of Lights lit through Dec 31, and free skating on Main Street; Volcano&#8217;s <b>On The Farce Day of Christmas</b> plays at 7:30 PM. Sunday still brings the rain — likely, with showers and thunderstorms possible (see the Outlook panel). <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>CHP board — empty at the midday read.</b> The Stockton center&#8217;s board, updated <b>12:30 PM</b> and re-read after its 12:31 PM refresh, holds <b>no incidents at all</b> — nothing in the beat, nothing anywhere on the board, and <b>no chain control</b> listed. The morning&#8217;s one incident, a traffic hazard on SR-26 at Jack Tone Rd west of the beat, has cleared.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 12:30–12:32 PM PT, Nov 27</p></div>
    <div class="item"><p><b>Roads — still clear on every route the paper checks.</b> Caltrans&#8217; midday reports list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four, the same clear picture as this morning. Black Friday traffic around Plymouth, Shenandoah, and Jackson&#8217;s Main Street tonight is the only slowdown to expect.</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, checked 12:30 PM PT, Nov 27</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a cloudy afternoon, rain still due Sunday.</b> At the midday check (12:30 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>This afternoon:</b> mostly cloudy, high near 63, temperatures falling to around 58. <b>Tonight:</b> mostly cloudy, low near 50. Saturday stays mostly cloudy; a slight chance of rain late Saturday night turns to rain likely Sunday, with showers and thunderstorms possible (see the Outlook panel in the Lead).</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 12:30 PM PT, Nov 27</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the midday check.</b> No fire incident in the beat appears on the CHP board at midday. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 12:30–12:32 PM PT, Nov 27</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>Black Friday, foothills style — wine first, malls never\.</b>.*?</p>','<p><b>Black Friday at midday — the sales are open, and tonight Jackson lights up.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>sixteen in-beat events span today</b>, listed below as cards, verified against the feed at midday and unchanged from the morning edition. The morning openings have happened — <b>Bella Grace&#8217;s sale at the cave, 9:00 AM</b>, then <b>Avio, Black Snake, and Iron Hub at 11:00 AM</b> — and the all-day sales (Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Amador Cellars, Golden Leaves) and <b>Sutter Creek Plaid Friday</b> run on into the afternoon. <b>Still to come tonight:</b> Jackson&#8217;s <b>Christmas Delights</b> — the <b>Festival of Trees at 6:00 PM</b>, the Tunnel of Lights lit through Dec 31, free skating at the South Pole Skating Rink, and the Great Christmas Light Show driving tour — plus <b>On The Farce Day of Christmas</b> at Volcano&#8217;s Cobblestone Theatre, <b>7:30 PM</b>. Tomorrow, Sat Nov 28: Baked in Amador&#8217;s Sourdough Breakfast, Knight Foundry Open Day, and Lacy J Dalton&#8217;s Country Christmas in Sutter Creek (see The Week Ahead).</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

html=sub(r'<div class="item"><p><b>Today, Fri Nov 27 — Black Friday:</b>.*?</div>','<div class="item"><p><b>Today, Fri Nov 27 — Black Friday, the rest of the day:</b> the winery sales run on this afternoon — <b>Bella Grace</b> at the cave, <b>Avio</b>, <b>Black Snake</b>, and <b>Iron Hub</b>, plus all-day sales at Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Amador Cellars, and Golden Leaves · <b>Sutter Creek Plaid Friday</b>, all day · tonight <b>Christmas Delights</b> opens on Main Street, Jackson, with the <b>Festival of Trees at 6:00 PM</b>, the Tunnel of Lights, the South Pole Skating Rink, and the Great Christmas Light Show · <b>On The Farce Day of Christmas</b>, Cobblestone Theatre, Volcano, 7:30 PM — see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 27</p></div>',html,flags=re.S,label="week today")

html=sub(r'The desk re-checked the home crossing this morning — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; morning web report lists no restrictions on SR-88, and the CHP CAD board \(updated 6:04 AM today\) holds one incident — on SR-26, not SR-88 \(see the Safety Wire\)\.','The desk re-checked the home crossing at midday — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; midday web report lists no restrictions on SR-88, and the CHP CAD board (updated 12:30 PM today) is empty (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 6:04 AM today\)','(CHP CAD + Caltrans, 12:30 PM today)',html,label="carson row")

open(p,"w",encoding="utf-8").write(html)
print("midday build ok",len(html))
