#!/usr/bin/env python3
"""One-off Morning Edition build for Sun Nov 22, 2026. Replaces section blocks in place."""
import re
p = "index.html"
html = open(p, encoding="utf-8").read()

def replace_block(html, id_attr, new_inner, tag="div"):
    m = re.search(r'(<%s[^>]*id="%s"[^>]*>)' % (tag, re.escape(id_attr)), html)
    if not m: raise SystemExit(f"block not found: {id_attr}")
    start = m.end(); depth = 1
    pat = re.compile(r'</?%s\b[^>]*>' % tag)
    for mm in pat.finditer(html, start):
        if mm.group(0).startswith('</'):
            depth -= 1
            if depth == 0: return html[:start] + new_inner + html[mm.start():]
        elif not mm.group(0).endswith('/>'): depth += 1
    raise SystemExit(f"unbalanced: {id_attr}")

def sub(pattern, repl, html, count=1, flags=0):
    new, n = re.subn(pattern, repl, html, count=count, flags=flags)
    if n == 0: raise SystemExit(f"pattern not found: {pattern[:90]}")
    return new

# Masthead: Morning uses daytime close-up watermark
html = html.replace("media/giant-fiddle-dusk-masthead.jpg", "media/giant-fiddle-closeup-masthead.jpg")
html = sub(r'<!-- EDITION:DATE -->.*?<!-- /EDITION:DATE -->', '<!-- EDITION:DATE --> Sunday, November 22, 2026 <!-- /EDITION:DATE -->', html)
html = sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->', '<!-- EDITION:NAME --> Morning Edition — published 6:00 AM PT <!-- /EDITION:NAME -->', html)
html = sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->', '<!-- WEATHER:BUG --> 🌧️ Chance of rain today, high 50°; clearing tonight, frost, low 37°; SR-88/49/124 no restrictions; no NWS alert (NWS / Caltrans / CHP) <!-- /WEATHER:BUG -->', html)

# Lead
html = sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->', '<!-- LEAD:HEADLINE --> A rainy matinee Sunday in the foothills — theatre in Volcano, music in Drytown and Plymouth, and the Thanksgiving order books close today <!-- /LEAD:HEADLINE -->', html)
lead_body = ('<!-- LEAD:BODY --> Sunday opens <b>cloudy with a chance of rain (about 40%), high near 50</b> — and the foothills are out anyway: <b>railbikes in Ione</b> and the <b>county museum in Jackson</b> this morning, a <b>Fall Craft Gathering in Sutter Creek</b> and <b>live music at Driven Cellars in Plymouth</b> at midday, the <b>Volcano farce as a Sunday matinee</b> at 2:00 PM, and <b>Darin Sexton and Highway 49 at Feist Wines in Drytown</b> to close the day. <b>No National Weather Service alert is in effect</b> for the Fiddletown point. <b>SR-88, SR-49, and SR-124 all report no restrictions</b> this morning, and the CHP board holds <b>no incident in the beat</b>. Two clocks run out today: <b>Baked in Amador&#8217;s Thanksgiving preorders close at 3:00 PM</b> and <b>Luka&#8217;s box-dinner orders close</b> (see Around Town). Tonight clears to <b>areas of frost, low near 37</b>. Today&#8217;s Road Marker of the Day is the <b>Amador City Cemetery</b> marker. The Sunday Stories release expected today — the Mormon Emigrant Trail — is not yet live on the Stories site this morning, so the Kit Carson story carries as Featured Story below. <!-- /LEAD:BODY -->')
html = sub(r'<p><!-- LEAD:BODY -->.*?</p>', lambda m: '<p>' + lead_body + '</p>', html, flags=re.S)

# Zen — briefing pick Nov 22 (un-tagged entry in zen-quotes-used.md)
zen = '''
      <p style="font-size:19px;font-style:italic">&#8220;To study the Buddha Way is to study the self. To study the self is to forget the self.&#8221;</p>
      <p>Dōgen&#8217;s saying is the morning&#8217;s pick — the same saying as this morning&#8217;s briefing, one Zen saying for the day. On a rainy Sunday of errands and order deadlines, it is a quiet reminder that the studying that matters is the inward kind — and that it ends, happily, in forgetting yourself in the day&#8217;s work.</p>
      <p class="meta">— Dōgen · From the Zen Master — Sayings archive</p>
    '''
html = replace_block(html, "zen-today", zen)

# Safety Wire
safety = '''
    <div class="item"><p><b>Weather — no alert in effect; rain possible today, frost tonight.</b> At the morning check (~6:00 AM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Today:</b> a chance of rain, cloudy, high near 50 (temperatures falling to about 47 in the afternoon), chance of precipitation about 40%. <b>Tonight:</b> a chance of rain before 7 PM, then areas of frost, partly cloudy, low near 37. <b>Monday</b> turns mostly sunny, high near 54, before rain likely returns Tuesday night and Wednesday — plan Thanksgiving travel with that wet stretch in mind.</p><p class="meta">Sources: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked ~6:00 AM PT, Nov 22</p></div>
    <div class="item"><p><b>Roads — SR-88, SR-49, and SR-124 all report no restrictions this morning.</b> Caltrans&#8217; morning reports (6:01 AM) list <b>no traffic restrictions</b> on SR-88 in the Central California / Sierra Nevada area, and none on SR-49 or SR-124. No closure or chain control is listed on any of the three.</p><p class="meta">Sources: Caltrans road reports for SR-88, SR-49 &amp; SR-124, checked 6:01 AM PT, Nov 22</p></div>
    <div class="item"><p><b>Roads — the CHP board holds no incident in the beat.</b> At the morning read (6:03 AM) the Stockton center&#8217;s board held <b>one incident</b> — a collision of unknown injury on <b>I-5 southbound at Eight Mile Road in Stockton</b> (logged 5:28 AM), outside the beat. Nothing names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Pioneer, Volcano, Pine Grove, SR-49, SR-88, or SR-124.</p><p class="meta">Sources: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 6:03 AM PT, Nov 22</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the morning check.</b> No fire incident in the beat appears on the CHP board this morning. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the main column).</p><p class="meta">Sources: CHP CAD Traffic — Stockton center, read 6:03 AM PT, Nov 22</p></div>
  '''
html = replace_block(html, "safety-wire", safety)

# Today in the Foothills — DB only
def ev(time, span, title, venue, venue_url, body, source):
    sp = f'<br><span>{span}</span>' if span else ''
    return (f'<article class="ev"><div class="ev-time">{time}{sp}</div><div class="ev-body"><h3>{title}</h3>'
            f'<p class="ev-venue">📍 <a href="{venue_url}">{venue}</a></p><p>{body}</p>'
            f'<p class="meta" style="margin-top:5px">Source: {source}</p></div></article>')
DBSRC = "events database published feed · Checked Nov 22"
cards = [
 ev("8:00 AM", "– 5:30 PM", "Amador Rail Explorers", "Rail Explorers Amador Staging Area, 702 Hunter Ln, Ione", "https://maps.apple.com/?q=702+Hunter+Ln%2C+Ione%2C+CA",
    "Railbikes out of Ione all day. Tandem from $90, Quad from $175; 10% off bookings of 10 or more. Rain is possible today — check with the operator before you roll.",
    DBSRC + ' · <a href="https://www.railexplorers.net/locations/amador">Rail Explorers — Amador</a> (host: Rail Explorers)'),
 ev("11:00 AM", "– 5:00 PM", "Drytown Cellars — Fall Wine Club Release Party (day two)", "Drytown Cellars, Drytown", "https://maps.apple.com/?q=Drytown+Cellars%2C+Drytown%2C+CA",
    "Day two of the club weekend, Sat–Sun Nov 21–22: tastings, barrel tastings, food, and live music (check with the winery on member and guest terms).",
    DBSRC + ' · <a href="https://drytowncellars.com/events/fall-wine-club-release-party/">Drytown Cellars — events</a> (host: Drytown Cellars)'),
 ev("11:00 AM", None, "Amador County Museum Open", "Amador County Museum, Jackson", "https://maps.apple.com/?q=Amador+County+Museum%2C+Jackson%2C+CA",
    "The county museum is open today — the Kennedy Mine model and the county&#8217;s mining story indoors, a dry and fitting stop on a rainy Sunday.",
    DBSRC + ' · <a href="https://amadorcountyhistoricalsociety.org/county-museum.html">Amador County Historical Society — County Museum</a> (host: Amador County Museum)'),
 ev("11:00 AM", None, "Fall Craft Gathering", "La Mesa, Sutter Creek", "https://maps.apple.com/?q=La+Mesa+Vineyards%2C+Sutter+Creek%2C+CA",
    "A fall craft gathering at the La Mesa tasting room in Sutter Creek. Rain is forecast — check before you roll.",
    DBSRC + ' · <a href="https://lamesavineyards.com/pages/calendar">La Mesa Vineyards — calendar</a> (host: La Mesa)'),
 ev("12:30 PM", None, "The Sun Followers at Driven Cellars", "Driven Cellars, 12595 Steiner Rd, Plymouth", "https://maps.apple.com/?q=12595+Steiner+Rd%2C+Plymouth%2C+CA",
    "Live music from The Sun Followers at Driven Cellars in the Shenandoah Valley. The winery&#8217;s November Wine Pick Up Party runs Nov 21–23.",
    DBSRC + ' · <a href="https://drivencellars.com/winery-events/">Driven Cellars — winery events</a> (host: Driven Cellars)'),
 ev("2:00 PM", "– 4:00 PM", "On The Farce Day of Christmas — Sunday Matinee", "Cobblestone Theatre, Volcano", "https://maps.apple.com/?q=Cobblestone+Theatre%2C+Volcano%2C+CA",
    "The Volcano Theatre Company&#8217;s holiday farce as a Sunday matinee — $24–$25 (the calendars differ by a dollar). It runs through Dec 13.",
    DBSRC + ' · <a href="https://volcanotheatre.net/on-the-farce-day-of-christmas/">Volcano Theatre Company</a> (host: Volcano Theatre Company)'),
 ev("4:00 PM", "– 7:00 PM", "Darin Sexton and Highway 49", "Feist Wines @ The Drytown Social Club, 15950 Highway 49, Drytown", "https://maps.apple.com/?q=15950+Highway+49%2C+Drytown%2C+CA",
    "Live music by Darin Sexton and Highway 49 at Feist Wines @ The Drytown Social Club in Drytown, 4:00–7:00 PM.",
    DBSRC + ' · <a href="https://feistwines.com/event/darin-sexton-and-highway-49-3/">Feist Wines — event</a> (host: Feist Wines)'),
]
intro = ('\n    <p><b>A matinee Sunday — seven listings from the events database.</b> Today in the Foothills is built only from the events database&#8217;s published feed, the same feed the public events viewer reads — <b>seven in-beat events span today</b>, listed below as cards. The desk&#8217;s calendar sweep this morning (Best of Amador, LodeDown, Visit Amador) found nothing in the beat for today that is not already in the database. <b>Tomorrow, Mon Nov 23, in the database:</b> Preschool Story Time at the Ione Branch Library, 10:00 AM, free, and the Jackson City Council at Jackson City Hall, 6:30 PM, free (see The Week Ahead). The Thanksgiving order deadlines closing today — Baked in Amador at 3:00 PM and Luka&#8217;s box dinners — are order material and run in Around Town, not in this listing.</p>\n'
         + "\n".join(cards) + "\n  ")
html = replace_block(html, "today-events", intro)

# Week Ahead — preserve Further Out tail from Knight Foundry item onward
s_idx = html.find('id="week-events"')
# locate block span manually via replace helper logic: extract old inner
m = re.search(r'(<div[^>]*id="week-events"[^>]*>)', html)
start = m.end(); depth=1; pat=re.compile(r'</?div\b[^>]*>')
end=None
for mm in pat.finditer(html, start):
    if mm.group(0).startswith('</'):
        depth-=1
        if depth==0: end=mm.start(); break
    elif not mm.group(0).endswith('/>'): depth+=1
old_week = html[start:end]
kidx = old_week.find("Further out — the Knight Foundry")
if kidx < 0: raise SystemExit("knight further-out not found")
item_start = old_week.rfind('<div class="item">', 0, kidx)
tail = old_week[item_start:]
new_week = '''
    <div class="item"><p><b>Today, Sun Nov 22 — a matinee Sunday:</b> <b>Amador Rail Explorers</b>, Ione, 8:00 AM–5:30 PM · <b>Drytown Cellars club weekend</b> day two, 11:00 AM–5:00 PM · <b>Amador County Museum</b> open, Jackson, 11:00 AM · <b>Fall Craft Gathering</b>, La Mesa, Sutter Creek, 11:00 AM · <b>The Sun Followers at Driven Cellars</b>, Plymouth, 12:30 PM · <b>On The Farce Day of Christmas</b> matinee, Volcano, 2:00–4:00 PM · <b>Darin Sexton and Highway 49</b>, Feist Wines, Drytown, 4:00–7:00 PM (see Today in the Foothills for the cards).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    <div class="item"><p><b>Mon Nov 23 — Jackson sits:</b> <b>Preschool Story Time</b>, Ione Branch Library, 10:00 AM, free · <b>Jackson City Council</b>, Jackson City Hall, 6:30 PM, free.</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    <div class="item"><p><b>Tue Nov 24 — giving back, and pickup day:</b> <b>Thanksgiving Boxes Assembly — Rotary Club</b>, Spur Emporium building, Amador County Fairgrounds, Plymouth, 8:00 AM — in place of the regular meeting, the club packs Thanksgiving food boxes for families in need; breakfast and coffee provided · <b>Baked in Amador Thanksgiving preorder pickup</b> begins today (orders closed Sun Nov 22 — see Around Town).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    <div class="item"><p><b>Wed Nov 25 — the night before:</b> <b>Preschool Story Time</b>, Plymouth Library, 1:00 PM, free · <b>Friendsgiving 2026 — Plymouth Hotel Kitchen &amp; Bar</b>, 6:30 PM — a family-style dinner, $45 a person, tax included, complimentary corkage · <b>Amador All Stars</b> at Feist Wines, Drytown (the weekly local-music showcase) · <b>Luka&#8217;s Thanksgiving box-dinner pickup</b>, by appointment, Jackson (orders closed Sun Nov 22).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    <div class="item"><p><b>Thu Nov 26 — Thanksgiving Day.</b> <b>Jackson Turkey Trot</b>, Lake Tabeaud, Jackson, 8:00–9:30 AM (donations welcomed) · <b>Preschool Story Time</b>, Jackson Library, 10:30 AM, free. Taste in Plymouth is closed for the holiday (see Around Town). The Fiddletown Community Center&#8217;s Rockin&#8217; Rousers dance follows Sat Nov 28 (see At the Fiddletown Community Center).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    <div class="item"><p><b>Fri Nov 27 — Black Friday, foothills style:</b> <b>Black Friday at the Cave</b>, Bella Grace Vineyards, Plymouth, 9:00 AM–4:30 PM · <b>Black Friday at Iron Hub</b>, Plymouth · <b>Black Friday at Casino Mine Ranch Winery</b>, Plymouth · <b>Dobra Zemlja&#8217;s 13th Annual My Precious Black Friday Sale</b> (current releases 40–50% off), Plymouth · <b>Black Friday Weekend at Terre Rouge &amp; Easton</b>, Plymouth · <b>Black Friday Weekend at Black Snake Winery</b>, Plymouth, 11:00 AM–5:00 PM · <b>Black Friday Wine Sale &amp; Italian Gift Collections at Avio Vineyards</b>, Sutter Creek, Fri–Sun · <b>Thanksgiving Weekend at Golden Leaves Vineyard &amp; Winery</b>, Somerset, Fri–Sat · <b>Sutter Creek Plaid Friday</b>, all day · and in Jackson that evening, <b>Festival of Trees</b> and <b>Christmas Delights</b>, 6:00–9:00 PM, with the Tunnel of Lights, the Great Christmas Light Show, and the South Pole Skating Rink (see Further Out).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    <div class="item"><p><b>Sat Nov 28 — the dance, and a full Saturday:</b> <b>Baked in Amador&#8217;s Saturday Sourdough Breakfast</b>, Volcano, 8:00–11:00 AM · <b>Knight Foundry open day</b>, Sutter Creek, 10:00 AM–2:00 PM · <b>Soup Cook Off at Gibson&#8217;s Roadhouse</b>, Pioneer, 12:00–3:00 PM · <b>Tiny Tim&#8217;s Christmas Carol</b>, Baker Street West, Jackson, 2:00–4:00 PM ($28) · <b>Cash Blast</b>, Acorn Ridge, 6:00–10:00 PM · <b>Christmas Delights</b>, Jackson, 6:00–9:00 PM · <b>Lacy J Dalton&#8217;s Country Christmas Show</b>, Sutter Creek Theatre, 7:00–9:00 PM · <b>On The Farce Day of Christmas</b>, Volcano, 7:30 PM · <b>Karaoke @ the Ridge</b>, Acorn Ridge, 8:00 PM–1:00 AM · and at the Fiddletown Community Center, <b>Geoffrey Miller and the Rockin&#8217; Rousers</b> (see At the Fiddletown Community Center, just below).</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    <div class="item"><p><b>Sun Nov 29 — the Black Friday weekend winds down:</b> the <b>Black Friday Wine Sale at Avio Vineyards</b> (Fri–Sun) and <b>Black Friday Weekend at Terre Rouge &amp; Easton</b> close out their runs in wine country. No other in-beat event for Sunday stands in the database at press time — the desk&#8217;s sweep finds for that day are relayed to Events Buddy and will print from the database once entered.</p><p class="meta">Source: events database published feed · Checked Nov 22</p></div>
    ''' + tail
html = html[:start] + new_week + html[end:]

# History
html = sub(r'<h2>📜 This Day in History — Nov 21</h2>', '<h2>📜 This Day in History — Nov 22</h2>', html)
history = '''
    <div class="hist-hl"><p>⭐ <b>From our own hills — an honest empty well today.</b> The desk dug back to 1848 through Gold Country timelines, Amador County histories, and Mother Lode records and found <b>no verified Fiddletown, Amador County, or Mother Lode event dated November 22</b>. The desk will not stretch a date to fill the panel. The California and national pages carry the box — a president lost, and a California studio changes the movies.</p></div>
    <p><b>1963 — President John F. Kennedy is assassinated (Nov 22)</b> — Kennedy is shot in Dallas, Texas, riding in an open motorcade through Dealey Plaza; Vice President Lyndon B. Johnson is sworn in aboard Air Force One the same afternoon. It remains the date a generation measures itself against.</p>
    <p><b>1995 — Toy Story is released (Nov 22)</b> — Pixar&#8217;s <i>Toy Story</i>, the first fully computer-animated feature film, opens in U.S. theatres — made in California by Pixar, then based in Richmond.</p>
    <p><b>1928 — Ravel&#8217;s Boléro premieres (Nov 22)</b> — Maurice Ravel&#8217;s <i>Boléro</i> is first performed in Paris — one long crescendo that has never left the repertoire since.</p>
    <p><b>1869 — The clipper ship Cutty Sark is launched (Nov 22)</b> — launched at Dumbarton, Scotland — one of the last and fastest tea clippers, and the only one to survive intact.</p>
    <p><b>1718 — Blackbeard is killed (Nov 22)</b> — the pirate Edward Teach, known as Blackbeard, is killed off Ocracoke Island, North Carolina.</p>
    <p class="meta" style="margin-top:8px">Sources: November 22 timelines — Wikipedia · Britannica · History · Texas State Historical Association (Kennedy) · Checked Nov 22, 2026 · Staged in history/2026-11-22.md</p>
  '''
html = replace_block(html, "history", history)

# Marker No. 7 — Amador City Cemetery (full text completed from HMdb, per truncated-text rule)
marker = '''
    <p class="meta" style="margin-bottom:6px">FROM MARKER BUDDY&#8217;S GOLD COUNTRY CATALOG · No. 7 · Sun Nov 22, 2026</p>
    <h3 style="margin:4px 0 6px">Amador City Cemetery — County/Local Marker, Amador City</h3>
    <p><b>What the marker says:</b></p>
    <blockquote style="margin:6px 0 10px;padding:8px 12px;border-left:3px solid var(--gold)">&#8220;The first internment in the Amador City Cemetery was 1851 with the last being in 1892. There are many more graves than indicated by the marble headstones. Some graves were never marked and others utilized hand carved wooden markers. During the 1950&#8217;s period, the City hired a person to clear the cemetery of weeds and brush. Albeit this was pre-weed eaters, but the person opted for the more speedy method of clearing the cemetery by the use of fire. In the process, all the wooden markers were destroyed. Note the very rocky ground. This precluded digging graves and frequently dynamite was used. Prior to the erection of the curb and fence in approximately 1915, soil would wash down from Church Street (The Methodist Church was on the corner of Church Street and O&#8217;Neil Alley north west of the cemetery) and that caused a collection of dirt which partially covered some of the headstones on the NW section.&#8221;</blockquote>
    <p class="meta">Erected by the City of Amador City. The catalog&#8217;s staged text was cut short, so the desk completed it in full from the marker&#8217;s HMdb page this morning, as the feature promises.</p>
    <p><b>Where:</b> <a href="https://maps.apple.com/?ll=38.419883,-120.825233&amp;q=Amador%20City%20Cemetery">Church Street, Amador City — the cemetery behind the Imperial Hotel, reached by Water Street off Hwy 49, left on West School Street, then left on Church Street; the marker stands just inside the gate</a>.</p>
    <p>A pioneer burying ground from the first Gold Rush years: burials from 1851 to 1892, graves dug with dynamite in rock too hard for a spade, and a 1950s brush-clearing fire that took the wooden markers with it — which is why so many who lie there lie unnamed. The feature runs text-only today — the desk holds no lawful photograph of the marker it has inspected, and it does not borrow HMdb contributors&#8217; pictures.</p>
    <p class="meta">Supplied daily by 🪧 Marker Buddy from his Gold Country marker catalog · <a href="https://davedellaquila.github.io/buddy-system/marker-buddy/markers/amador-city-cemetery.html">The marker&#8217;s own page</a> · <a href="https://www.hmdb.org/m.asp?m=17020">Marker record at HMdb</a> · A new marker every morning</p>
  '''
html = replace_block(html, "marker-of-the-day", marker)

# Star Chart
star = '''
    <figure class="skyfig"><img src="sky/2026-11-22.png" alt="Chart of tonight&#8217;s visible planets over Fiddletown: Saturn about 52 degrees up in the south at 8 PM, the waxing gibbous Moon in the east-southeast about 54 degrees up setting about 5:55 AM Monday, Jupiter and Mars rising late evening, Venus before dawn"><figcaption>Tonight over Fiddletown — the Moon and visible planets, sunset to sunrise. Higher on the chart = higher in the sky = easier to see. (Chart: the Gazette sky desk, computed for Fiddletown.)</figcaption></figure>
    <p><b>Tonight&#8217;s chart (~8 PM, facing south):</b> Saturn is the evening planet — about 52° up in the south at 8 PM, up all evening. The near-full waxing gibbous Moon stands in the east-southeast at 8 PM, about 54° up, and sets about 5:55 AM Monday. Pegasus rides high overhead, Cassiopeia climbs in the northeast, and Taurus rides the east.</p>
    <p>🌔 <b>Moon:</b> waxing gibbous — about 95% lit at noon. It rises about 3:10 PM and sets about 5:55 AM Monday.</p>
    <p><b>Planets up:</b> Saturn takes the evening — high in the south all night (sets about 2:33 AM). Jupiter rises about 11:02 PM and Mars about 11:12 PM, both brilliant before dawn. Venus is a pre-dawn object only (it rises about 3:51 AM Monday). Mercury is not an evening target tonight.</p>
    <p><b>Notable — the Leonids wind down:</b> the Leonid meteors fade after their Nov 17–18 peak — a few fast streaks still possible in the dark hours, though the bright Moon will wash out the faint ones. No storm is expected this year. The Taurids&#8217; slow, bright fireballs remain possible on any clear stretch.</p>
    <p><b>Viewing note (honest, morning check):</b> today is cloudy with a chance of rain, but <b>tonight the rain chance ends before 7 PM and the sky turns partly cloudy, with areas of frost and a low near 37</b>. The honest word: <b>give the evening an hour to clear</b> — Saturn and the bright Moon are tonight&#8217;s show once the cloud thins, and dress warm for the frost.</p>
    <p class="meta" style="margin-top:8px">Sources: Gazette sky desk (skyfield, computed for Fiddletown) · International Meteor Organization / EarthSky / NASA (Leonids) · NWS Sacramento (conditions) · Checked Nov 22, 2026 · Staged in sky/2026-11-22.md</p>
  '''
html = replace_block(html, "star-chart", star)

# Weather card
weather = '''
    <p><b>A rainy Sunday, a frosty night, and one fair day before the next wet stretch.</b> <b>Today:</b> a chance of rain, cloudy, high near 50, with temperatures falling to about 47 in the afternoon; light northeast wind; new rainfall under a tenth of an inch. <b>Tonight:</b> a chance of rain before 7 PM, then areas of frost, partly cloudy, low near 37. <b>Monday:</b> mostly sunny, high near 54. Then the pattern turns again — rain likely <b>Tuesday night and Wednesday</b>, easing to a slight chance for <b>Thanksgiving Day</b> (partly sunny, high near 61). The five-day panel above carries the numbers, and every day in it opens its own hour-by-hour page.</p>
    <p class="meta">Source: National Weather Service, Sacramento (Fiddletown point) · Forecast checked ~6:00 AM PT, Nov 22</p>
  '''
html = replace_block(html, "weather", weather)

# Almanac
almanac = '''
    <p>Sunrise 6:54 AM · Sunset 4:44 PM — a 9-hour-50-minute day, and shrinking.</p>
    <p>Moon: waxing gibbous — about 95% lit at noon. It rises about 3:10 PM and sets about 5:55 AM Monday.</p>
    <p>📅 A rainy Sunday in the foothills. Today, Sun Nov 22, the foothills run on PST (standard time) until March. Ahead on the civic clock: Thanksgiving is Thu Nov 26, and the Fiddletown Community Center&#8217;s Rockin&#8217; Rousers dance is Sat Nov 28.</p>
    <p>Day 326 of 2026 · 39 days left in the year</p>
  '''
html = replace_block(html, "almanac", almanac)

# Car Shows — Sunday update
html = sub(r'<div class="item"><p><b>Today, Sat Nov 21 — the standing meets run\.</b>.*?</div>',
  '<div class="item"><p><b>Today, Sun Nov 22 — a quiet Sunday on the circuit.</b> The standing meets are Saturday affairs, so no meet runs today; the next round is <b>Sat Nov 28</b> (below). No judged shows today — the season has wound down.</p></div>', html, flags=re.S)
html = sub(r'Next meets: <b>today, Sat Nov 21</b>, then Sat Dec 5 and Sat Dec 19', 'Next meets: <b>Sat Dec 5</b> and Sat Dec 19 (no meet Sat Nov 28 — it is a 4th Saturday)', html)
html = sub(r'So today, Sat Nov 21, it&#8217;s the Palladio in Folsom\.', 'So next Saturday, Nov 28 — a 4th Saturday — it&#8217;s the Palladio in Folsom.', html)

# Sierra Passes intro — morning re-verify of the home crossing
html = sub(r'<p>The crest is still in winter&#8217;s grip after the storm:.*?</p>',
  '<p>The desk re-verified the home crossing this morning — <b>SR-88&#8217;s Carson Pass is open with no restrictions</b> (Caltrans, 6:01 AM today: no traffic restrictions reported on SR-88). The other crossings carry the chain-control and closure picture from the last full read (Thu–Fri) in the rows below, with their last-read status and time in the source line. Elevations from <a href="https://davedellaquila.github.io/sierra-crest-passes/">Dave&#8217;s Sierra Crest Passes tracker</a>.</p>', html, flags=re.S)

# Community Wire — retire the passed Jackson cemetery clean-up item (event was Sat Nov 21)
html = sub(r'<div class="item"><p><b>Jackson invites a hand at the City Cemetery — Sat Nov 21\.</b>.*?</div>', '', html, flags=re.S)

# Around Town — add Baked in Amador preorder-close item before Luka's item
baked_item = '<div class="item"><p><b>Last call — Baked in Amador&#8217;s Thanksgiving preorders close today at 3:00 PM.</b> The Volcano bakery&#8217;s preorder book (loaves, rolls, cookies, and the pumpkin-stencil centerpiece loaf) closes <b>Sunday, November 22 at 3:00 PM</b>; pickup runs Tue Nov 24 – Wed Nov 25. Order ahead for the holiday table at <a href="tel:+12092964301">(209) 296-4301</a>.</p><p class="meta"><a href="https://davedellaquila.github.io/baked-in-amador/">Baked in Amador</a>, 16154 Main St, Volcano · via the bakery&#8217;s specials page</p></div> '
html = sub(r'(<div class="card" id="around-town"> <div class="item"><p><b>Volcano&#8217;s galleries)', baked_item + r'\1', html)

open(p, "w", encoding="utf-8").write(html)
print("build ok", len(html))
