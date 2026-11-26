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

html=sub(r'<meta name="fg-edition" content="2026-11-25-evening">','<meta name="fg-edition" content="2026-11-26-morning">',html,label="fg-edition")
html=sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->','<!-- EDITION:NAME --> Morning Edition — published 6:00 AM PT <!-- /EDITION:NAME -->',html,flags=re.S,label="edition name")
html=sub(r'<!-- EDITION:DATE -->.*?<!-- /EDITION:DATE -->','<!-- EDITION:DATE --> Thursday, November 26, 2026 <!-- /EDITION:DATE -->',html,flags=re.S,label="edition date")
html=sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->','<!-- WEATHER:BUG --> 🦃 Thanksgiving Day: partly sunny, 63°; tonight mostly cloudy, low 47°; roads clear — no restrictions on SR-49, SR-88, SR-124 or SR-104, and the CHP board is empty; no NWS alert (NWS / CHP / Caltrans) <!-- /WEATHER:BUG -->',html,flags=re.S,label="bug")
html=sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->','<!-- LEAD:HEADLINE --> Thanksgiving morning in the foothills — the roads are clear on every route the paper checks, the CHP board is empty, and the day belongs to two turkey trots and the tables after them <!-- /LEAD:HEADLINE -->',html,flags=re.S,label="headline")
html=sub(r'<p><!-- LEAD:BODY -->.*?</p>','<p><!-- LEAD:BODY --> Happy Thanksgiving from the Gazette. The holiday starts clean: at the morning checks, <b>no National Weather Service alert is in effect</b> for the Fiddletown point; <b>Caltrans&#8217; morning reports list no restrictions on SR-49, SR-88, SR-124, or SR-104</b> — no closures and <b>no chain control</b>; and the <b>CHP Stockton board, read at 6:01 AM, holds no incidents at all</b> (see the Safety Wire). The day&#8217;s events, built only from the events database, are a Thanksgiving pair and a story time: the <b>Jackson Turkey Trot at Lake Tabeaud at 8:00 AM</b> and the <b>Sutter Creek Turkey Trot at Cribbs Field at 9:00 AM</b> — both Thanksgiving-morning runs — and <b>Preschool Story Time at the Jackson Library, 10:30 AM</b>. <b>Today:</b> partly sunny, high near 63, with temperatures easing to around 57 in the afternoon — a fair morning for a trot around the lake. <b>Tonight:</b> mostly cloudy, low near 47. The next weather to watch is the weekend&#8217;s turn: a slight chance of rain late Saturday night, then rain likely Sunday (see the Outlook panel below and the Weather box). <!-- /LEAD:BODY --></p>',html,flags=re.S,label="lead body")

# Zen — the briefing's pick for Nov 26 (un-tagged entry in zen-quotes-used.md)
zen='''
      <p style="font-size:19px;font-style:italic">&#8220;A fool sees himself as another, but a wise man sees others as himself.&#8221;</p>
      <p>Thanksgiving Day, in plain words: the people across the table are not strangers to work out — they are mirrors. See yourself in them, and the day gets easier and kinder at once.</p>
      <p class="meta">— Dōgen · From the Zen Master — Sayings archive</p>
    '''
html=replace_block(html,"zen-today",zen)

safety='''
    <div class="item"><p><b>Roads — clear on every route the paper checks, on Thanksgiving morning.</b> Caltrans&#8217; morning reports list <b>no traffic restrictions</b> on <b>SR-49, SR-88, SR-124, or SR-104</b> — no closures, no one-way control, and <b>no chain control</b> anywhere on the four. Turkey-trot traffic is the only slowdown to expect, around Lake Tabeaud (Jackson, 8:00 AM) and Cribbs Field (Sutter Creek, 9:00 AM).</p><p class="meta">Source: Caltrans road reports for SR-49, SR-88, SR-124 &amp; SR-104, checked 6:02 AM PT, Nov 26</p></div>
    <div class="item"><p><b>CHP board — empty at the morning read.</b> The Stockton center&#8217;s board, updated <b>6:01 AM</b>, holds <b>no incidents at all</b> — nothing in the beat, nothing on the foothill routes, and <b>no chain control</b> on the board. A clean board to start the holiday.</p><p class="meta">Source: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 6:01 AM PT, Nov 26</p></div>
    <div class="item"><p><b>Weather — no alert in effect; a fair Thanksgiving, a cloudier night.</b> At the morning check (6:00 AM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Today:</b> partly sunny, high near 63. <b>Tonight:</b> mostly cloudy, low near 47. The weekend turns: a slight chance of rain late Saturday night, then rain likely Sunday with showers and thunderstorms possible (see the Outlook panel in the Lead).</p><p class="meta">Source: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 6:00 AM PT, Nov 26</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the morning check.</b> No fire incident in the beat appears on the CHP board this morning. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Source: CHP CAD Traffic — Stockton center, read 6:01 AM PT, Nov 26</p></div>
  '''
html=replace_block(html,"safety-wire",safety)

def card(time,slug,name,venue,maps_q,desc,host):
    return (f'<article class="ev"><div class="ev-time">{time}</div><div class="ev-body"><h3>{name}</h3>'
      f'<p class="ev-venue">📍 <a href="https://maps.apple.com/?q={maps_q}">{venue}</a></p><p>{desc}</p>'
      f'<p class="meta" style="margin-top:5px">Source: <a href="https://events.fiddletowngazette.com/?event={slug}#/event/{slug}">events database</a> published feed · Checked Nov 26 · Host: {host}</p></div></article>')

today_intro='<p><b>Thanksgiving morning — a short, good list.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>three in-beat events span today</b>, listed below as cards, verified against the feed this morning. The day opens on foot: the <b>Jackson Turkey Trot at Lake Tabeaud, 8:00 AM</b>, and the <b>Sutter Creek Turkey Trot at Cribbs Field, 9:00 AM</b> — then <b>Preschool Story Time at the Jackson Library, 10:30 AM</b>. After that, the holiday is yours. <b>Tomorrow, Fri Nov 27 — Black Friday, foothills style, in the database:</b> wine-country Black Friday sales across Plymouth and Shenandoah (Bella Grace&#8217;s Black Friday at the Cave, 9:00 AM; Avio and Black Snake at 11:00 AM; Iron Hub, Casino Mine Ranch, Dobra Zemlja, Terre Rouge &amp; Easton, Golden Leaves), Sutter Creek Plaid Friday, and Jackson&#8217;s Christmas Delights opening with the Festival of Trees at 6:00 PM (see The Week Ahead).</p>\n'
cards = today_intro
cards += card("8:00–9:30 AM","jackson-turkey-trot-2026-11-26","Jackson Turkey Trot","Lake Tabeaud, Jackson","Lake+Tabeaud%2C+Jackson%2C+CA","Thanksgiving morning Turkey Trot at Lake Tabeaud — donations welcomed.","Jackson Turkey Trot")
cards += "\n" + card("9:00 AM","sutter-creek-turkey-trot-2026","Sutter Creek Turkey Trot","Cribbs Field, Sutter Creek, CA","Cribbs+Field%2C+Sutter+Creek%2C+CA","Start Thanksgiving with a trot: the second annual Sutter Creek Turkey Trot runs Thanksgiving morning at Cribbs Field. The 9:00 AM start is as listed on public event calendars; the organizer hadn&#8217;t published registration details on the pages found, so check local listings before race day.","Sutter Creek Turkey Trot (host not named in the record)")
cards += "\n" + card("10:30 AM","preschool-story-time-jackson-2026-11-26","Preschool Story Time — Jackson Library","Jackson Library, Jackson","Jackson+Library%2C+Jackson%2C+CA","Preschool Story Time at the Jackson Library — free.","Amador County Library")
cards += '\n  <p class="meta" style="margin-top:8px"><a href="https://events.fiddletowngazette.com/">From the Gold Country events database →</a></p>\n  '
html=replace_block(html,"today-events",cards)

week = '''
    <div class="item"><p><b>Today, Thu Nov 26 — Thanksgiving Day:</b> <b>Jackson Turkey Trot</b>, Lake Tabeaud, 8:00 AM · <b>Sutter Creek Turkey Trot</b>, Cribbs Field, 9:00 AM · <b>Preschool Story Time</b>, Jackson Library, 10:30 AM — see Today in the Foothills for the cards.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>
    <div class="item"><p><b>Fri Nov 27 — Black Friday, foothills style:</b> <b>Black Friday at the Cave</b>, Bella Grace Vineyards, Plymouth, 9:00 AM · <b>Black Friday Wine Sale &amp; Italian Gift Collections</b>, Avio Vineyards, Sutter Creek, 11:00 AM · <b>Black Friday Weekend at Black Snake Winery</b>, Plymouth, 11:00 AM · <b>Black Friday at Iron Hub</b> and <b>Black Friday at Casino Mine Ranch Winery</b>, Plymouth · the <b>13th Annual My Precious Black Friday Sale</b> at Dobra Zemlja Winery, Plymouth · <b>Thanksgiving Weekend at Terre Rouge &amp; Easton Wines</b> and at <b>Golden Leaves Vineyard &amp; Winery</b>, Somerset · <b>Sutter Creek Plaid Friday</b>, downtown Sutter Creek · <b>Christmas Delights</b> opens on Main Street, Jackson, with the <b>Festival of Trees</b> at 6:00 PM, the <b>Tunnel of Lights</b> at the foot bridge beside the National Hotel, and the <b>South Pole Skating Rink</b> on Main Street · <b>On The Farce Day of Christmas</b>, Cobblestone Theatre, Volcano, 7:30 PM · <b>Community Observatory Public Viewing Night</b>, Placerville, 7:30 PM.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>
    <div class="item"><p><b>Sat Nov 28 — the fullest day of the week:</b> <b>Baked in Amador&#8217;s Saturday Sourdough Breakfast</b>, Volcano, 8:00 AM · <b>Knight Foundry Open Day</b>, Sutter Creek, 10:00 AM · <b>Soup Cook Off at Gibson&#8217;s Roadhouse</b>, Pioneer, 12:00 PM · <b>Tiny Tim&#8217;s Christmas Carol</b>, Baker Street West, Jackson, 2:00 PM · <b>Geoffrey Miller and the Rockin&#8217; Rousers</b>, Fiddletown Community Center, 6:00 PM · <b>Cash Blast at Acorn Ridge Casino</b>, Plymouth, 6:00 PM · <b>Lacy J Dalton&#8217;s Country Christmas Show</b>, Sutter Creek Theatre, 7:00 PM · <b>On The Farce Day of Christmas</b>, Volcano, 7:30 PM · <b>Karaoke @ the Ridge</b>, Acorn Ridge Casino, from 8:00 PM.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>
    <div class="item"><p><b>Sun Nov 29:</b> <b>On The Farce Day of Christmas — Sunday Matinee</b>, Cobblestone Theatre, Volcano, 2:00 PM. A quiet Sunday otherwise in the database — the Christmas season opens in earnest next week.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>
    <div class="item"><p><b>Tue Dec 1 — Giving Tuesday in Fiddletown:</b> <b>Coffee &amp; Conversations</b>, Amador County Chamber of Commerce, Jackson, 8:00 AM · <b>Giving Tuesday Porch Donations</b> with hot cocoa on the Fiddletown Community Center porch, 1:30 PM · <b>Tapas Tuesday at Krissie Vineyards</b>, Plymouth, 3:00 PM · <b>FNRW at Amador Giving Tuesday</b>, Catherine Drexel Hall, Martell, 4:00 PM.</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>
    <div class="item"><p><b>Wed Dec 2:</b> <b>Amador All Stars</b> at Feist Wines, Drytown. <b>Thu Dec 3:</b> the <b>Fiddletown Community Center&#8217;s Annual Meeting</b>, 5:30 PM, and the <b>Amador City Holiday Market</b> opens (Dec 3–6).</p><p class="meta">Source: <a href="https://events.fiddletowngazette.com/">events database</a> published feed · Checked Nov 26</p></div>
  '''
html=replace_block(html,"week-events",week)

history='''
    <div class="hist-hl"><p>⭐ <b>From our own hills — an honest empty well today, and the date is the story.</b> The desk dug back to 1848 through Gold Country timelines, Amador County histories, and Mother Lode records and found <b>no verified Fiddletown, Amador County, or Mother Lode event dated November 26</b>. The desk will not stretch a date to fill the panel. But look at the calendar: <b>Thanksgiving Day 2026 falls on November 26 — the very date Abraham Lincoln fixed for the holiday in 1863</b>, in the middle of the Gold Rush&#8217;s second decade, while these hills were full of miners far from home. The lead item below is as local as a national item gets.</p></div>
    <p><b>1863 — Lincoln proclaims November 26 a national Thanksgiving Day (Nov 26)</b> — President Abraham Lincoln proclaims November 26, 1863 a national day of Thanksgiving, to be celebrated annually on the final Thursday of November. One hundred sixty-three years on, the holiday lands on November 26 again.</p>
    <p><b>1789 — Washington&#8217;s first Thanksgiving is observed (Nov 26)</b> — the first national Thanksgiving under the new Constitution is observed across the young United States, as proclaimed by President George Washington at the request of Congress.</p>
    <p><b>1842 — The University of Notre Dame is founded (Nov 26)</b> — Father Edward Sorin and brothers of the Congregation of Holy Cross found the university on the Indiana frontier at South Bend.</p>
    <p><b>1922 — Carter enters Tutankhamun&#8217;s tomb (Nov 26)</b> — Howard Carter and Lord Carnarvon become the first people in more than 3,000 years to step into the burial chamber of Pharaoh Tutankhamun in Egypt&#8217;s Valley of the Kings — gold of a very different dig.</p>
    <p><b>1942 — <i>Casablanca</i> premieres in New York (Nov 26)</b> — the Humphrey Bogart and Ingrid Bergman film opens at New York&#8217;s Hollywood Theatre, on its way to becoming one of the most loved movies ever made.</p>
    <p><b>1865 — <i>Alice&#8217;s Adventures in Wonderland</i> reaches America (Nov 26)</b> — Lewis Carroll&#8217;s book, published in Britain earlier in the year, is published in America; it has never been out of print since.</p>
    <p><b>2011 — NASA launches the Curiosity rover (Nov 26)</b> — the Mars Science Laboratory lifts off from Cape Canaveral carrying Curiosity, which lands in Gale Crater the following August and is working on Mars still.</p>
    <p class="meta" style="margin-top:8px">Sources: November 26 timelines — Wikipedia (Selected Anniversaries, Nov 26) · timeanddate On This Day · Good News Network history (Nov 26) · on-this-day timelines (Lincoln&#8217;s proclamation · Washington 1789 · Notre Dame · Tutankhamun · Casablanca · Alice · the Curiosity launch) · Checked Nov 26, 2026 · Staged in history/2026-11-26.md</p>
  '''
html=sub(r'<h2>📜 This Day in History — Nov 25</h2>','<h2>📜 This Day in History — Nov 26</h2>',html,label="history h2")
html=replace_block(html,"history",history)

marker='''
    <p class="meta" style="margin-bottom:6px">FROM MARKER BUDDY&#8217;S GOLD COUNTRY CATALOG · No. 11 · Thu Nov 26, 2026</p>
    <h3 style="margin:4px 0 6px">Original Amador Mine — County/Local Marker, Amador City</h3>
    <p><b>What the marker says:</b></p>
    <blockquote style="margin:6px 0 10px;padding:8px 12px;border-left:3px solid var(--gold)">&#8220;Opened in 1852 from six claims. Renamed Original Amador Consolidated working till 1918. Reopened in 1935 till 1937. Shaft reached 1238&#8217;. Total production was $3,500,000.&#8221;</blockquote>
    <p><b>Where:</b> <a href="https://maps.apple.com/?ll=38.419867,-120.82375&amp;q=Original%20Amador%20Mine">Intersection of East School Street and Amador Creek Street, Amador City</a> — on the right when traveling south on East School Street.</p>
    <p>Six claims in 1852 became one of Amador City&#8217;s anchors: the Original Amador worked, as the Original Amador Consolidated, until 1918, slept, then reopened for a last run in 1935–37 — a shaft 1,238 feet deep and $3.5 million in gold all told. The feature runs text-only today — the desk holds no lawful photograph of the marker it has inspected, and it does not borrow HMdb contributors&#8217; pictures.</p>
    <p class="meta">Supplied daily by 🪧 Marker Buddy from his Gold Country marker catalog · <a href="https://davedellaquila.github.io/buddy-system/marker-buddy/markers/original-amador-mine.html">The marker&#8217;s own page</a> · <a href="https://www.hmdb.org/m.asp?m=10329">Marker record at HMdb</a> · A new marker every morning</p>
  '''
html=replace_block(html,"marker-of-the-day",marker)

star='''
    <figure class="skyfig"><img src="sky/2026-11-26.png" alt="Chart of tonight&#8217;s visible planets over Fiddletown: Saturn about 52 degrees up in the south at 8 PM, the waning gibbous Moon low in the east about 10 degrees up, rising 6:52 PM, Jupiter and Mars rising late evening, Venus before dawn"><figcaption>Tonight over Fiddletown — the Moon and visible planets, sunset to sunrise. Higher on the chart = higher in the sky = easier to see. (Chart: the Gazette sky desk, computed for Fiddletown.)</figcaption></figure>
    <p><b>Tonight&#8217;s chart (~8 PM, facing south):</b> Saturn is the evening planet — about 52° up in the south at 8 PM, up all evening. The waning gibbous Moon stands low in the east at 8 PM, about 10° up, and is up all night. Pegasus rides high overhead, Cassiopeia climbs in the northeast, and Taurus rides the east under the Moon&#8217;s glare.</p>
    <p>🌖 <b>Moon:</b> waning gibbous — 93% lit, shrinking toward last quarter. It rises about 6:52 PM and is up all night.</p>
    <p><b>Planets up:</b> Saturn takes the evening — high in the south all night (sets about 2:30 AM). Jupiter rises about 11:00 PM and Mars about 11:30 PM, both brilliant before dawn. Venus is a pre-dawn object only (it rises about 4:00 AM Friday). Mercury is not an evening target tonight.</p>
    <p><b>Notable — the Leonids wind down:</b> the Leonid meteors fade after their Nov 17–18 peak — a few fast streaks still possible in the dark hours, though the bright Moon will wash out all but the brightest. The Taurids&#8217; slow, bright fireballs remain possible on any clear stretch.</p>
    <p><b>Viewing note (honest):</b> tonight is <b>mostly cloudy, low near 47</b> — so expect the Moon and Saturn to show through gaps rather than hold steady, and faint stars and meteors are a poor bet. If a gap opens around 8 PM, Saturn high in the south is the prize, with the bright gibbous Moon low in the east. Dress warm; the ridge cools fast after sunset.</p>
    <p class="meta" style="margin-top:8px">Sources: Gazette sky desk (skyfield, computed for Fiddletown) · International Meteor Organization / EarthSky / NASA (Leonids) · NWS Sacramento (conditions) · Checked Nov 26, 2026 · Staged in sky/2026-11-26.md</p>
  '''
html=replace_block(html,"star-chart",star)

almanac='''
    <p>Sunrise 6:56 AM · Sunset 4:43 PM — a 9-hour-47-minute day, and shrinking.</p>
    <p>Moon: waning gibbous — 93% lit, shrinking toward last quarter. It rises about 6:52 PM and is up all night.</p>
    <p>📅 Thanksgiving Day in the foothills. Today, Thu Nov 26, the foothills run on PST (standard time) until March. Amador County schools are out Wed–Fri for the holiday break. Ahead on the civic clock: Black Friday in the wine country tomorrow, Fri Nov 27, and the Fiddletown Community Center&#8217;s Rockin&#8217; Rousers dance Sat Nov 28.</p>
    <p>Day 330 of 2026 · 35 days left in the year</p>
  '''
html=replace_block(html,"almanac",almanac)

album='''
    <!-- ALBUM:BEGIN — Music Buddy's daily pick, printed verbatim (artist, album, year, write-up, Apple Music links) from Music Buddy's Album of the Day; refreshed in the Morning edition, carried forward at Midday and Evening. See PUBLISHING.md. -->
    <div class="item"><p><b>Keola Beamer — <a href="https://music.apple.com/us/album/kolonahe-from-the-gentle-wind/1491385621"><i>Kolonahe: From the Gentle Wind</i></a> (1999)</b></p>
    <p>A Thanksgiving-morning record from Dave&#8217;s slack-key shelf — Keola Beamer&#8217;s nahenahe touch, where the spaces between the notes are as musical as the notes themselves, and George Winston sits in on &#8220;Ka Makani Ka&#8216;ili Aloha.&#8221; Warm, unhurried guitar that will glow on the Quests before the drive south.</p>
    <p class="meta">Music Buddy's pick for Thursday, November 26, 2026 — the same Album of the Day that goes to Dave by email each morning. <a href="https://davedellaquila.github.io/buddy-system/music-buddy/">Music Buddy's page</a></p></div>
    <!-- ALBUM:END -->
    <p class="meta" style="margin-top:8px">Every pick so far stands in <a href="album-archive.html">The Album of the Day Archive</a>.</p>
  '''
html=replace_block(html,"album-of-the-day",album)

# Passes re-check wording
html=sub(r'The desk re-checked the home crossing this evening — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; 5:26 PM web report lists no restrictions on SR-88, and the CHP CAD board \(updated 5:26 PM today\) holds no SR-88 incident \(see the Safety Wire\)\.','The desk re-checked the home crossing this morning — <b>SR-88 carries no chain control</b> and no restriction of any kind: Caltrans&#8217; morning web report lists no restrictions on SR-88, and the CHP CAD board (updated 6:01 AM today) holds no incidents at all (see the Safety Wire).',html,label="passes intro")
html=sub(r'\(CHP CAD \+ Caltrans, 5:26 PM today\)','(CHP CAD + Caltrans, 6:01 AM today)',html,label="carson row")

# Car shows — today item
html=sub(r'<div class="item"><p><b>Today, Wed Nov 25 — a quiet Wednesday on the circuit\.</b>.*?</div>','<div class="item"><p><b>Today, Thu Nov 26 — Thanksgiving Day, a quiet Thursday on the circuit.</b> The standing meets are Saturday affairs, so no meet runs today; the next round is <b>Sat Nov 28</b> (below). No judged shows today — the season has wound down.</p></div>',html,flags=re.S,label="car shows today")

# Around Town — retire the two spent Nov 25 items
html=sub(r' <div class="item"><p><b>A shout-out for a friend of the paper — Friendsgiving in Placerville\.</b>.*?</div>','',html,flags=re.S,label="around friendsgiving retire")
html=sub(r' <div class="item"><p><b>Luka&#8217;s box dinners — pickup day is Wed Nov 25\.</b>.*?</div>','',html,flags=re.S,label="around luka retire")

# Joke + riddle — new for Nov 26 (yesterday's riddle was the keys one, from the current page)
html=sub(r'<p><b>Today’s joke:</b> Why did the turkey join the band\? …Because it had the drumsticks\.</p>','<p><b>Today’s joke:</b> What do you call a turkey the day after Thanksgiving? …Lucky.</p>',html,label="joke")
html=sub(r'<p><b>Yesterday&#8217;s riddle: What can you catch, but never throw\? — Answer: A cold\.</b></p>','<p><b>Yesterday&#8217;s riddle: What has keys but can&#8217;t open a single lock? — Answer: A piano.</b></p>',html,label="riddle answer")
html=sub(r'<p style="margin-top:6px"><b>Today’s riddle:</b> What has keys but can&#8217;t open a single lock\?</p>','<p style="margin-top:6px"><b>Today’s riddle:</b> What has many teeth but cannot bite?</p>',html,label="riddle today")

open(p,"w",encoding="utf-8").write(html)
print("morning build ok",len(html))
