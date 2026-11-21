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
  '<!-- EDITION:NAME --> Midday Edition — published 12:30 PM PT <!-- /EDITION:NAME -->', html, flags=re.S, label="edition name")

# 2. Weather bug
html = sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->',
  '<!-- WEATHER:BUG --> ☁️ Mostly cloudy this afternoon, high 50°; rain chance tonight (~40%) &amp; Sunday (~50%); SR-88 open, chains or snow tires Cooks Station → Silver Lake; no NWS alert (NWS / Caltrans / CHP) <!-- /WEATHER:BUG -->', html, flags=re.S, label="weather bug")

# 3. Lead headline
html = sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->',
  '<!-- LEAD:HEADLINE --> Midday on a full Saturday — the evening slate is still ahead, and rain returns tonight <!-- /LEAD:HEADLINE -->', html, flags=re.S, label="lead headline")

# 4. Lead closing paragraph (after forecast panel)
html = sub(r'<p><!-- LEAD:BODY --> Saturday opens with.*?</p>',
  '<p><!-- LEAD:BODY --> The morning frost gave way to a mostly cloudy midday, high near 50 — and the foothills are using the fair day while it lasts: Cars &amp; Coffee and the Sourdough Breakfast filled the morning, the cemetery clean-up crew worked the late morning in Jackson, and the afternoon and evening still hold wine-country music at Sobon Estate and Drytown Cellars, Protect The Foothills in Sutter Creek, Feist&#8217;s fifteenth anniversary in Drytown, and theatre in Volcano. Clouds thicken tonight, with a chance of rain after 10 PM — get the evening in first.</p>', html, flags=re.S, label="lead para")

# 5. Safety Wire — midday refresh
safety = '''
    <div class="item"><p><b>Weather — no alert in effect; a mostly cloudy afternoon, and rain returns tonight.</b> At the midday check (12:31 PM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>This afternoon:</b> mostly cloudy, high near 50, with temperatures falling to about 47. <b>Tonight:</b> a chance of rain after 10 PM (about 40%), mostly cloudy, low near 41. <b>Sunday:</b> a chance of rain (about 50%), high near 50 — the morning edition&#8217;s wetter Sunday call has eased — with rain likely Sunday night (about 70%) and patchy frost behind it. <b>Monday</b> turns mostly sunny, high near 54.</p><p class="meta">Sources: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked 12:31 PM PT, Nov 21</p></div>
    <div class="item"><p><b>Roads — SR-88 is open; the chain-control segment has shifted since morning; SR-49 and SR-124 are clear.</b> Caltrans&#8217; midday report lists <b>chains or snow tires required from Cooks Station to Silver Lake (Amador Co)</b> on SR-88 — a different segment than the morning&#8217;s Dew Drop–Woodfords listing; no closure is listed. On SR-49 and SR-124, Caltrans reports <b>no restrictions</b>.</p><p class="meta">Sources: Caltrans road reports for SR-88, SR-49 &amp; SR-124, checked 12:30 PM PT, Nov 21</p></div>
    <div class="item"><p><b>Roads — the CHP board is quiet in the beat, and its chain log agrees with Caltrans.</b> At the midday read (12:31 PM) the Stockton center&#8217;s board held <b>four incidents — no collision or hazard in the beat</b>. The board&#8217;s only Amador entry is the standing chain-control log (No. 0055, logged at the <a href="https://maps.apple.com/?ll=38.343069,-120.763200&amp;q=301%20Clinton%20Rd">Amador CHP office, 301 Clinton Rd, Jackson</a>), whose 10:53 AM detail reads <b>R-2 chain control on SR-88 from Cooks Station to Silver Lake</b> — matching the Caltrans report above. The board&#8217;s other incidents are two no-injury collisions in the Stockton area and a no-injury hit-and-run in San Andreas (Calaveras Co). Nothing names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Pioneer, Volcano, Pine Grove, SR-49, or SR-124.</p><p class="meta">Sources: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 12:31 PM PT, Nov 21</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the midday check.</b> No fire incident in the beat appears on the CHP board at midday. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Sources: CHP CAD Traffic — Stockton center, read 12:31 PM PT, Nov 21</p></div>
  '''
html = replace_block(html, "safety-wire", safety)

# 6. Today in the Foothills — new midday intro; cards stand (they are the DB feed's 12 events for today + the two order-deadline cards)
s, e = block_span(html, "today-events")
blk = html[s:e]
blk2, n = re.subn(r'<p><b>A full Saturday — the fair day between storms\.</b>.*?</p>',
  '<p><b>Midday on a full Saturday — the morning is spent, and the evening slate is still ahead.</b> Today&#8217;s cards are built from the events database&#8217;s published feed — the same feed the public events viewer reads (Dave&#8217;s Nov 21 ruling: if it is not in the database, it does not print here) — <b>12 events in the beat today</b>, wineries first in the desk&#8217;s running order below. Done and dusted: Cars &amp; Coffee, the Sourdough Breakfast, and the cemetery clean-up. Still running: the Rail Explorers out of Ione (to 5:30 PM), Drytown Cellars&#8217; club party (to 5:00 PM), the County Museum (to 3:00 PM), and the Di Arie Dumpling Bar. Ahead: Sobon Estate&#8217;s Radio Plays at 1:00 PM, then tonight&#8217;s run — Cash Blast at Acorn Ridge (6:00 PM), Protect The Foothills in Sutter Creek and Feist&#8217;s fifteenth in Drytown (7:00 PM), and the Volcano farce at 7:30 PM. The two cards at the foot of the section are tomorrow&#8217;s Thanksgiving order deadlines, not database events.</p>', blk, count=1, flags=re.S)
if n == 0: raise SystemExit("today intro not found")
html = html[:s] + blk2 + html[e:]

# 7a. Week Ahead — Today item, midday wording
html = sub(r'<div class="item"><p><b>Today, Sat Nov 21 — anniversaries, coffee, and a cause:</b>.*?</div>',
  '<div class="item"><p><b>Today, Sat Nov 21 — the rest of the day:</b> <b>Drytown Cellars club weekend</b>, to 5:00 PM · <b>Amador Rail Explorers</b>, Ione, to 5:30 PM · <b>Sobon Estate live music</b>, 1:00–3:30 PM · <b>Di Arie Dumpling Bar</b>, Mt Aukum · <b>Cash Blast</b>, Acorn Ridge, 6:00–10:00 PM · <b>Protect The Foothills</b>, Sutter Creek, 7:00–10:00 PM ($25) · <b>Feist&#8217;s Fifteen Year Anniversary with Boot Juice</b>, Drytown, 7:00 PM · <b>On The Farce Day of Christmas</b>, Volcano, 7:30 PM (see Today in the Foothills for the cards; the morning&#8217;s Cars &amp; Coffee, Sourdough Breakfast, and cemetery clean-up have wrapped).</p><p class="meta">Sources: events database published feed · Checked Nov 21</p></div>', html, flags=re.S, label="week today item")

# 7b. Week Ahead — Fri Nov 27: add Golden Leaves (in DB, missing from morning line)
html = sub(r'<b>Black Friday Weekend at Black Snake Winery</b>, Plymouth, 11:00 AM–5:00 PM ·',
  '<b>Black Friday Weekend at Black Snake Winery</b>, Plymouth, 11:00 AM–5:00 PM · <b>Thanksgiving Weekend at Golden Leaves Vineyard &amp; Winery</b>, Somerset, Fri–Sat ·', html, label="golden leaves")

# 7c. Week Ahead — Sat Nov 28: add DB items (Soup Cook Off, Cash Blast, Karaoke)
html = sub(r'<b>Knight Foundry open day</b>, Sutter Creek, 10:00 AM–2:00 PM ·',
  '<b>Knight Foundry open day</b>, Sutter Creek, 10:00 AM–2:00 PM · <b>Soup Cook Off at Gibson&#8217;s Roadhouse</b>, Pioneer, 12:00 PM · <b>Cash Blast</b>, Acorn Ridge, 6:00–10:00 PM · <b>Karaoke @ the Ridge</b>, Acorn Ridge, from 8:00 PM ·', html, label="nov28 adds")

# 8. Weather card — midday
weather = '''
    <p><b>A mostly cloudy afternoon — then the rain returns tonight.</b> <b>This afternoon:</b> mostly cloudy, high near 50, temperatures falling to about 47; light south-southeast wind. <b>Tonight:</b> mostly cloudy, a chance of rain after 10 PM (about 40%), low near 41. <b>Sunday:</b> a chance of rain (about 50%), high near 50; rain likely Sunday night (about 70%), then patchy frost. <b>Monday</b> turns mostly sunny, high near 54, before rain chances return in Thanksgiving week. Up high, SR-88 stays open with chains or snow tires required from Cooks Station to Silver Lake (see the Safety Wire). The five-day panel above carries the numbers, and every day in it opens its own hour-by-hour page.</p>
    <p class="meta">Source: National Weather Service, Sacramento (Fiddletown point) · Forecast checked 12:31 PM PT, Nov 21</p>
  '''
html = replace_block(html, "weather", weather)

# 9. Around Town — retire the three stale Fri Nov 20 notes + re-date the deadlines note
html = sub(r'<div class="item"><p>Friday evening in the foothills:.*?</div>',
  '<div class="item"><p><b>Saturday at midday in the foothills:</b> the morning&#8217;s frost has lifted into a mostly cloudy afternoon, and the day&#8217;s second half is the busy half — wine-country music at Sobon Estate and Drytown Cellars this afternoon, then Protect The Foothills in Sutter Creek, Feist&#8217;s fifteenth anniversary in Drytown, and theatre in Volcano tonight (see Today in the Foothills). Rain holds off until after 10 PM on the midday forecast.</p><p class="meta">Gazette note · Nov 21</p></div>', html, flags=re.S, label="at fri eve")
html = sub(r'<div class="item"><p>Tonight&#8217;s open doors:.*?</div>',
  '<div class="item"><p><b>Tonight&#8217;s open doors:</b> Acorn Ridge&#8217;s Cash Blast runs 6:00–10:00 PM, Feist&#8217;s anniversary show starts at 7:00 PM in Drytown, and Volcano theatre opens at 7:30 PM (see Today in the Foothills).</p><p class="meta">Gazette note · Nov 21</p></div>', html, flags=re.S, label="at tonight")
html = sub(r'<div class="item"><p>Tomorrow is a full Saturday.*?</div>', '', html, flags=re.S, label="at tomorrow")
html = sub(r'(Thanksgiving is Thu Nov 26 — and the order deadlines cluster this Sunday, Nov 22:.*?<p class="meta">)Gazette note · Nov 20(</p>)',
  r'\g<1>Gazette note · Nov 21\g<2>', html, flags=re.S, label="at deadline date")

# 10. Sierra Passes — Carson Pass segment updated to the midday Caltrans read
html = sub(r'chains or snow tires required from west of Dew Drop to west of Woodfords\)',
  'chains or snow tires required from Cooks Station to Silver Lake — the segment as re-reported at midday)', html, label="passes intro segment")
html = sub(r'\(Caltrans, 6:03 AM today: ', '(Caltrans, 12:30 PM today: ', html, label="passes intro time")
html = sub(r're-verified the home crossing this morning', 're-verified the home crossing at midday', html, label="passes intro midday")
html = sub(r'Dew Drop to 1 mi west of Woodfords \(Caltrans, 6:03 AM today\); no closure listed',
  'Cooks Station to Silver Lake (Caltrans, 12:30 PM today); no closure listed', html, label="carson row")

open(p, "w", encoding="utf-8").write(html)
print("midday build ok", len(html))
