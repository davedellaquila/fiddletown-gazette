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

def sub(pattern, repl, html, flags=0, label=""):
    new, n = re.subn(pattern, repl, html, count=1, flags=flags)
    if n == 0: raise SystemExit(f"pattern not found: {label or pattern[:90]}")
    return new

# 1. Edition name
html = sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->',
  '<!-- EDITION:NAME --> Evening Edition — published 5:30 PM PT <!-- /EDITION:NAME -->', html, flags=re.S, label="edition name")

# 2. Evening masthead watermark = dusk shot (standing Nov 11 rule)
html = sub(r"background:url\('media/giant-fiddle-closeup-masthead\.jpg'\)",
  "background:url('media/giant-fiddle-dusk-masthead.jpg')", html, label="dusk watermark")

# 3. Weather bug
html = sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->',
  '<!-- WEATHER:BUG --> ☁️ Mostly cloudy tonight, low 41°; rain chance after 10 PM (~40%) &amp; Sunday (~50%); SR-88 open, no restrictions; no NWS alert (NWS / Caltrans / CHP) <!-- /WEATHER:BUG -->', html, flags=re.S, label="weather bug")

# 4. Lead
html = sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->',
  '<!-- LEAD:HEADLINE --> Evening on a full Saturday — tonight&#8217;s slate is on, the passes are clear, and rain waits until late <!-- /LEAD:HEADLINE -->', html, flags=re.S, label="lead headline")
html = sub(r'<p><!-- LEAD:BODY -->.*?</p>',
  '<p><!-- LEAD:BODY --> The fair Saturday is giving way to a busy foothill evening: Cash Blast starts at Acorn Ridge at 6:00 PM, Protect The Foothills and Feist&#8217;s fifteenth anniversary both open at 7:00 PM, and the Volcano farce takes the stage at 7:30 PM. The roads have eased with the day — Caltrans reports no restrictions on SR-88, SR-49, or SR-124 at the evening check, the chain control of midday lifted — and the rain holds off until after 10 PM. One caution for the drive home: CHP logged an injured deer on Shake Ridge Road this evening (see the Safety Wire).</p>', html, flags=re.S, label="lead para")

# 5. Safety Wire — evening refresh
safety = '''
    <div class="item"><p><b>Weather — no alert in effect; a mostly cloudy evening, and rain returns late tonight.</b> At the evening check (5:26 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Tonight:</b> mostly cloudy, low near 41, with a chance of rain after 10 PM (about 40%) — new amounts under a tenth of an inch. <b>Sunday:</b> a chance of rain (about 50%), high near 50, with rain likely Sunday night (about 70%) and patchy frost behind it. <b>Monday</b> turns mostly sunny, high near 54.</p><p class="meta">Sources: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 5:26 PM PT, Nov 21</p></div>
    <div class="item"><p><b>Roads — SR-88, SR-49, and SR-124 all report no restrictions at the evening check; the midday chain control has lifted.</b> Caltrans&#8217; evening reports (5:26 PM) list <b>no traffic restrictions</b> on SR-88 in the Central California / Sierra Nevada area, and none on SR-49 or SR-124 — the chains-or-snow-tires segment from Cooks Station to Silver Lake reported at midday is no longer listed. No closure is listed on any of the three.</p><p class="meta">Sources: Caltrans road reports for SR-88, SR-49 &amp; SR-124, checked 5:26 PM PT, Nov 21</p></div>
    <div class="item"><p><b>Roads — an injured deer on Shake Ridge Road, and the CHP chain log agrees the passes are clear.</b> At the evening read (5:26 PM) the Stockton center&#8217;s board held <b>three incidents</b>. In the beat: an <b>animal hazard — an injured deer — at <a href="https://maps.apple.com/?ll=38.415276,-120.768289&amp;q=Shake%20Ridge%20Rd%20%2F%20Pine%20Gulch%20Rd">Shake Ridge Rd / Pine Gulch Rd</a></b> (No. 0215, logged 5:17 PM, Amador area; a unit was en route at 5:19 PM) — drive that stretch with care tonight. The board&#8217;s standing chain-control log (No. 0172, 2:37 PM) reads <b>&#8220;NO CHAINS ON SR4 / SR88&#8221;</b> — matching the Caltrans report above. The board&#8217;s third incident is a collision with an ambulance en route at Grant Line Rd / S Banta Rd near Tracy, outside the beat. Nothing else names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Pioneer, Volcano, Pine Grove, SR-49, or SR-124.</p><p class="meta">Sources: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 5:26 PM PT, Nov 21</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the evening check.</b> No fire incident in the beat appears on the CHP board this evening. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the main column).</p><p class="meta">Sources: CHP CAD Traffic — Stockton center, read 5:26 PM PT, Nov 21</p></div>
  '''
html = replace_block(html, "safety-wire", safety)

# 6. Today in the Foothills — evening intro + add the CE Barrel Racing card (entered in the DB after midday)
s, e = block_span(html, "today-events")
blk = html[s:e]
blk2, n = re.subn(r'<p><b>Midday on a full Saturday.*?</p>',
  '<p><b>Evening on a full Saturday — the day is spent, and tonight is the main event.</b> Today&#8217;s cards are built from the events database&#8217;s published feed — the same feed the public events viewer reads (Dave&#8217;s Nov 21 ruling: if it is not in the database, it does not print here) — <b>13 events in the beat today</b>. Done and dusted: Cars &amp; Coffee, the Sourdough Breakfast, the cemetery clean-up, the County Museum, Sobon Estate&#8217;s Radio Plays, and Drytown Cellars&#8217; club party. One card is new since midday: the CE Barrel Racing benefit race in Ione, entered in the database this afternoon. Tonight: Cash Blast at Acorn Ridge (6:00 PM), Protect The Foothills in Sutter Creek and Feist&#8217;s fifteenth in Drytown (7:00 PM), and the Volcano farce at 7:30 PM. The two cards at the foot of the section are tomorrow&#8217;s Thanksgiving order deadlines, not database events.</p>', blk, count=1, flags=re.S)
if n == 0: raise SystemExit("today intro not found")
barrel = '<article class="ev"><div class="ev-time">All day</div><div class="ev-body"><h3>CE Barrel Racing — 7D Buckle Benefit Race</h3><p class="ev-venue">📍 <a href="https://maps.apple.com/?q=600+S.+Church+St%2C+Ione%2C+CA">Ed Hughes Memorial Arena, 600 S. Church St, Ione</a></p><p>Cheatham Equine&#8217;s CE Barrel Racing Association runs the 7D Buckle Benefit Race at the Ed Hughes Memorial Arena in Ione — races and clinics for everyone. The database record carries no start time; questions and entries: <a href="tel:+12094434484">(209) 443-4484</a>.</p><p class="meta" style="margin-top:5px">Source: events database published feed (Cheatham Equine / CE Barrel Racing) · <a href="https://ionetoday.com/events.html">Ione Today — events</a> · Checked Nov 21</p></div></article>'
anchor = '<article class="ev"><div class="ev-time">1:00 PM'
idx = blk2.find(anchor)
if idx < 0: raise SystemExit("sobon anchor not found")
blk2 = blk2[:idx] + barrel + blk2[idx:]
html = html[:s] + blk2 + html[e:]

# 7a. Week Ahead — Today item, evening wording
html = sub(r'<div class="item"><p><b>Today, Sat Nov 21 — the rest of the day:</b>.*?</div>',
  '<div class="item"><p><b>Tonight, Sat Nov 21 — what remains:</b> <b>Cash Blast</b>, Acorn Ridge, 6:00–10:00 PM · <b>Protect The Foothills</b>, Sutter Creek, 7:00–10:00 PM ($25) · <b>Feist&#8217;s Fifteen Year Anniversary with Boot Juice</b>, Drytown, 7:00 PM · <b>On The Farce Day of Christmas</b>, Volcano, 7:30 PM (see Today in the Foothills for the cards; the day&#8217;s Cars &amp; Coffee, Sourdough Breakfast, cemetery clean-up, museum, Sobon Estate music, and Drytown club party have wrapped).</p><p class="meta">Sources: events database published feed · Checked Nov 21</p></div>', html, flags=re.S, label="week today item")
# 7b. Week Ahead — Sunday rain call corrected to the evening forecast
html = sub(r'Rain is forecast \(about 80%\) — check before you roll\.',
  'Rain is forecast Sunday (about 50% by day, likely Sunday night) — check before you roll.', html, label="week sun rain")

# 8. Weather card — evening
weather = '''
    <p><b>A mostly cloudy evening — then the rain returns late tonight.</b> <b>Tonight:</b> mostly cloudy, low near 41, with a chance of rain after 10 PM (about 40%). <b>Sunday:</b> a chance of rain (about 50%), high near 50; rain likely Sunday night (about 70%), then patchy frost. <b>Monday</b> turns mostly sunny, high near 54, before rain chances return in Thanksgiving week. Up high, SR-88 is open with no restrictions at the evening check (see the Safety Wire). The five-day panel above carries the numbers, and every day in it opens its own hour-by-hour page.</p>
    <p class="meta">Source: National Weather Service, Sacramento (Fiddletown point) · Forecast checked 5:26 PM PT, Nov 21</p>
  '''
html = replace_block(html, "weather", weather)

# 9. Sierra Passes — Carson Pass updated to the evening Caltrans read (no restrictions)
html = sub(r'The crest is still in winter&#8217;s grip after the storm: most crossings carry the chain-control and closure picture from the last full read \(Thu–Fri\), and the desk re-verified the home crossing at midday — <b>SR-88&#8217;s Carson Pass stays open under chain control</b> \(Caltrans, 12:30 PM today: chains or snow tires required from Cooks Station to Silver Lake — the segment as re-reported at midday\)\.',
  'The crest is still in winter&#8217;s grip after the storm: most crossings carry the chain-control and closure picture from the last full read (Thu–Fri), and the desk re-verified the home crossing this evening — <b>SR-88&#8217;s Carson Pass is open with no restrictions</b> (Caltrans, 5:26 PM today: no traffic restrictions reported; the midday chain control has lifted).', html, label="passes intro")
html = sub(r'<tr><td><b>Carson Pass</b> · 8,573 ft</td><td>SR-88</td><td><b>Chain controls</b> — chains or snow tires required, 3\.6 mi west of Cooks Station to Silver Lake \(Caltrans, 12:30 PM today\); no closure listed</td></tr>',
  '<tr><td><b>Carson Pass</b> · 8,573 ft</td><td>SR-88</td><td><b>Open</b> — no restrictions reported (Caltrans, 5:26 PM today); no closure listed</td></tr>', html, label="carson row")

# 10. Around Town — evening refresh of the two desk notes
html = sub(r'<div class="item"><p><b>Saturday at midday in the foothills:</b>.*?</div>',
  '<div class="item"><p><b>Saturday evening in the foothills:</b> the fair day is closing mostly cloudy, and tonight belongs to the slate — Cash Blast at Acorn Ridge, Protect The Foothills in Sutter Creek, Feist&#8217;s fifteenth in Drytown, and theatre in Volcano (see Today in the Foothills). Rain holds off until after 10 PM on the evening forecast, and SR-88 is clear for the drive home.</p><p class="meta">Gazette note · Nov 21</p></div>', html, flags=re.S, label="at eve")
html = sub(r'<div class="item"><p><b>Tonight&#8217;s open doors:</b> Acorn Ridge&#8217;s Cash Blast runs 6:00–10:00 PM, Feist&#8217;s anniversary show starts at 7:00 PM in Drytown, and Volcano theatre opens at 7:30 PM \(see Today in the Foothills\)\.</p><p class="meta">Gazette note · Nov 21</p></div>',
  '<div class="item"><p><b>Tomorrow&#8217;s look-ahead:</b> a matinee Sunday — the Volcano farce at 2:00 PM, Darin Sexton and Highway 49 at Feist Wines at 4:00 PM, the Fall Craft Gathering at La Mesa at 11:00 AM, and Drytown Cellars&#8217; club weekend day two — with the Baked in Amador and Luka&#8217;s Thanksgiving order deadlines closing (see The Week Ahead).</p><p class="meta">Gazette note · Nov 21</p></div>', html, flags=re.S, label="at tomorrow look")

# 11. Star Chart — evening viewing note refresh
html = sub(r'<p><b>Viewing note \(honest, morning check\):</b>.*?</p>',
  '<p><b>Viewing note (honest, evening check):</b> the early evening is mostly cloudy but the rain is not due until after 10 PM (about 40%) — <b>get out early</b>: Saturn and the bright gibbous Moon in the first hours of darkness are tonight&#8217;s show, and broken cloud may still let them through; by late evening the sky likely closes.</p>', html, flags=re.S, label="star note")

open(p, "w", encoding="utf-8").write(html)
print("evening build ok", len(html))
