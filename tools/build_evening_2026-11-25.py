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

html=sub(r'<meta name="fg-edition" content="2026-11-25-midday">','<meta name="fg-edition" content="2026-11-25-evening">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Evening Edition — published 5:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> ☁️ Mostly cloudy tonight, low 46° rising to 48°; Thanksgiving Day haze early, then partly sunny, 62°; roads clear — no restrictions on SR-49, SR-88, SR-124 or SR-104; no NWS alert (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Evening, the night before Thanksgiving — the roads home are clear on every route the paper checks, and the double Friendsgiving is tonight: dinner in Plymouth at 6:30, the show in Placerville at 7 <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Evening settles over the foothills on the night before Thanksgiving, and the day closes as clear as it ran. At the evening checks, <b>no National Weather Service alert is in effect</b> for the Fiddletown point; <b>Caltrans&#8217; 5:26 PM reports list no restrictions on SR-49, SR-88, SR-124, or SR-104</b> — no closures and <b>no chain control</b>; and the <b>CHP Stockton board (updated 5:26 PM) holds two incidents, neither in the beat</b> — the nearest is a no-injury collision on SR-26 near San Andreas, south of the paper&#8217;s country (see the Safety Wire). The day&#8217;s business is done: <b>Preschool Story Time</b> read at the Plymouth Library at 1:00 PM, and <b>Baked in Amador&#8217;s Thanksgiving preorder pickup closed at 3:00 PM</b> in Volcano — its final day. What remains is tonight, and it is a good one: <b>Friendsgiving dinner at the Plymouth Hotel Kitchen &amp; Bar at 6:30 PM</b> and the <b>Friendsgiving Show at The Green Room Social Club in Placerville at 7:00 PM</b>, with <b>Amador All Stars</b> at Feist Wines in Drytown and <b>Luka&#8217;s box-dinner pickup</b> in Jackson. <b>Tonight:</b> mostly cloudy, low near 46, rising to about 48 overnight. <b>Thanksgiving Day:</b> haze before 9 AM, then partly sunny, high near 62 — a fair morning for the turkey trots in Jackson (8:00 AM) and Sutter Creek (9:00 AM). <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>Roads — clear on every route the paper checks, into the holiday.</b> Caltrans&#8217; evening reports (5:26 PM) list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four. Anyone driving home for Thanksgiving tonight, or out early for the turkey trots, starts with a clean board.</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, as of 5:26 PM PT, Nov 25</p></div>
    <div class="item"><p><b>CHP board — nothing in the beat at the evening read.</b> The Stockton center&#8217;s board, updated <b>5:26 PM</b>, holds two incidents: a <b>no-injury collision on SR-26 at Dirt Rd (San Andreas area), logged 2:27 PM</b> — south of the paper&#8217;s beat, noted for anyone driving SR-26 this evening — and the standing <b>assist-with-construction on SR-4 at Stanley Rd</b> in the Stockton area. Nothing names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Volcano, or Pine Grove, and there is <b>no chain control</b> on the board.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 5:27 PM PT, Nov 25</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a cloudy night, a fair Thanksgiving.</b> At the evening check (5:26 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Tonight:</b> mostly cloudy, low near 46, with temperatures rising to about 48 overnight. <b>Thanksgiving Day:</b> haze before 9 AM, then partly sunny, high near 62. No weather event ran today; there are no storm totals to close out. The next weather to watch is days out — a slight chance of rain arrives late Saturday night (see the Outlook panel in the Lead).</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 5:26 PM PT, Nov 25</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the evening check.</b> No fire incident in the beat appears on the CHP board this evening. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 5:27 PM PT, Nov 25</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>Midday, the day before Thanksgiving.*?</p>','<p><b>Evening — the day is done except for the best part.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>six in-beat events span today</b>, listed below as cards, verified against the feed this evening and unchanged from the morning and midday editions. Done for the day: <b>Preschool Story Time at the Plymouth Library</b> (1:00 PM) and the <b>final Baked in Amador preorder pickup in Volcano, which closed at 3:00 PM</b>. Still tonight: the double Friendsgiving — <b>dinner at the Plymouth Hotel Kitchen &amp; Bar at 6:30 PM</b> and the <b>Friendsgiving Show at The Green Room Social Club in Placerville at 7:00 PM</b> — with <b>Amador All Stars</b> at Feist Wines in Drytown and <b>Luka&#8217;s box-dinner pickup</b> in Jackson. <b>Tomorrow, Thu Nov 26 — Thanksgiving Day, in the database:</b> the Jackson Turkey Trot at Lake Tabeaud, 8:00 AM; the Sutter Creek Turkey Trot at Cribbs Field, 9:00 AM; and Preschool Story Time at the Jackson Library, 10:30 AM (see The Week Ahead).</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

html=sub(r'<div class="item"><p><b>Today, Wed Nov 25 — the rest of the day:</b>.*?</div>','<div class="item"><p><b>Today, Wed Nov 25 — tonight:</b> <b>Friendsgiving 2026 — Plymouth Hotel Kitchen &amp; Bar</b>, 6:30 PM · <b>Friendsgiving Show</b>, The Green Room Social Club, Placerville, 7:00 PM · <b>Amador All Stars</b> at Feist Wines, Drytown · <b>Luka&#8217;s Thanksgiving box-dinner pickup</b>, by appointment, Jackson — the day&#8217;s earlier listings (Preschool Story Time, 1:00 PM; the final Baked in Amador pickup, which closed at 3:00 PM) are done — see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 25</p></div>',html,flags=re.S,label="week today")

html=sub(r'The desk re-checked the home crossing at midday — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 12:30 PM web report lists no restrictions on SR-88, and the CHP CAD board \(updated 12:30 PM today\) holds no SR-88 incident \(see the Safety Wire\)\.','The desk re-checked the home crossing this evening — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 5:26 PM web report lists no restrictions on SR-88, and the CHP CAD board (updated 5:26 PM today) holds no SR-88 incident (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 12:30 PM today\)','(CHP CAD + Caltrans, 5:26 PM today)',html,label="carson row")

html=sub(r'<p><b>Viewing note \(honest\):</b>.*?</p>','<p><b>Viewing note (honest, evening check):</b> tonight has turned <b>mostly cloudy, low near 46</b> — cloudier than the morning&#8217;s partly-cloudy call, so expect the Moon and Saturn to show through gaps rather than hold steady, and faint stars and meteors are a poor bet. If a gap opens around 8 PM, Saturn high in the south is the prize, with the bright gibbous Moon in the east. Dress warm; the ridge cools fast after sunset.</p>',html,flags=re.S,label="star note")

open(p,"w",encoding="utf-8").write(html)
print("evening build ok",len(html))
