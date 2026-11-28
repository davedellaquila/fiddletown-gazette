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

html=sub(r'<meta name="fg-edition" content="2026-11-27-midday">','<meta name="fg-edition" content="2026-11-27-evening">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Evening Edition — published 5:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> 🎄 Black Friday evening in the foothills: mostly cloudy, low 50°; Saturday mostly cloudy, 65°; roads clear — no restrictions on SR-49, SR-88, SR-124 or SR-104; the CHP board&#8217;s 3 incidents are all in Stockton, none in the beat; no NWS alert (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Black Friday evening — Jackson&#8217;s Christmas Delights lights up Main Street tonight, the foothill roads stay clear, and the CHP board&#8217;s only incidents are down in Stockton <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Evening on Black Friday, and the day&#8217;s shopping gives way to the season&#8217;s first big night. The wine-country sales have run their day — <b>Bella Grace at the cave</b>, <b>Avio</b>, <b>Black Snake</b>, <b>Iron Hub</b>, and the all-day sales at <b>Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Amador Cellars, and Golden Leaves</b> — and <b>Sutter Creek&#8217;s Plaid Friday</b> winds down. <b>Tonight in Jackson: Christmas Delights opens</b> — the <b>Festival of Trees at 6:00 PM</b> in the Krabbenhoft Building, the <b>Tunnel of Lights</b> lit from tonight through Dec 31, free skating at the <b>South Pole Skating Rink</b>, and the <b>Great Christmas Light Show</b> driving tour — plus <b>On The Farce Day of Christmas</b> at Volcano&#8217;s Cobblestone Theatre, <b>7:30 PM</b>, and a free <b>Community Observatory viewing night</b> in Placerville, 7:30–9:30 PM. The safety picture stays calm for the foothills: <b>no National Weather Service alert is in effect</b>; <b>Caltrans&#8217; 5:26 PM reports list no restrictions on SR-49, SR-88, SR-124, or SR-104</b>; and the <b>CHP Stockton board (updated 5:26 PM) holds three incidents, all in Stockton</b> — none in the beat (see the Safety Wire). <b>Tonight:</b> mostly cloudy, low near 50. <b>Saturday:</b> mostly cloudy, high near 65 — and the fullest day of the week (see The Week Ahead). No weather event ran today; there are no storm totals to close out. The next weather to watch is Sunday, when rain is likely with showers and thunderstorms (see the Outlook panel). <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>CHP board — three incidents at the evening read, all in Stockton; none in the beat.</b> The Stockton center&#8217;s board, updated <b>5:26 PM</b>, holds <b>three incidents</b>, every one down in Stockton: a <b>traffic hazard</b> on <a href="https://maps.apple.com/?ll=38.02114,-121.31499&amp;q=I5%20S%20%2F%20Hammer%20Ln%20Ofr">I5 S / Hammer Ln Ofr</a> (logged 5:03 PM); a <b>collision with an ambulance en route</b> at <a href="https://maps.apple.com/?ll=37.95347,-121.28246&amp;q=E%20Charter%20Way%20%2F%20E%20Main%20St">E Charter Way / E Main St</a> (logged 4:57 PM); and a <b>no-injury collision</b> at <a href="https://maps.apple.com/?ll=37.93568,-121.23793&amp;q=W%20Frontage%20Rd%20%2F%20E%20Mariposa%20Rd">W Frontage Rd / E Mariposa Rd</a> (logged 4:30 PM). <b>Nothing in the foothills beat, and no chain control</b> anywhere on the board.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 5:26 PM PT, Nov 27</p></div>
    <div class="item"><p><b>Roads — clear on every route the paper checks, into the night.</b> Caltrans&#8217; evening reports (5:26 PM) list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four. Expect Christmas Delights crowds on Jackson&#8217;s Main Street tonight and Black Friday traffic around Plymouth and Shenandoah to be the only slowdowns.</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, as of 5:26 PM PT, Nov 27</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a cloudy night, a mostly cloudy Saturday, rain Sunday.</b> At the evening check (5:26 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Tonight:</b> mostly cloudy, low near 50, rising to around 52 overnight. <b>Saturday:</b> mostly cloudy, high near 65, with a slight chance of rain late Saturday night. <b>Sunday</b> brings the change: rain likely, then showers and thunderstorms (see the Outlook panel in the Lead). No weather event ran today, so there are no totals to close out.</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 5:26 PM PT, Nov 27</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the evening check.</b> No fire incident in the beat appears on the CHP board this evening — its three incidents are all Stockton traffic matters. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 5:26 PM PT, Nov 27</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>Black Friday at midday —.*?</p>','<p><b>Black Friday evening — the sales have run, and tonight Jackson lights up.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>sixteen in-beat events span today</b>, listed below as cards, verified against the feed this evening and unchanged from the morning and midday editions. The daytime sales have wrapped or are wrapping — <b>Bella Grace&#8217;s sale at the cave</b>, <b>Avio</b>, <b>Black Snake</b>, <b>Iron Hub</b>, the all-day sales at Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Amador Cellars, and Golden Leaves, and <b>Sutter Creek Plaid Friday</b>. <b>Still to come tonight:</b> Jackson&#8217;s <b>Christmas Delights</b> — the <b>Festival of Trees, 6:00–9:00 PM</b>, the Tunnel of Lights lit through Dec 31, free skating at the South Pole Skating Rink, and the Great Christmas Light Show driving tour — <b>On The Farce Day of Christmas</b> at Volcano&#8217;s Cobblestone Theatre, <b>7:30 PM</b>, and the <b>Community Observatory&#8217;s free viewing night</b> in Placerville, <b>7:30–9:30 PM</b>. Tomorrow, Sat Nov 28: Baked in Amador&#8217;s Sourdough Breakfast, Knight Foundry Open Day, and Lacy J Dalton&#8217;s Country Christmas in Sutter Creek (see The Week Ahead).</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

html=sub(r'<div class="item"><p><b>Today, Fri Nov 27 — Black Friday, the rest of the day:</b>.*?</div>','<div class="item"><p><b>Today, Fri Nov 27 — Black Friday, tonight:</b> the winery sales and <b>Sutter Creek Plaid Friday</b> have run their day · tonight <b>Christmas Delights</b> opens on Main Street, Jackson, with the <b>Festival of Trees at 6:00 PM</b>, the Tunnel of Lights, the South Pole Skating Rink, and the Great Christmas Light Show · <b>On The Farce Day of Christmas</b>, Cobblestone Theatre, Volcano, 7:30 PM · <b>Community Observatory viewing night</b>, Placerville, 7:30 PM — see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 27</p></div>',html,flags=re.S,label="week today")

html=sub(r'The desk re-checked the home crossing at midday — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; midday web report lists no restrictions on SR-88, and the CHP CAD board \(updated 12:30 PM today\) is empty \(see the Safety Wire\)\.','The desk re-checked the home crossing this evening — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 5:26 PM web report lists no restrictions on SR-88, and the CHP CAD board (updated 5:26 PM today) holds three incidents, all in Stockton — none on SR-88 (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 12:30 PM today\)','(CHP CAD + Caltrans, 5:26 PM today)',html,label="carson row")

# Freshness: retire the Gibson's Roadhouse Community Wire item (Thanksgiving seats + Nov 20 dinner, both past; item also past its 3-day life)
html=sub(r'<div class="item"><p><b>Gibson&#8217;s Roadhouse — Thanksgiving seats were going fast\.</b>.*?</div>','',html,flags=re.S,label="gibson wire retire")
# Freshness: retire the Swingle Thanksgiving turkey order card from Around Town (Thanksgiving was Nov 26)
html=sub(r'<div class="item"><p><b>Thanksgiving brined turkeys — Swingle Meat Co\., Jackson\.</b>.*?</div>\s*','',html,flags=re.S,label="swingle retire")

html=sub(r'<p><b>Viewing note \(honest\):</b>.*?</p>','<p><b>Viewing note (honest, evening check):</b> tonight is <b>mostly cloudy, low near 50</b> — so expect Saturn and the rising Moon to show through gaps rather than hold steady, and faint stars and meteors are a poor bet. If a gap opens around 8 PM, Saturn high in the south is the prize, with the bright gibbous Moon clearing the ridge about 8:09 PM. Dress warm; the ridge cools fast after sunset.</p>',html,flags=re.S,label="star note")

open(p,"w",encoding="utf-8").write(html)
print("evening build ok",len(html))
