#!/usr/bin/env python3
import re, json
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

html=sub(r'<meta name="fg-edition" content="2026-11-26-evening">','<meta name="fg-edition" content="2026-11-27-morning">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Morning Edition — published 6:00 AM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition name")
html=sub(r'<!-- EDITION:DATE -->.*?<!-- /EDITION:DATE -->','<!-- EDITION:DATE --> Friday, November 27, 2026 <!-- /EDITION:DATE -->',html,flags=re.S,label="edition date")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> 🛍️ Black Friday in the foothills: partly sunny, 63°; tonight mostly cloudy, low 50°; roads clear — no restrictions on SR-49, SR-88, SR-124 or SR-104; one CHP traffic hazard on SR-26 at Jack Tone Rd; no NWS alert (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Black Friday, foothills style — the wine caves open early, Jackson lights its Christmas Delights tonight, and the roads are clear on every route the paper checks <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> The day after Thanksgiving starts clean in the foothills: at the morning checks, <b>no National Weather Service alert is in effect</b> for the Fiddletown point; <b>Caltrans&#8217; morning reports list no restrictions on SR-49, SR-88, SR-124, or SR-104</b> — no closures and <b>no chain control</b>; and the <b>CHP Stockton board, read at 6:04 AM, holds a single incident</b> — a traffic hazard on SR-26 at Jack Tone Rd, west of the beat (see the Safety Wire). The day&#8217;s events, built only from the events database, are Black Friday in full: <b>Bella Grace&#8217;s 20-year Black Friday sale opens at the Plymouth wine cave at 9:00 AM</b>, a dozen more winery sales follow across Plymouth and Shenandoah, <b>Sutter Creek goes Plaid Friday</b> all day, and tonight <b>Jackson&#8217;s Christmas Delights opens with the Festival of Trees at 6:00 PM</b>, the Tunnel of Lights lit through Dec 31, and free skating on Main Street. <b>Today:</b> partly sunny, high near 63. <b>Tonight:</b> mostly cloudy, low near 50. The weekend&#8217;s turn is real: rain likely Sunday, with showers and thunderstorms possible (see the Outlook panel below and the Weather box) — shop today, batten down Sunday. <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

zen='''
      <p style="font-size:19px;font-style:italic">&#8220;When you reach the top of the mountain, keep climbing.&#8221;</p>
      <p>The morning after a feast, in plain words: a summit is a resting place, not a finish line. Whatever you topped this year — a harvest, a table, a hard season — the next rise is already in view, and the legs remember the way.</p>
      <p class="meta">— Zen proverb · From the Zen Master — Sayings archive</p>
    '''
html=replace_block(html,"zen-today",zen)

safety='''
    <div class="item"><p><b>Roads — clear on every route the paper checks, on Black Friday morning.</b> Caltrans&#8217; morning reports list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four. Black Friday winery and Main Street traffic is the only slowdown to expect, around Plymouth and Shenandoah from 9:00 AM and on Jackson&#8217;s Main Street tonight.</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, checked 6:02 AM PT, Nov 27</p></div>
    <div class="item"><p><b>CHP board — one incident at the morning read, west of the beat.</b> The Stockton center&#8217;s board, updated <b>6:04 AM</b>, holds <b>one incident</b>: a <b>traffic hazard on <a href="https://maps.apple.com/?ll=38.000726,-121.149456&amp;q=SR-26%20%2F%20Jack%20Tone%20Rd">SR-26 at Jack Tone Rd</a></b> (Incident 0035, reported 5:46 AM, westbound SR-26 just west of Jack Tone Rd; the board posts no details). That is the SR-26 corridor west toward Stockton — <b>nothing in Fiddletown, Plymouth, Jackson, or Sutter Creek, and nothing on SR-49, SR-88, SR-124, or SR-104</b>.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 6:01–6:04 AM PT, Nov 27</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a fair Black Friday, rain by Sunday.</b> At the morning check (6:00 AM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Today:</b> partly sunny, high near 63. <b>Tonight:</b> mostly cloudy, low near 50. Saturday stays fair; then a slight chance of rain late Saturday night turns to <b>rain likely Sunday, with showers and thunderstorms possible</b> (see the Outlook panel in the Lead).</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 6:00 AM PT, Nov 27</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the morning check.</b> No fire incident in the beat appears on the CHP board this morning. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 6:01–6:04 AM PT, Nov 27</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

ev={e['slug']:e for e in json.load(open('/tmp/events.json'))}
def esc(t):
    return (t or '').replace('&','&amp;').replace('’','&#8217;').replace('‘','&#8216;').replace('“','&#8220;').replace('”','&#8221;').replace('—','&#8217;—').replace('–','&#8211;')
def card(time,slug):
    e=ev[slug]; name=esc(e['name']); venue=esc(e['location']); host=esc(e.get('host_org') or 'host not named in the record')
    desc=esc((e.get('short_description') or e.get('description') or '').strip())
    if len(desc)>260: desc=desc[:257].rsplit(' ',1)[0]+'…'
    mq=venue.replace(' ','+').replace(',','%2C').replace('&','%26')
    return (f'<article class="ev"><div class="ev-time">{time}</div><div class="ev-body"><h3>{name}</h3>'
      f'<p class="ev-venue">📍 <a href="https://maps.apple.com/?q={mq}">{venue}</a></p><p>{desc}</p>'
      f'<p class="meta" style="margin-top:5px">Source: <a href="https://events.fiddletowngazette.com/?event={slug}#/event/{slug}">events database</a> published feed · Checked Nov 27 · Host: {host}</p></div></article>')

today_intro='<p><b>Black Friday, foothills style — wine first, malls never.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>seventeen in-beat events span today</b>, listed below as cards, verified against the feed this morning, Christmas-season events first within each time. The wine country opens the day: <b>Bella Grace&#8217;s 20-year Black Friday sale at the Plymouth wine cave, 9:00 AM</b>, then Avio, Black Snake, and Iron Hub at 11:00 AM and all-day sales at Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Amador Cellars, and Golden Leaves. <b>Sutter Creek runs Plaid Friday all day.</b> Tonight the season turns on: <b>Jackson&#8217;s Christmas Delights</b> — the <b>Festival of Trees at 6:00 PM</b>, the <b>Tunnel of Lights</b> lit through Dec 31, free skating at the <b>South Pole Skating Rink</b>, and the <b>Great Christmas Light Show</b> driving tour — plus <b>On The Farce Day of Christmas</b> at Volcano&#8217;s Cobblestone Theatre, 7:30 PM. <b>Tomorrow, Sat Nov 28:</b> Baked in Amador&#8217;s Sourdough Breakfast, Knight Foundry Open Day, and Lacy J Dalton&#8217;s Country Christmas in Sutter Creek (see The Week Ahead).</p>\n'
cards=today_intro
order=[("9:00 AM","black-friday-at-the-cave-2026"),
("11:00 AM","black-friday-wine-sale-avio-vineyards-2026"),
("11:00 AM","black-snake-winery-black-friday-weekend-2026"),
("6:00 PM","festival-of-trees-jackson-2026"),
("7:30 PM","on-the-farce-day-of-christmas-2026-11-27"),
("All day","sutter-creek-plaid-friday-2026-11-27"),
("All day","christmas-delights-jackson-2026"),
("All day","tunnel-of-lights-jackson-2026"),
("All day","south-pole-skating-rink-jackson-2026-11-27"),
("All day","great-christmas-light-show-jackson-2026"),
("All day","black-friday-at-iron-hub-2026"),
("All day","black-friday-casino-mine-ranch-2026"),
("All day","dobra-zemlja-my-precious-black-friday-2026"),
("All day","terre-rouge-easton-black-friday-weekend-2026"),
("All day","black-friday-amador-cellars-2026"),
("All day","golden-leaves-thanksgiving-weekend-2026")]
for t,s in order: cards+="\n"+card(t,s)
cards+='\n  <p class="meta" style="margin-top:8px"><a href="https://events.fiddletowngazette.com/">From the Gold Country events database →</a></p>\n  '
html=replace_block(html,"today-events",cards)

week = '''
    <div class="item"><p><b>Today, Fri Nov 27 — Black Friday:</b> <b>Black Friday at the Cave</b>, Bella Grace Vineyards, Plymouth, 9:00 AM · <b>Avio</b>, <b>Black Snake</b>, and <b>Iron Hub</b> Black Friday sales from 11:00 AM · <b>Sutter Creek Plaid Friday</b>, all day · <b>Christmas Delights</b> opens on Main Street, Jackson, with the <b>Festival of Trees</b> at 6:00 PM, the <b>Tunnel of Lights</b>, the <b>South Pole Skating Rink</b>, and the <b>Great Christmas Light Show</b> · <b>On The Farce Day of Christmas</b>, Cobblestone Theatre, Volcano, 7:30 PM — see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 27</p></div>
    <div class="item"><p><b>Sat Nov 28 — the fullest day of the week:</b> <b>Baked in Amador&#8217;s Saturday Sourdough Breakfast</b>, Volcano, 8:00 AM · <b>Knight Foundry Open Day</b>, Sutter Creek, 10:00 AM · <b>Soup Cook Off at Gibson&#8217;s Roadhouse</b>, Pioneer, 12:00 PM · <b>Tiny Tim&#8217;s Christmas Carol</b>, Baker Street West, Jackson, 2:00 PM · <b>Geoffrey Miller and the Rockin&#8217; Rousers</b>, Fiddletown Community Center, 6:00 PM · <b>Cash Blast at Acorn Ridge Casino</b>, Plymouth, 6:00 PM · <b>Lacy J Dalton&#8217;s Country Christmas Show</b>, Sutter Creek Theatre, 7:00 PM · <b>On The Farce Day of Christmas</b>, Volcano, 7:30 PM · <b>Karaoke @ the Ridge</b>, Acorn Ridge Casino, from 8:00 PM.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 27</p></div>
    <div class="item"><p><b>Sun Nov 29:</b> <b>On The Farce Day of Christmas — Sunday Matinee</b>, Cobblestone Theatre, Volcano, 2:00 PM. Further out the same morning, the driving club DWA! runs its <b>Morning Motors</b> gathering in Santa Cruz at 8:00 AM — a coastal run, listed here because DWA! is a standing source. A quiet Sunday in the foothills otherwise — and a wet one, on the forecast.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 27</p></div>
    <div class="item"><p><b>Tue Dec 1 — Giving Tuesday in Fiddletown:</b> <b>Coffee &amp; Conversations</b>, Amador County Chamber of Commerce, Jackson, 8:00 AM · <b>Giving Tuesday Porch Donations</b> with hot cocoa on the Fiddletown Community Center porch, 1:30 PM · <b>Tapas Tuesday at Krissie Vineyards</b>, Plymouth, 3:00 PM · <b>FNRW at Amador Giving Tuesday</b>, Catherine Drexel Hall, Martell, 4:00 PM.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 27</p></div>
    <div class="item"><p><b>Wed Dec 2:</b> <b>Amador All Stars</b> at Feist Wines, Drytown. <b>Thu Dec 3:</b> the <b>Fiddletown Community Center&#8217;s Annual Meeting</b>, 5:30 PM, and the <b>Amador City Holiday Market</b> opens (Dec 3–6).</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 27</p></div>
  '''
html=replace_block(html,"week-events",week)

history='''
    <div class="hist-hl"><p>⭐ <b>From our own hills — an honest empty well in the Mother Lode today; California carries the date, and carries it hard.</b> The desk dug back to 1848 through Gold Country timelines, Amador County histories, and Mother Lode records and found <b>no verified Fiddletown, Amador County, or Mother Lode event dated November 27</b>. The desk will not stretch a date to fill the panel. The nearest true layer is California itself — and November 27 is one of the heaviest dates in the state&#8217;s modern history, told straight below, as this feature does hard history.</p></div>
    <p><b>1978 — Moscone and Milk are assassinated in San Francisco (Nov 27)</b> — former Supervisor Dan White shoots Mayor George Moscone and Supervisor Harvey Milk — one of the first openly gay elected officials in the United States — inside San Francisco City Hall. Forty-eight years on, the date still stops Californians cold.</p>
    <p><b>1940 — Bruce Lee is born in San Francisco (Nov 27)</b> — the actor and martial artist is born at Jackson Street Hospital in San Francisco&#8217;s Chinatown, while his father, a Cantonese opera star, is touring America.</p>
    <p><b>1895 — Alfred Nobel signs the will creating the Nobel Prizes (Nov 27)</b> — Nobel, inventor of dynamite — a substance every hard-rock miner in these hills knew firsthand — leaves his fortune to fund prizes for those who &#8220;have conferred the greatest benefit to humankind.&#8221;</p>
    <p><b>1924 — The first Macy&#8217;s Thanksgiving Day Parade (Nov 27)</b> — Macy&#8217;s employees march through New York with floats, bands, and animals borrowed from the Central Park Zoo; the giant balloons arrive a few years later. A fitting item for the morning after Thanksgiving.</p>
    <p><b>1942 — The French fleet scuttles itself at Toulon (Nov 27)</b> — as German forces move to seize it, the Vichy French navy sinks more than 70 of its own ships and submarines rather than let them fall into Nazi hands. The same day, in Seattle, Jimi Hendrix is born.</p>
    <p><b>1868 — The Washita River attack (Nov 27)</b> — Lt. Col. George Armstrong Custer&#8217;s 7th Cavalry attacks Black Kettle&#8217;s Cheyenne village on the Washita River, in present-day Oklahoma, killing Black Kettle and dozens of Cheyenne men, women, and children — a hard chapter of the Plains wars, named plainly.</p>
    <p><b>1095 — Pope Urban II calls the First Crusade (Nov 27)</b> — speaking at the Council of Clermont in France, Urban II urges Western Christians to march east to aid Byzantium and take Jerusalem — the speech that launches the Crusades.</p>
    <p class="meta" style="margin-top:8px">Sources: November 27 timelines — HISTORY (This Day in History, Nov 27) · USA Today, &#8220;Today in history, November 27&#8221; · Wikipedia (November 27) · on-this-day timelines (Moscone &amp; Milk · Bruce Lee · Nobel&#8217;s will · Macy&#8217;s parade · Toulon · Washita · Clermont) · Checked Nov 27, 2026 · Staged in history/2026-11-27.md</p>
  '''
html=sub(r'<h2>📜 This Day in History — Nov 26</h2>','<h2>📜 This Day in History — Nov 27</h2>',html,label="history h2")
html=replace_block(html,"history",history)

marker='''
    <p class="meta" style="margin-bottom:6px">FROM MARKER BUDDY&#8217;S GOLD COUNTRY CATALOG · No. 12 · Fri Nov 27, 2026</p>
    <h3 style="margin:4px 0 6px">Marguerite Mine &#8220;Quartz Rock&#8221; — Other organization marker, Auburn</h3>
    <p><b>What the marker says:</b></p>
    <blockquote style="margin:6px 0 10px;padding:8px 12px;border-left:3px solid var(--gold)">&#8220;MARGUERITE MINE &#8216;QUARTZ ROCK&#8217;<br>The quartz rock on site here at the Auburn depot came from &#8216;The Marquerite (sic) Mine&#8217; of Auburn<br>Donated by<br>Don Robinson<br>Don Robinson Sand &amp; Gravel&#8221;</blockquote>
    <p><b>Where:</b> <a href="https://maps.apple.com/?ll=38.902133,-121.065833&amp;q=Marguerite%20Mine%20Quartz%20Rock">Transcontinental Railroad Plaza, at or near 601 Lincoln Way, Auburn</a> — reached from Lincoln Way, in front of the Chinese Coolie statue at the Auburn depot.</p>
    <p>A boulder of quartz — the rock that carried the Mother Lode&#8217;s gold — hauled from Auburn&#8217;s Marguerite Mine and set at the old depot as a monument you can touch: the mine&#8217;s own ore-body, standing in for every quartz vein the Placer County hills ever hid. The plaque&#8217;s spelling (&#8220;Marquerite&#8221;) is the mine&#8217;s as recorded, sic and all. The feature runs text-only today — the desk holds no lawful photograph of the marker it has inspected, and it does not borrow HMdb contributors&#8217; pictures.</p>
    <p class="meta">Supplied daily by 🪧 Marker Buddy from his Gold Country marker catalog · <a href="https://davedellaquila.github.io/buddy-system/marker-buddy/markers/marguerite-mine-quartz-rock.html">The marker&#8217;s own page</a> · <a href="https://www.hmdb.org/m.asp?m=81625">Marker record at HMdb</a> · A new marker every morning</p>
  '''
html=replace_block(html,"marker-of-the-day",marker)

star='''
    <figure class="skyfig"><img src="sky/2026-11-27.png" alt="Chart of tonight&#8217;s visible planets over Fiddletown: Saturn about 52 degrees up in the south at 8 PM, the waning gibbous Moon rising about 8:09 PM in the east-northeast, Jupiter and Mars rising late evening, Venus before dawn"><figcaption>Tonight over Fiddletown — the Moon and visible planets, sunset to sunrise. Higher on the chart = higher in the sky = easier to see. (Chart: the Gazette sky desk, computed for Fiddletown.)</figcaption></figure>
    <p><b>Tonight&#8217;s chart (~8 PM, facing south):</b> Saturn is the evening planet — about 52° up in the south at 8 PM, up all evening. The waning gibbous Moon rises about 8:09 PM in the east-northeast and climbs all night. Pegasus rides high overhead, Cassiopeia climbs in the northeast, and Taurus waits in the east for the Moon to join it.</p>
    <p>🌖 <b>Moon:</b> waning gibbous — about 85% lit, shrinking toward last quarter. It rises about 8:09 PM and is up the rest of the night.</p>
    <p><b>Planets up:</b> Saturn takes the evening — high in the south all night (sets about 2:15 AM). Jupiter rises about 10:50 PM and Mars about 11:10 PM, both brilliant before dawn. Venus is a pre-dawn object only (it rises about 3:45 AM Saturday). Mercury is not an evening target tonight.</p>
    <p><b>Notable — the Leonids wind down:</b> the Leonid meteors fade after their Nov 17–18 peak — a few fast streaks still possible in the dark hours before moonrise, though the bright Moon will wash out all but the brightest once it is up. The Taurids&#8217; slow, bright fireballs remain possible on any clear stretch.</p>
    <p><b>Viewing note (honest):</b> tonight is <b>mostly cloudy, low near 50</b> — so expect Saturn and the rising Moon to show through gaps rather than hold steady, and faint stars and meteors are a poor bet. The best window may be early: Saturn high in the south from dark, and the gibbous Moon clearing the ridge about 8:09 PM. Dress warm; the ridge cools fast after sunset.</p>
    <p class="meta" style="margin-top:8px">Sources: Gazette sky desk (skyfield, computed for Fiddletown) · International Meteor Organization / EarthSky / NASA (Leonids) · NWS Sacramento (conditions) · Checked Nov 27, 2026 · Staged in sky/2026-11-27.md</p>
  '''
html=replace_block(html,"star-chart",star)

almanac='''
    <p>Sunrise 6:57 AM · Sunset 4:43 PM — a 9-hour-46-minute day, and shrinking.</p>
    <p>Moon: waning gibbous — about 85% lit, shrinking toward last quarter. It rises about 8:09 PM and is up the rest of the night.</p>
    <p>📅 Black Friday in the foothills. Today, Fri Nov 27, the foothills run on PST (standard time) until March. Amador County schools are out Wed–Fri for the holiday break — today is the last day of it. Ahead on the civic clock: Small Business Saturday tomorrow, Sat Nov 28, and Giving Tuesday on Tue Dec 1, with the Fiddletown Community Center&#8217;s porch donations at 1:30 PM.</p>
    <p>Day 331 of 2026 · 34 days left in the year</p>
  '''
html=replace_block(html,"almanac",almanac)

album='''
    <!-- ALBUM:BEGIN — Music Buddy's daily pick, printed verbatim (artist, album, year, write-up, Apple Music links) from Music Buddy's Album of the Day; refreshed in the Morning edition, carried forward at Midday and Evening. See PUBLISHING.md. -->
    <div class="item"><p><b>Journey — <a href="https://music.apple.com/us/album/escape-2022-remaster/1640102583"><i>Escape</i></a> (1981)</b></p>
    <p>A Friday record from Dave&#8217;s classic-rock shelf — Journey at their arena peak, with &#8220;Don&#8217;t Stop Believin&#8217;,&#8221; &#8220;Who&#8217;s Crying Now&#8221; and &#8220;Open Arms,&#8221; Steve Perry soaring over Neal Schon&#8217;s guitar and Jonathan Cain&#8217;s piano. Big melodies and bigger choruses, made to fill a room.</p>
    <p class="meta">Music Buddy's pick for Friday, November 27, 2026 — the same Album of the Day that goes to Dave by email each morning. <a href="https://davedellaquila.github.io/buddy-system/music-buddy/">Music Buddy's page</a></p></div>
    <!-- ALBUM:END -->
    <p class="meta" style="margin-top:8px">Every pick so far stands in <a href="album-archive.html">The Album of the Day Archive</a>.</p>
  '''
html=replace_block(html,"album-of-the-day",album)
try:
    s,e=block_span(html,"album-archive-list")
    seg=html[s:e]
    if "Escape" not in seg:
        entry='''<div class="item"><p><b>Fri Nov 27, 2026 — Journey — <i>Escape</i> (1981)</b> · <a href="https://music.apple.com/us/album/escape-2022-remaster/1640102583">Apple Music</a></p></div>\n    '''
        html=html[:s]+"\n    "+entry+html[s:]
        print("album archive prepended")
except SystemExit:
    print("album-archive-list not on front page (archive page separate) — skipped")

html=sub(r'The desk re-checked the home crossing this evening — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 5:26 PM web report lists no restrictions on SR-88, and the CHP CAD board \(updated 5:26 PM today\) holds zero incidents at all \(see the Safety Wire\)\.','The desk re-checked the home crossing this morning — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; morning web report lists no restrictions on SR-88, and the CHP CAD board (updated 6:04 AM today) holds one incident — on SR-26, not SR-88 (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 5:26 PM today\)','(CHP CAD + Caltrans, 6:04 AM today)',html,label="carson row")

html=sub(r'<div class="item"><p><b>Today, Thu Nov 26 — Thanksgiving Day, a quiet Thursday on the circuit\.</b>.*?</div>','<div class="item"><p><b>Today, Fri Nov 27 — Black Friday, a quiet Friday on the circuit.</b> The standing meets are Saturday affairs, so no meet runs today; the next round is <b>Sat Nov 28</b> (below). No judged shows today — the season has wound down.</p></div>',html,flags=re.S,label="car shows today")

html=sub(r'<p><b>Today’s joke:</b> What do you call a turkey the day after Thanksgiving\? …Lucky\.</p>','<p><b>Today’s joke:</b> What do you call a Black Friday sale at a winery? …A grape deal.</p>',html,label="joke")
html=sub(r'<p><b>Yesterday&#8217;s riddle: What has keys but can&#8217;t open a single lock\? — Answer: A piano\.</b></p>','<p><b>Yesterday&#8217;s riddle: What has many teeth but cannot bite? — Answer: A comb.</b></p>',html,label="riddle answer")
html=sub(r'<p style="margin-top:6px"><b>Today’s riddle:</b> What has many teeth but cannot bite\?</p>','<p style="margin-top:6px"><b>Today’s riddle:</b> What gets wetter the more it dries?</p>',html,label="riddle today")

open(p,"w",encoding="utf-8").write(html)
print("morning build ok",len(html))
