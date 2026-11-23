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

html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Evening Edition — published 5:30 PM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> ⛓️ SR-88 chain control R2, Peddler Vista to Silver Lake; patchy fog tonight, low 37°; SR-49/124 no restrictions; no NWS alert (CHP / NWS / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Evening on a rainy Sunday — chain control is up on SR-88 above Peddler Vista, and one last set of music plays in Drytown <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Evening closes a rainy Sunday in the foothills. The day&#8217;s last event in the database is still playing: <b>Darin Sexton and Highway 49 at Feist Wines in Drytown, 4:00–7:00 PM</b>; the railbikes, the Drytown Cellars club weekend, the Volcano matinee, and the Driven Cellars music have all run their course. The safety picture changed late in the day: at <b>5:26 PM the CHP board logged R2 chain control on SR-88 from Peddler Vista to Silver Lake</b> — chains required on all vehicles except four-wheel/all-wheel drive with snow tires on all four wheels. <b>No National Weather Service alert is in effect</b>; tonight brings <b>patchy fog and a slight chance of rain before 11 PM, then partly cloudy, low near 37</b>. <b>SR-49 and SR-124 report no restrictions.</b> The Thanksgiving order books that closed today — Baked in Amador at 3:00 PM and Luka&#8217;s box dinners — move to pickup this week (see Around Town). <b>Tomorrow, Mon Nov 23:</b> Preschool Story Time in Ione at 10:00 AM and the Jackson City Council at 6:30 PM, both from the events database. <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

safety='''
    <div class="item"><p><b>Chain control — R2 on SR-88, Peddler Vista to Silver Lake (new this evening).</b> The CHP Stockton board, updated 5:29 PM, logs <b>chain control at 5:26 PM for Amador / Calaveras Counties: SR-88 R2 from Peddler Vista to Silver Lake</b>. R2 means chains are required on all vehicles except four-wheel/all-wheel-drive vehicles with snow tires on all four wheels. Drivers headed up SR-88 tonight should carry chains and expect the control point on the upper highway; the foothill towns themselves are not under control. Caltrans&#8217; web report at 5:27 PM still listed no restrictions on SR-88 — the CHP log, posted as that report was issued, is the later word and governs here.</p><p class="meta">Sources: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 5:29 PM PT, Nov 22 · Caltrans SR-88 report, 5:27 PM PT, Nov 22</p></div>
    <div class="item"><p><b>Weather — no alert in effect; the rain ends, patchy fog tonight.</b> At the evening check (5:30 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Tonight:</b> patchy fog and a slight chance of rain before 11 PM, then partly cloudy, low near 37 (rising to about 39 overnight), chance of precipitation about 20%. <b>Monday</b> brings patchy frost early, then mostly sunny, high near 54, before rain likely returns Tuesday night and Wednesday — plan Thanksgiving travel with that wet stretch in mind.</p><p class="meta">Sources: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 5:30 PM PT, Nov 22</p></div>
    <div class="item"><p><b>Roads — SR-49 and SR-124 report no restrictions; no foothill incident on the board.</b> Caltrans&#8217; evening reports (5:27 PM) list <b>no traffic restrictions</b> on SR-49 or SR-124. Apart from the SR-88 chain-control log above, the CHP board at 5:29 PM held three Stockton-area incidents, all outside the beat. Nothing names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Pioneer, Volcano, or Pine Grove.</p><p class="meta">Sources: Caltrans road reports for SR-49 &amp; SR-124, checked 5:27 PM PT, Nov 22 · <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 5:29 PM PT, Nov 22</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the evening check.</b> No fire incident in the beat appears on the CHP board this evening. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Sources: CHP CAD Traffic — Stockton center, read 5:29 PM PT, Nov 22</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

# Today intro evening
s,e=block_span(html,"today-events"); blk=html[s:e]
blk2,n=re.subn(r'<p><b>Midday on a matinee Sunday — the afternoon slate is still ahead\.</b>.*?</p>','<p><b>Evening on a matinee Sunday — one set still playing.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>seven in-beat events spanned today</b>, listed below as cards, verified against the feed this evening. Still playing: <b>Darin Sexton and Highway 49 at Feist Wines, Drytown, to 7:00 PM</b>. Run their course today: Amador Rail Explorers in Ione (to 5:30 PM), Drytown Cellars&#8217; club weekend day two (to 5:00 PM), the Amador County Museum, the Fall Craft Gathering at La Mesa, The Sun Followers at Driven Cellars, and the Volcano farce matinee. The desk&#8217;s evening discovery sweep found nothing in the beat for today that is not already in the database; one Plymouth find for next weekend is relayed to Events Buddy in the edition report. <b>Tomorrow, Mon Nov 23, in the database:</b> Preschool Story Time at the Ione Branch Library, 10:00 AM, free, and the Jackson City Council at Jackson City Hall, 6:30 PM, free (see The Week Ahead). The Thanksgiving order deadlines that closed today — Baked in Amador at 3:00 PM and Luka&#8217;s box dinners — are order material and run in Around Town, not in this listing.</p>',blk,count=1,flags=re.S)
if n==0: raise SystemExit("today intro not found")
html=html[:s]+blk2+html[e:]

html=sub(r'<div class="item"><p><b>Today, Sun Nov 22 — the rest of the day:</b>.*?</div>','<div class="item"><p><b>Today, Sun Nov 22 — the evening:</b> <b>Darin Sexton and Highway 49</b>, Feist Wines, Drytown, plays to 7:00 PM — the day&#8217;s last listed event (see Today in the Foothills for the cards; the rest of today&#8217;s slate has run).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>',html,flags=re.S,label="week today")

weather='''
    <p><b>The rain is done for the day; a foggy, frosty night, then one fair day before the next wet stretch.</b> <b>Tonight:</b> patchy fog and a slight chance of rain before 11 PM, then partly cloudy, low near 37. <b>Monday:</b> patchy frost early, then mostly sunny, high near 54. Then rain likely <b>Tuesday night and Wednesday</b>, easing for <b>Thanksgiving Day</b> (partly sunny, high near 61 on the evening panel; see the five-day panel above for the latest numbers). Up the hill, SR-88 carries R2 chain control tonight from Peddler Vista to Silver Lake (see the Safety Wire). No rainfall total for today is published in the sources the desk reads, so none is printed. The five-day panel above carries the numbers, and every day in it opens its own hour-by-hour page.</p>
    <p class="meta">Source: National Weather Service, Sacramento (Fiddletown point) · Forecast checked 5:30 PM PT, Nov 22</p>
  '''
html=replace_block(html,"weather",weather)

# Sierra passes intro + Carson row -> chain control
html=sub(r'The desk re-verified the home crossing at midday — <b>SR-88&#8217;s Carson Pass is open with no restrictions</b> \(Caltrans, 12:30 PM today: no traffic restrictions reported on SR-88\)\.','The desk re-checked the home crossing this evening — <b>SR-88 now carries R2 chain control from Peddler Vista to Silver Lake</b> (CHP CAD log, 5:26 PM today), on the approach to Carson Pass; Caltrans&#8217; 5:27 PM web report still listed no restrictions, and the later CHP log governs.',html,label="passes intro")
html=sub(r'<tr><td><b>Carson Pass</b> · 8,573 ft</td><td>SR-88</td><td><b>Open</b> — no restrictions reported \(Caltrans, 5:26 PM today\); no closure listed</td></tr>','<tr><td><b>Carson Pass</b> · 8,573 ft</td><td>SR-88</td><td><b>Open — R2 chain control</b> Peddler Vista to Silver Lake (CHP CAD, 5:26 PM today); no closure listed</td></tr>',html,label="carson row")

# Star chart viewing note refresh (evening actuals)
html=sub(r'<p><b>Viewing note \(honest, morning check\):</b>.*?</p>','<p><b>Viewing note (honest, evening check):</b> the rain chance ends before 11 PM and the sky turns partly cloudy, but <b>patchy fog</b> is in the forecast for tonight and the low falls to about 37 with frost possible toward morning. The honest word: <b>if the fog stays off your ridge, Saturn and the bright Moon are tonight&#8217;s show</b> — check the sky before you dress for it, and dress warm if you stay out.</p>',html,flags=re.S,label="star note")

# Around Town evening updates
html=sub(r'<div class="item"><p><b>Sunday at midday in the foothills:</b>.*?</div>','<div class="item"><p><b>Sunday evening in the foothills:</b> the day&#8217;s last listed music — Darin Sexton and Highway 49 at Feist Wines, Drytown — plays to 7:00 PM, and the Thanksgiving order books that closed today move to pickup this week (Baked in Amador from Tue Nov 24; Luka&#8217;s by appointment Wed Nov 25).</p><p class="meta">Gazette note · Nov 22</p></div>',html,flags=re.S,label="around sunday")
html=sub(r'<div class="item"><p>Thanksgiving is Thu Nov 26 — and the order deadlines cluster today, Sun Nov 22:.*?</div>','<div class="item"><p>Thanksgiving is Thu Nov 26 — the Sun Nov 22 order deadlines (Luka&#8217;s boxes and Baked in Amador&#8217;s preorders) have now closed; pickups run this week as listed in The Week Ahead.</p><p class="meta">Gazette note · Nov 22</p></div>',html,flags=re.S,label="around deadlines")

open(p,"w",encoding="utf-8").write(html)
print("evening build ok",len(html))
