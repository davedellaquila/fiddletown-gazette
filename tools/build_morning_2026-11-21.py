#!/usr/bin/env python3
"""One-off Morning Edition build for Sat Nov 21, 2026. Replaces section blocks in place."""
import re, sys
p = "index.html"
html = open(p, encoding="utf-8").read()

def replace_block(html, id_attr, new_inner, tag="div"):
    """Replace inner content of <tag ... id="id_attr" ...> ... </tag> balancing nested same tags."""
    m = re.search(r'(<%s[^>]*id="%s"[^>]*>)' % (tag, re.escape(id_attr)), html)
    if not m:
        raise SystemExit(f"block not found: {id_attr}")
    start = m.end()
    depth = 1
    pat = re.compile(r'</?%s\b[^>]*>' % tag)
    for mm in pat.finditer(html, start):
        if mm.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return html[:start] + new_inner + html[mm.start():]
        else:
            if not mm.group(0).endswith('/>'):
                depth += 1
    raise SystemExit(f"unbalanced: {id_attr}")

def sub(pattern, repl, html, count=1, flags=0):
    new, n = re.subn(pattern, repl, html, count=count, flags=flags)
    if n == 0:
        raise SystemExit(f"pattern not found: {pattern[:80]}")
    return new

# --- Masthead ---
html = sub(r'<!-- EDITION:DATE -->.*?<!-- /EDITION:DATE -->', '<!-- EDITION:DATE --> Saturday, November 21, 2026 <!-- /EDITION:DATE -->', html)
html = sub(r'<!-- EDITION:NAME -->.*?<!-- /EDITION:NAME -->', '<!-- EDITION:NAME --> Morning Edition — published 6:00 AM PT <!-- /EDITION:NAME -->', html)
html = sub(r'<!-- WEATHER:BUG -->.*?<!-- /WEATHER:BUG -->', '<!-- WEATHER:BUG --> 🌤️ Frost early, then partly sunny, high 50°; rain returns tonight &amp; Sunday; SR-88 open, chains or snow tires Dew Drop → Woodfords; no NWS alert (NWS / Caltrans / CHP) <!-- /WEATHER:BUG -->', html)

# --- Lead ---
html = sub(r'<!-- LEAD:HEADLINE -->.*?<!-- /LEAD:HEADLINE -->', '<!-- LEAD:HEADLINE --> Frost at dawn, a full Saturday ahead — and rain returns tonight into Sunday <!-- /LEAD:HEADLINE -->', html)
lead_body = ('<!-- LEAD:BODY --> Saturday opens with <b>areas of frost before 9 AM</b>, then turns <b>partly sunny with a high near 50</b> — the one fair day in a wet stretch, and the foothills are using it: <b>Cars &amp; Coffee in Jackson</b> and the <b>Sourdough Breakfast in Volcano</b> this morning, the <b>Jackson cemetery clean-up</b> mid-morning, wine-country music at <b>Sobon Estate</b> and <b>Drytown Cellars</b> this afternoon, <b>Protect The Foothills in Sutter Creek</b> and <b>Feist&#8217;s fifteenth anniversary in Drytown</b> tonight, and theatre in Volcano. <b>No National Weather Service alert is in effect</b> for the Fiddletown point this morning. <b>SR-88 stays open</b> with chains or snow tires required on the high segment; SR-49 and SR-124 are clear, and the CHP board holds <b>no incident in the beat</b>. Enjoy the day — <b>rain chances return after 9 PM tonight (about 40%) and Sunday brings rain (about 80%), high near 48</b>. Today&#8217;s Road Marker of the Day is the <b>Argonaut and Kennedy Mines</b> at Jackson. <!-- /LEAD:BODY -->')
html = sub(r'<!-- LEAD:BODY -->.*?<!-- /LEAD:BODY -->', lambda m: lead_body, html, flags=re.S)

# --- Zen ---
zen = '''
      <p style="font-size:19px;font-style:italic">&#8220;Letting go gives us freedom, and freedom is the only condition for happiness.&#8221;</p>
      <p>Thich Nhat Hanh&#8217;s saying is the morning&#8217;s pick — the same saying as this morning&#8217;s briefing, one Zen saying for the day. On a bright Saturday between storms, it reads like instructions for the day itself: hold the good hours lightly, and let the rest go.</p>
      <p class="meta">— Thich Nhat Hanh · From the Zen Master — Sayings archive</p>
    '''
html = replace_block(html, "zen-today", zen)

# --- Safety Wire ---
safety = '''
    <div class="item"><p><b>Weather — no alert in effect, frost early, and rain returns tonight.</b> At the morning check (~6:00 AM), the National Weather Service alert feed carries <b>no watch, warning, or advisory for the Fiddletown point</b>. <b>Today:</b> areas of frost before 9 AM, then partly sunny, high near 50 (temperatures falling to about 47 in the afternoon). <b>Tonight:</b> a chance of rain after 9 PM (about 40%), mostly cloudy, low near 40. <b>Sunday:</b> rain, about 80% chance, high near 48. The wet pattern continues into Thanksgiving week — rain likely Tuesday and Wednesday.</p><p class="meta">Sources: National Weather Service Sacramento — alerts &amp; forecast for the Fiddletown point, checked ~6:00 AM PT, Nov 21</p></div>
    <div class="item"><p><b>Roads — SR-88 is open with chain control on the high segment; SR-49 and SR-124 are clear.</b> Caltrans&#8217; morning report lists <b>chains or snow tires required from 3.6 miles west of Dew Drop (Amador Co) to 1 mile west of Woodfords (Alpine Co)</b> on SR-88 — unchanged from last evening; no closure is listed. On SR-49 and SR-124, Caltrans reports <b>no restrictions</b>.</p><p class="meta">Sources: Caltrans road reports for SR-88, SR-49 &amp; SR-124, checked 6:03 AM PT, Nov 21</p></div>
    <div class="item"><p><b>Roads — the CHP board is quiet in the beat.</b> At the morning reads (6:02 and 6:13 AM) the Stockton center&#8217;s board held <b>three, then four incidents — none of them a collision or hazard in the beat</b>. The board&#8217;s Amador entries are the standing <b>chain-control logs for SR-88 (R-2, Dew Drop to Picket&#8217;s Junction)</b>, matching the Caltrans report above; the morning&#8217;s collisions sit in Stockton, on SR-99 and French Camp Road. Nothing names Fiddletown, Plymouth, Jackson, Sutter Creek, Ione, Drytown, Pioneer, Volcano, Pine Grove, SR-49, or SR-124.</p><p class="meta">Sources: <a href="https://cad.chp.ca.gov/Traffic.aspx">CHP CAD Traffic — Stockton center</a>, read 6:02–6:13 AM PT, Nov 21</p></div>
    <div class="item"><p><b>Fire — quiet in the foothills at the morning check.</b> No fire incident in the beat appears on the CHP board this morning. Burn-day status: the paper does not state it — the recorded Burn Day Line (updated daily 4–5 PM) is the authority; call before lighting any outdoor fire (see the Burn Day Line in the rail).</p><p class="meta">Sources: CHP CAD Traffic — Stockton center, read 6:02–6:13 AM PT, Nov 21</p></div>
  '''
html = replace_block(html, "safety-wire", safety)

# --- Today in the Foothills ---
def ev(time, span, title, venue, venue_url, body, source):
    sp = f'<br><span>{span}</span>' if span else ''
    return (f'<article class="ev"><div class="ev-time">{time}{sp}</div><div class="ev-body"><h3>{title}</h3>'
            f'<p class="ev-venue">📍 <a href="{venue_url}">{venue}</a></p><p>{body}</p>'
            f'<p class="meta" style="margin-top:5px">Source: {source}</p></div></article>')

cards = [
 ev("8:00 AM", None, "Amador Cars &amp; Coffee", "Raley&#8217;s, Jackson", "https://maps.apple.com/?q=Raley%27s%2C+Jackson%2C+CA",
    "The county&#8217;s standing meet — 1st &amp; 3rd Saturdays — fills the Raley&#8217;s lot on CA-49 from 8:00 AM. All years, makes, and models; free and family-friendly (see Car Shows).",
    "Amador Cars and Coffee — group flyer · Standing Gazette listing · Checked Nov 21"),
 ev("8:00 AM", "– 11:00 AM", "Baked in Amador&#8217;s Saturday Sourdough Breakfast", "Baked in Amador, 16154 Main St, Volcano", "https://maps.apple.com/?q=16154+Main+St%2C+Volcano%2C+CA",
    "The standing Saturday breakfast at the Volcano bakery — Kris runs the bakery and Tom cooks the pancakes. While you&#8217;re there: Thanksgiving preorders close tomorrow at 3:00 PM (card below). <a href=\"tel:+12092964301\">(209) 296-4301</a>.",
    "Baked in Amador — standing Gazette listing, placed Nov 14 · Checked Nov 21"),
 ev("8:00 AM", "– 5:30 PM", "Amador Rail Explorers", "Rail Explorers Amador Staging Area, 702 Hunter Ln, Ione", "https://maps.apple.com/?q=702+Hunter+Ln%2C+Ione%2C+CA",
    "Railbikes out of Ione all day. Tandem from $90, Quad from $175; 10% off bookings of 10 or more.",
    "Visit Amador — events (carried from the desk&#8217;s Nov 20 check; the site rendered no readable listings this morning) · Checked Nov 21"),
 ev("10:00 AM", "– 12:00 PM", "Jackson City Cemetery Clean-Up Day", "Jackson City Cemetery, Jackson", "https://maps.apple.com/?q=Jackson+City+Cemetery%2C+Jackson%2C+CA",
    "The Cemetery Committee&#8217;s bi-monthly clean-up at the historic city cemetery — volunteers welcome; there is much to be done, and many hands help (see the Community Wire).",
    "City of Jackson — Facebook post, Nov 19 · Checked Nov 21"),
 ev("11:00 AM", "– 3:00 PM", "Amador County Museum Open", "Amador County Museum, Jackson", "https://maps.apple.com/?q=Amador+County+Museum%2C+Jackson%2C+CA",
    "The county museum is open today — the Kennedy Mine model and the county&#8217;s mining story indoors, a fitting companion to today&#8217;s Road Marker (below).",
    "Best of Amador / LodeDown · Checked Nov 20"),
 ev("11:00 AM", "– 5:00 PM", "Drytown Cellars — Fall Wine Club Release Party", "Drytown Cellars, Drytown", "https://maps.apple.com/?q=Drytown+Cellars%2C+Drytown%2C+CA",
    "Day one of the club weekend, Sat–Sun Nov 21–22: tastings, barrel tastings, food, and live music (check with the winery on member and guest terms).",
    "Drytown Cellars · printed Nov 16 · Checked Nov 21"),
 ev("All day", None, "Di Arie Tasting Room Dumpling Bar", "Di Arie Winery, 5200 Di Arie Rd, Mt Aukum", "https://maps.apple.com/?q=Di+Arie+Winery%2C+Mt+Aukum%2C+CA",
    "A Dumpling Bar at the tasting room today, with 50% off selected vintage wines Saturday &amp; Sunday. The events desk&#8217;s intake lists the day without a start time — check with the winery before you roll.",
    "Events desk intake (Di Arie Winery email) · Checked Nov 21"),
 ev("1:00 PM", "– 3:30 PM", "Live Music at Sobon Estate — The Radio Plays", "Sobon Estate, Plymouth", "https://maps.apple.com/?q=Sobon+Estate%2C+Plymouth%2C+CA",
    "The Radio Plays (pop, rock, and more, with a new set list) play the winery and museum this afternoon.",
    "The band&#8217;s Nov 11 announcement · printed Nov 16 · Checked Nov 21"),
 ev("6:00 PM", "– 10:00 PM", "Cash Blast at Acorn Ridge Casino", "Acorn Ridge Casino, 17500 State Highway 49, Plymouth", "https://maps.apple.com/?q=17500+State+Highway+49%2C+Plymouth%2C+CA",
    "The casino&#8217;s Saturday-night drawing run: five players drawn every hour, with up to $1,750 in cash in the pot.",
    '<a href="https://www.acornridgecasino.com/casino/promotions/">Acorn Ridge Casino — promotions</a> · Checked Nov 20'),
 ev("7:00 PM", "– 10:00 PM", "Protect The Foothills — Foothill Conservancy Fundraiser", "Native Sons Hall, 56 Main St, Sutter Creek", "https://maps.apple.com/?q=56+Main+St%2C+Sutter+Creek%2C+CA",
    "An evening of live music for the Foothill Conservancy: the BabyBacks, a six-piece Amador County dance band (rock, blues, funk, soul, some country, and originals). Doors 6:30 PM, music 7:00–10:00 PM, no-host beer and wine bar. $25 — the night supports the Conservancy&#8217;s work protecting rivers, forests, open spaces, and communities in Amador and Calaveras counties.",
    "Best of Amador / LodeDown · Re-checked Nov 21"),
 ev("7:00 PM", None, "Feist Wines&#8217; Fifteen Year Anniversary with Boot Juice", "Feist Wines @ The Drytown Social Club, 15950 Highway 49, Drytown", "https://maps.apple.com/?q=15950+Highway+49%2C+Drytown%2C+CA",
    "Fifteen years of Feist, celebrated at the Drytown Social Club with Boot Juice, a NorCal seven-piece rock/Americana band (acoustic guitar, mandolin, horn section). Tickets $25–$35.",
    "Events desk intake / Feist Wines event page · Checked Nov 21"),
 ev("7:30 PM", None, "On The Farce Day of Christmas", "Cobblestone Theatre, Volcano", "https://maps.apple.com/?q=Cobblestone+Theatre%2C+Volcano%2C+CA",
    "The Volcano Theatre Company&#8217;s holiday farce — $24–$25 (the two calendars differ by a dollar). It runs again tomorrow as a Sunday matinee, 2:00–4:00 PM, and through Dec 13.",
    "Best of Amador / LodeDown · Re-checked Nov 21"),
 ev("Open now", "closes Sun Nov 22, 3:00 PM", "Thanksgiving preorders — Baked in Amador", "Baked in Amador, 16154 Main St, Volcano", "https://maps.apple.com/?q=16154+Main+St%2C+Volcano%2C+CA",
    "The Volcano bakery&#8217;s Thanksgiving preorder book is open and rides until <b>Sunday, November 22 at 3:00 PM</b> — order ahead for the holiday table. <a href=\"tel:+12092964301\">(209) 296-4301</a>.",
    "Baked in Amador — standing Gazette listing, placed Nov 14 · Checked Nov 21"),
 ev("Order soon", "while they last", "Thanksgiving brined turkeys — Swingle Meat Co.", "Swingle Meat Company, 12640 Kennedy Flat Rd, Jackson", "https://maps.apple.com/?q=12640+Kennedy+Flat+Rd,+Jackson,+CA",
    "Swingle&#8217;s <b>All Natural Spiced Brined Turkey, $4.09/lb</b> — order-only, in the shop or by phone at <a href=\"tel:+12092230731\">(209) 223-0731</a>. The birds run 14–16 lbs; smoked ham and honey-cured smoked turkey are reservable too. No published deadline — they urge ordering soon, as quantities go fast. Saturday hours 8 AM–5 PM.",
    "Swingle Meat Co. — &#8220;The November Cut&#8221; flyer · Checked Nov 14"),
]
intro = ('\n    <p><b>A full Saturday — the fair day between storms.</b> The events desk&#8217;s intake carried <b>two in-beat items for today</b> (the Di Arie Dumpling Bar and Feist&#8217;s fifteenth anniversary, both below); the rest of today&#8217;s cards come from the public-calendar sweep and the paper&#8217;s standing listings. One honest gap: the <b>Amador Wine Country calendar (amadorwine.com/events) could not be checked this morning</b> — it sits behind a verification check the desk could not clear — so winery listings stand as last verified (Sobon Estate and Drytown Cellars, from the winery desk); Visit Amador&#8217;s page likewise rendered no readable listings this morning. Best of Amador and LodeDown were re-checked at press time.</p>\n'
         + "\n".join(cards) + "\n  ")
html = replace_block(html, "today-events", intro)

open(p, "w", encoding="utf-8").write(html)
print("part 1 ok", len(html))
