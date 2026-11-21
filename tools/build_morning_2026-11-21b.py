#!/usr/bin/env python3
import re
p = "index.html"
html = open(p, encoding="utf-8").read()

def block_span(html, id_attr, tag="div"):
    m = re.search(r'(<%s[^>]*id="%s"[^>]*>)' % (tag, re.escape(id_attr)), html)
    if not m: raise SystemExit(f"not found {id_attr}")
    start = m.end(); depth = 1
    pat = re.compile(r'</?%s\b[^>]*>' % tag)
    for mm in pat.finditer(html, start):
        if mm.group(0).startswith('</'):
            depth -= 1
            if depth == 0: return start, mm.start()
        elif not mm.group(0).endswith('/>'):
            depth += 1
    raise SystemExit(f"unbalanced {id_attr}")

def replace_block(html, id_attr, new_inner, tag="div"):
    s, e = block_span(html, id_attr, tag)
    return html[:s] + new_inner + html[e:]

def sub(pattern, repl, html, flags=0):
    new, n = re.subn(pattern, repl, html, count=1, flags=flags)
    if n == 0: raise SystemExit(f"pattern not found: {pattern[:90]}")
    return new

# --- Week Ahead: keep Further Out items from Knight Foundry onward ---
s, e = block_span(html, "week-events")
old_week = html[s:e]
idx = old_week.find("Further out — the Knight Foundry")
if idx < 0: raise SystemExit("knight further-out not found")
item_start = old_week.rfind('<div class="item">', 0, idx)
tail = old_week[item_start:]
# Gibson further-out: drop the passed Fri Nov 20 dinner clause
tail = tail.replace("<b>Fri Nov 20, 5:00–7:00 PM — Dinner and The Kells</b> (the acoustic duo returns; dinner and music, no cover stated). ", "")
new_week = '''
    <div class="item"><p><b>Today, Sat Nov 21 — anniversaries, coffee, and a cause:</b> <b>Amador Cars &amp; Coffee</b>, Raley&#8217;s, Jackson, 8:00 AM · <b>Baked in Amador&#8217;s Saturday Sourdough Breakfast</b>, Volcano, 8:00–11:00 AM · <b>Amador Rail Explorers</b>, Ione, 8:00 AM–5:30 PM · <b>Jackson City Cemetery Clean-Up Day</b>, 10:00 AM–12:00 PM · <b>Drytown Cellars club weekend</b>, 11:00 AM–5:00 PM · <b>Di Arie Dumpling Bar</b>, Mt Aukum · <b>Sobon Estate live music</b>, 1:00–3:30 PM · <b>Cash Blast</b>, Acorn Ridge, 6:00–10:00 PM · <b>Protect The Foothills</b>, Sutter Creek, 7:00–10:00 PM ($25) · <b>Feist&#8217;s Fifteen Year Anniversary with Boot Juice</b>, Drytown, 7:00 PM ($25–$35) · <b>On The Farce Day of Christmas</b>, Volcano, 7:30 PM (see Today in the Foothills for the cards).</p><p class="meta">Sources: Best of Amador · LodeDown · events desk · standing listings · Checked Nov 21</p></div>
    <div class="item"><p><b>Sun Nov 22 — a matinee Sunday, and the Thanksgiving order deadline:</b> <b>On The Farce Day of Christmas</b> matinee, Cobblestone Theatre, Volcano, 2:00–4:00 PM ($24–$25) · <b>Amador Rail Explorers</b>, Ione, 8:00 AM–5:30 PM · <b>Amador County Museum</b> open, Jackson, 11:00 AM · <b>Darin Sexton and Highway 49</b> at Feist Wines, Drytown, 4:00–7:00 PM ($15) · <b>Drytown Cellars club weekend</b> day two, 11:00 AM–5:00 PM · <b>Baked in Amador Thanksgiving preorders close at 3:00 PM</b> and <b>Luka&#8217;s box-dinner orders close</b> today (see Today in the Foothills / Around Town) · <b>Fall Craft Gathering</b>, La Mesa, Sutter Creek, 11:00 AM (see the Community Wire). Rain is forecast (about 80%) — check before you roll.</p><p class="meta">Sources: Best of Amador · LodeDown · events desk · Checked Nov 21</p></div>
    <div class="item"><p><b>Mon Nov 23 — Jackson sits:</b> <b>Preschool Story Time</b>, Ione Branch Library, 10:00 AM, free · <b>Jackson City Council</b>, Jackson City Hall, 6:30 PM, free.</p><p class="meta">Source: <a href="https://events.lodedown.com/amador">LodeDown — Amador events</a> · Re-checked Nov 21</p></div>
    <div class="item"><p><b>Tue Nov 24 — giving back:</b> <b>Thanksgiving Boxes Assembly — Rotary Club</b>, Spur Emporium building, Amador County Fairgrounds, 8:00 AM — in place of the regular meeting, the club packs Thanksgiving food boxes for families in need; breakfast and coffee provided.</p><p class="meta">Source: events desk intake (Rotary Club update) · Checked Nov 21</p></div>
    <div class="item"><p><b>Wed Nov 25 — the night before:</b> <b>Preschool Story Time</b>, Plymouth Library, 1:00 PM, free · <b>Friendsgiving 2026 — Plymouth Hotel Kitchen &amp; Bar</b>, 6:30 PM — a family-style dinner, $45 a person, tax included, complimentary corkage (reservations were asked by Fri Nov 20) · <b>Amador All Stars</b> at Feist Wines, Drytown (the weekly local-music showcase; time tentative in the desk&#8217;s listing).</p><p class="meta">Sources: LodeDown · events desk intake · Checked Nov 21</p></div>
    <div class="item"><p><b>Thu Nov 26 — Thanksgiving Day.</b> <b>Jackson Turkey Trot</b>, Lake Tabeaud, Jackson, 8:00–9:30 AM (donations welcomed) · <b>Preschool Story Time</b>, Jackson Library, 10:30 AM, free. Taste in Plymouth is closed for the holiday (see Around Town). The Fiddletown Community Center&#8217;s Rockin&#8217; Rousers dance follows Sat Nov 28 (see At the Fiddletown Community Center).</p><p class="meta">Sources: LodeDown · Gazette note · Checked Nov 21</p></div>
    <div class="item"><p><b>Fri Nov 27 — Black Friday, foothills style:</b> <b>Black Friday at the Cave</b>, Bella Grace Vineyards, Plymouth, from 9:00 AM · <b>Black Friday at Iron Hub</b>, Plymouth, 11:00 AM–5:00 PM · <b>Black Friday at Casino Mine Ranch Winery</b>, Plymouth · <b>Dobra Zemlja&#8217;s My Precious Black Friday Sale</b> (current releases 40–50% off), Plymouth · <b>Black Friday Weekend at Terre Rouge &amp; Easton</b>, Plymouth · <b>Black Friday Weekend at Black Snake Winery</b>, Plymouth, 11:00 AM–5:00 PM · <b>Sutter Creek Plaid Friday</b>, all day · and in Jackson that evening, <b>Festival of Trees</b> and <b>Christmas Delights</b>, 6:00–9:00 PM, with the Tunnel of Lights, the Great Christmas Light Show, and the South Pole Skating Rink (see Further Out).</p><p class="meta">Sources: events desk intake (Amador Wine listings) · LodeDown · Best of Amador · Checked Nov 21</p></div>
    <div class="item"><p><b>Sat Nov 28 — the dance:</b> <b>Geoffrey Miller and the Rockin&#8217; Rousers</b>, Fiddletown Community Center — doors 6 PM, free dance instruction 6:15–7 PM, show 7 PM, $20 advance / $25 door (see At the Fiddletown Community Center) · <b>Knight Foundry open day</b>, Sutter Creek, 10:00 AM–2:00 PM · <b>Tiny Tim&#8217;s Christmas Carol</b>, Baker Street West, Jackson, 2:00–4:00 PM ($28) · <b>Christmas Delights</b>, Jackson, 6:00–9:00 PM · <b>On The Farce Day of Christmas</b>, Volcano, 7:30 PM.</p><p class="meta">Sources: events desk · LodeDown · Knight Foundry · Checked Nov 21</p></div>
    ''' + tail
html = html[:s] + new_week + html[e:]

# --- History ---
html = sub(r'<h2>📜 This Day in History — Nov 20</h2>', '<h2>📜 This Day in History — Nov 21</h2>', html)
history = '''
    <div class="hist-hl"><p>⭐ <b>From our own hills — an honest empty well today.</b> The desk dug back to 1848 through Gold Country timelines, county histories, and Fiddletown&#8217;s own records and found <b>no verified Fiddletown, Amador County, or Mother Lode event dated November 21</b>. The desk will not stretch a date to fill the panel. The California page carries the box — a monument in the lava country, the internet&#8217;s first permanent link, and trouble off San Francisco.</p></div>
    <p><b>1925 — Lava Beds National Monument is established (Nov 21)</b> — President Calvin Coolidge establishes Lava Beds National Monument in northeastern California — one of the country&#8217;s largest concentrations of lava-tube caves, and the ground of Captain Jack&#8217;s Stronghold from the Modoc War.</p>
    <p><b>1969 — The first permanent ARPANET link (Nov 21)</b> — UCLA and the Stanford Research Institute establish a permanent network connection — an early, durable stitch in the net that became the internet, sewn between two California campuses.</p>
    <p><b>1910 — Attempted piracy off San Francisco (Nov 21)</b> — an extraordinary attempted seizure unfolds aboard the steamship <i>Buckman</i> near San Francisco, by men who reportedly believed she carried valuable gold; the attack turns deadly and the ship&#8217;s captain is killed.</p>
    <p><b>1620 — The Mayflower Compact is signed (Nov 21)</b> — Plymouth Colony&#8217;s settlers sign the Mayflower Compact (dated November 11, Old Style) — a namesake date for our own Plymouth down the road, three centuries and a continent apart.</p>
    <p><b>1877 — Edison announces the phonograph (Nov 21)</b> — Thomas Edison announces his invention of a machine that can record and play sound.</p>
    <p><b>1789 — North Carolina ratifies the Constitution (Nov 21)</b> — North Carolina becomes the 12th state to ratify the United States Constitution.</p>
    <p class="meta" style="margin-top:8px">Sources: November 21 timelines — Wikipedia, November 21 · CalExplornia — California History in November (Lava Beds, ARPANET, Buckman) · National Park Service — Lava Beds · Checked Nov 21, 2026 · Staged in history/2026-11-21.md</p>
  '''
html = replace_block(html, "history", history)

# --- Marker No. 6 ---
marker = '''
    <p class="meta" style="margin-bottom:6px">FROM MARKER BUDDY&#8217;S GOLD COUNTRY CATALOG · No. 6 · Sat Nov 21, 2026</p>
    <h3 style="margin:4px 0 6px">Argonaut and Kennedy Mines — California Historical Landmark No. 786, Jackson</h3>
    <p><b>What the marker says:</b></p>
    <blockquote style="margin:6px 0 10px;padding:8px 12px;border-left:3px solid var(--gold)">&#8220;Argonaut Mine, discovered 1850, and Kennedy Mine, discovered 1856, played dramatic roles in the economic development of California. They produced $105,268,760 in gold. Kennedy Mine has a vertical shaft of 5,912 feet, the deepest in the United States and changed mining methods in the Mother Lode. The Argonaut Mine was the scene of the Mother Lode&#8217;s most tragic mine disaster. Forty-eight miners were trapped in a fire at the 3,500 foot level on August 27, 1922 &#8212; a few survived. Both mines closed in 1942.&#8221;</blockquote>
    <p><b>Where:</b> <a href="https://maps.apple.com/?ll=38.364683,-120.787133&amp;q=Argonaut%20and%20Kennedy%20Mines">On State Highway 49, at the rest area across from the Kennedy Mine, 1.6 miles north of Jackson</a> — the Kennedy headframe still stands over the highway.</p>
    <p>Two neighbours, two legends: the Kennedy, the deepest mine in the country in its day, and the Argonaut, whose 1922 fire remains the Mother Lode&#8217;s darkest day. Together they poured more than a hundred million dollars in gold into California. The feature runs text-only today — the desk holds no lawful photograph of the marker it has inspected, and it does not borrow HMdb contributors&#8217; pictures.</p>
    <p class="meta">Supplied daily by 🪧 Marker Buddy from his Gold Country marker catalog · <a href="https://davedellaquila.github.io/buddy-system/marker-buddy/markers/argonaut-and-kennedy-mines.html">The marker&#8217;s own page</a> · <a href="https://www.hmdb.org/m.asp?m=100586">Marker record at HMdb</a> · A new marker every morning</p>
  '''
html = replace_block(html, "marker-of-the-day", marker)

# --- Star Chart ---
star = '''
    <figure class="skyfig"><img src="sky/2026-11-21.png" alt="Chart of tonight&#8217;s visible planets over Fiddletown: Saturn about 52 degrees up in the south-southeast at 8 PM, the waxing gibbous Moon in the southeast about 58 degrees up setting about 4:39 AM, Jupiter and Mars rising late evening, Venus before dawn"><figcaption>Tonight over Fiddletown — the Moon and visible planets, sunset to sunrise. Higher on the chart = higher in the sky = easier to see. (Chart: the Gazette sky desk, computed for Fiddletown.)</figcaption></figure>
    <p><b>Tonight&#8217;s chart (~8 PM, facing south):</b> Saturn is the evening planet — about 52° up in the south-southeast at 8 PM, up all evening. The waxing gibbous Moon stands in the southeast at 8 PM, about 58° up, and sets about 4:39 AM Sunday. Pegasus rides high overhead, Cassiopeia climbs in the northeast, and Taurus rides the east.</p>
    <p>🌔 <b>Moon:</b> waxing gibbous — about 89% lit at noon. It rises about 2:38 PM and sets about 4:39 AM Sunday.</p>
    <p><b>Planets up:</b> Saturn takes the evening — high in the south-southeast all night. Jupiter rises about 11:06 PM and Mars about 11:14 PM, both brilliant before dawn. Venus is a pre-dawn object only (it rises about 3:54 AM). Mercury is not an evening target tonight.</p>
    <p><b>Notable — the Leonids wind down:</b> the Leonid meteors fade after their Nov 17–18 peak — a few fast streaks still possible in the dark hours, though the bright Moon will wash out the faint ones. No storm is expected this year. The Taurids&#8217; slow, bright fireballs remain possible on any clear stretch.</p>
    <p><b>Viewing note (honest, morning check):</b> the early evening should be fair — NWS calls today partly sunny after morning frost — but <b>clouds thicken and a chance of rain arrives after 9 PM (about 40%)</b>. The honest word: <b>get out early</b> — Saturn and the Moon in the first hours of darkness are tonight&#8217;s show; by late evening the sky may close.</p>
    <p class="meta" style="margin-top:8px">Sources: Gazette sky desk (skyfield, computed for Fiddletown) · International Meteor Organization / EarthSky / NASA (Leonids) · NWS Sacramento (conditions) · Checked Nov 21, 2026 · Staged in sky/2026-11-21.md</p>
  '''
html = replace_block(html, "star-chart", star)

# --- Weather card ---
weather = '''
    <p><b>Frost at dawn, a fair Saturday — then the rain returns.</b> <b>Today:</b> areas of frost before 9 AM, then partly sunny, high near 50, with temperatures falling to about 47 in the afternoon; light southeast wind. <b>Tonight:</b> mostly cloudy, a chance of rain after 9 PM (about 40%), low near 40. <b>Sunday:</b> rain, high near 48 (about 80% chance). <b>Monday</b> turns mostly sunny, high near 53, before rain likely returns Tuesday and Wednesday — a wet Thanksgiving week is shaping up. Up high, SR-88 stays open with chains or snow tires required on the high segment (see the Safety Wire). The five-day panel above carries the numbers, and every day in it opens its own hour-by-hour page.</p>
    <p class="meta">Source: National Weather Service, Sacramento (Fiddletown point) · Forecast checked ~6:00 AM PT, Nov 21</p>
  '''
html = replace_block(html, "weather", weather)

# --- Almanac ---
almanac = '''
    <p>Sunrise 6:52 AM · Sunset 4:46 PM — a 9-hour-54-minute day, and shrinking.</p>
    <p>Moon: waxing gibbous — about 89% lit at noon. It rises about 2:38 PM and sets about 4:39 AM Sunday.</p>
    <p>📅 A bright Saturday in the foothills. Today, Sat Nov 21, the foothills run on PST (standard time) until March. Ahead on the civic clock: Thanksgiving is Thu Nov 26, and the Fiddletown Community Center&#8217;s Rockin&#8217; Rousers dance is Sat Nov 28.</p>
    <p>Day 325 of 2026 · 40 days left in the year</p>
  '''
html = replace_block(html, "almanac", almanac)

# --- Car Shows: today's item ---
html = sub(r'<div class="item"><p><b>Today, Fri Nov 20 — no shows on the foothill calendar\.</b>.*?</div>',
  '<div class="item"><p><b>Today, Sat Nov 21 — the standing meets run.</b> It&#8217;s a 3rd Saturday, so <b>Amador Cars &amp; Coffee fills the Raley&#8217;s lot in Jackson from 8:00 AM</b>, and the Folsom rotation puts <b>Cars &amp; Coffee at the Palladio in Folsom, 7:00–9:30 AM</b>. Placerville&#8217;s Saturday-morning meet runs on Broadway as usual. No judged shows today — the season has wound down (below).</p></div>', html, flags=re.S)
html = sub(r'Next meets: <b>Sat Nov 21</b>, Sat Dec 5, and Sat Dec 19', 'Next meets: <b>today, Sat Nov 21</b>, then Sat Dec 5 and Sat Dec 19', html)
html = sub(r'So next Sat Nov 21 it&#8217;s the Palladio in Folsom\.', 'So today, Sat Nov 21, it&#8217;s the Palladio in Folsom.', html)

# --- Sierra Passes intro + Carson Pass row ---
html = sub(r'<p>A hard day on the crest, easing at the edges:.*?</p>',
  '<p>The crest is still in winter&#8217;s grip after the storm: most crossings carry the chain-control and closure picture from the last full read (Thu–Fri), and the desk re-verified the home crossing this morning — <b>SR-88&#8217;s Carson Pass stays open under chain control</b> (Caltrans, 6:03 AM today: chains or snow tires required from west of Dew Drop to west of Woodfords). Rows other than Carson Pass carry their last-read status and time in the source line below. Elevations from <a href="https://davedellaquila.github.io/sierra-crest-passes/">Dave&#8217;s Sierra Crest Passes tracker</a>.</p>', html, flags=re.S)

open(p, "w", encoding="utf-8").write(html)
print("part 2 ok", len(html))
