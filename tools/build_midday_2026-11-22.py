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
    new,n=re.subn(pattern,repl,html,count=1,flags=flags)
    if n==0: raise SystemExit(f"pattern not found: {label or pattern[:90]}")
    return new

html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Midday Edition — published 12:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
# masthead evening? Midday keep daytime closeup (morning already set) - leave
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> 🌧️ Chance of rain this afternoon, high 50°; patchy fog tonight, low 37°; SR-88/49/124 no restrictions; no NWS alert (NWS / Caltrans / CHP) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Midday on a matinee Sunday — the Volcano farce and Drytown music are still ahead, and the Thanksgiving order books close this afternoon <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Midday finds the foothills in the middle of a rainy Sunday: the <b>railbikes in Ione</b> and <b>Drytown Cellars&#8217; club weekend</b> run into the afternoon, <b>The Sun Followers are due at Driven Cellars in Plymouth at 12:30 PM</b>, the <b>Volcano farce plays its Sunday matinee at 2:00 PM</b>, and <b>Darin Sexton and Highway 49 close the day at Feist Wines in Drytown at 4:00 PM</b>. <b>No National Weather Service alert is in effect</b> for the Fiddletown point; this afternoon carries a <b>chance of rain (about 53%), high near 50 falling to about 46</b>, then <b>patchy fog tonight, low near 37</b>. <b>SR-88, SR-49, and SR-124 all report no restrictions</b> at midday, and the CHP board holds <b>no incident in the beat</b>. Two clocks run out this afternoon: <b>Baked in Amador&#8217;s Thanksgiving preorders close at 3:00 PM</b> and <b>Luka&#8217;s box-dinner orders close today</b> (see Around Town). <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>Weather — no alert in effect; rain chance this afternoon, patchy fog tonight.</b> At the midday check (12:30 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>This afternoon:</b> a chance of rain before 4 PM, then a chance of rain and patchy fog, cloudy, high near 50 with temperatures falling to about 46, chance of precipitation about 53%. <b>Tonight:</b> patchy fog and a slight chance of rain before 11 PM, then partly cloudy, low near 37 (rising to about 39 overnight), chance of precipitation about 20%. <b>Monday</b> brings patchy frost early, then mostly sunny, high near 54, before rain likely returns Tuesday night and Wednesday — plan Thanksgiving travel with that wet stretch in mind.</p><p class="meta">Sources: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 12:30 PM PT, Nov 22</p></div>
    <div class="item"><p><b>Roads — SR-88, SR-49, and SR-124 all report no restrictions at midday.</b> Caltrans&#8217; midday reports (12:30 PM) list <b>no traffic restrictions</b> on SR-88 in the Central California / Sierra Nevada area, and none on SR-49 or SR-124. No closure or chain control is listed on any of the three.</p><p class="meta">Sources: Caltrans road reports for SR-88, SR-49 &amp; SR-124, checked 12:30 PM PT, Nov 22</p></div>
    <div class="item"><p><b>Roads — the CHP board holds no incident in the beat.</b> At the midday read (12:30 PM) the Stockton center&#8217;s board held <b>one incident</b> — an animal hazard on <b>I-5 southbound at the Eighth Street off-ramp in Stockton</b> (logged 12:10 PM), outside the beat. No chain-control log is listed. Nothing names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Pioneer, Volcano, Pine Grove, SR-49, SR-88, or SR-124.</p><p class="meta">Sources: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 12:30 PM PT, Nov 22</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the midday check.</b> No fire incident in the beat appears on the CHP board at midday. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Sources: CHP CAD Traffic — Stockton center, read 12:30 PM PT, Nov 22</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

# Today intro midday
s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>A matinee Sunday — seven listings from the events database\.</b>.*?</p>','<p><b>Midday on a matinee Sunday — the afternoon slate is still ahead.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>seven in-beat events span today</b>, listed below as cards, verified against the feed at midday. Still running: Amador Rail Explorers in Ione (to 5:30 PM) and Drytown Cellars&#8217; club weekend day two (to 5:00 PM). Starting now: The Sun Followers at Driven Cellars, Plymouth, 12:30 PM. Ahead: the Volcano farce matinee at 2:00 PM and Darin Sexton and Highway 49 at Feist Wines, Drytown, 4:00–7:00 PM. The desk&#8217;s midday discovery sweep (Amador Wine / Best of Amador) found nothing in the beat for today that is not already in the database. <b>Tomorrow, Mon Nov 23, in the database:</b> Preschool Story Time at the Ione Branch Library, 10:00 AM, free, and the Jackson City Council at Jackson City Hall, 6:30 PM, free (see The Week Ahead). The Thanksgiving order deadlines closing today — Baked in Amador at 3:00 PM and Luka&#8217;s box dinners — are order material and run in Around Town, not in this listing.</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

# Week Ahead today item
html=sub(r'<div class="item"><p><b>Today, Sun Nov 22 — a matinee Sunday:</b>.*?</div>','<div class="item"><p><b>Today, Sun Nov 22 — the rest of the day:</b> <b>Amador Rail Explorers</b>, Ione, to 5:30 PM · <b>Drytown Cellars club weekend</b> day two, to 5:00 PM · <b>The Sun Followers at Driven Cellars</b>, Plymouth, 12:30 PM · <b>On The Farce Day of Christmas</b> matinee, Volcano, 2:00–4:00 PM · <b>Darin Sexton and Highway 49</b>, Feist Wines, Drytown, 4:00–7:00 PM (see Today in the Foothills for the cards; the morning&#8217;s museum and craft gathering have run).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>',html,flags=re.S,label="week today")

weather='''
    <p><b>A rainy Sunday afternoon, a foggy night, and one fair day before the next wet stretch.</b> <b>This afternoon:</b> a chance of rain, cloudy, high near 50, with temperatures falling to about 46; chance of precipitation about 53%. <b>Tonight:</b> patchy fog and a slight chance of rain before 11 PM, then partly cloudy, low near 37. <b>Monday:</b> patchy frost early, then mostly sunny, high near 54. Then rain likely <b>Tuesday night and Wednesday</b>, easing for <b>Thanksgiving Day</b> (partly sunny, high near 61 on the morning panel; see the five-day panel above for the latest numbers). The five-day panel above carries the numbers, and every day in it opens its own hour-by-hour page.</p>
    <p class="meta">Source: National Weather Service, Sacramento (Fiddletown point) · Forecast checked 12:30 PM PT, Nov 22</p>
  '''
html=replace_block(html,"weather",weather)

# Sierra passes intro midday re-verify
html=sub(r'The desk re-verified the home crossing this morning — <b>SR-88&#8217;s Carson Pass is open with no restrictions</b> \(Caltrans, 6:01 AM today:','The desk re-verified the home crossing at midday — <b>SR-88&#8217;s Carson Pass is open with no restrictions</b> (Caltrans, 12:30 PM today:',html,label="passes")

# Around Town midday note: update the Sunday item
html=sub(r'<div class="item"><p><b>Sunday in the foothills:</b> a matinee day —.*?</div>','<div class="item"><p><b>Sunday at midday in the foothills:</b> the afternoon slate is the Volcano farce at 2:00 PM and Darin Sexton and Highway 49 at Feist Wines at 4:00 PM, with Driven Cellars&#8217; music from 12:30 PM — and the Baked in Amador (3:00 PM) and Luka&#8217;s Thanksgiving order deadlines closing today (see Around Town).</p><p class="meta">Gazette note · Nov 22</p></div>',html,flags=re.S,label="around sunday")
html=sub(r'<div class="item"><p>Thanksgiving is Thu Nov 26 — and the order deadlines cluster this Sunday, Nov 22:.*?</div>','<div class="item"><p>Thanksgiving is Thu Nov 26 — and the order deadlines cluster today, Sun Nov 22: Luka&#8217;s boxes (above) and Baked in Amador&#8217;s preorders both close today.</p><p class="meta">Gazette note · Nov 22</p></div>',html,flags=re.S,label="around deadlines")

open(p,"w",encoding="utf-8").write(html)
print("midday build ok",len(html))
