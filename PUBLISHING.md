# Publishing — The Fiddletown Gazette

## Rhythm
- **Morning Edition ~7:00 AM PT** — after Event Buddy's 06:41 intake sweep.
- **Midday Edition ~12:30 PM PT.**
- **Evening Edition ~5:30 PM PT** — evening events + overnight alert picture.
- **Hourly safety poll** between editions (NWS / CHP / CAL FIRE / Cal OES / PG&E). Qualifying events — Red Flag Warning, evacuation order/warning, county fire start, major road closure — trigger an out-of-cycle banner in `#safety-banner` on the front page, stamped with its time.
- Each edition is a full front-page rebuild; each is archived under `editions/YYYY-MM-DD-<morning|midday|evening>.html` and linked from `archive.html`. The masthead always shows when the page was last rebuilt; every item carries its timestamp and source.

## Sources (the desks)
- Safety Wire ← Neighborhood Buddy's verified Fiddletown/Amador patch (NWS Alerts, CHP Stockton center, Cal OES + CAL FIRE public ArcGIS, PG&E public ArcGIS, Amador County Sheriff releases, county OES page). Public-source items only. Burn-day authority: CAL FIRE AEU + Amador County air district — machine-readable feed still to confirm.
- Today / Week Ahead ← Event Buddy's store (Firestore `internalEvents`, project `fiddletown-events`). **Only `isPublic = true`. Never reach around the gate.**
- Weather ← NWS API, Fiddletown zone.
- Community Wire ← local Facebook public/official pages + only groups Dave names and already belongs to. Summarize in our own words, attribute, link the original. Never copy wholesale; never join a group.

## Pre-publish privacy gate (every item, every edition — all three must pass)
1. Public source?
2. Public event? (for events: `isPublic = true`)
3. No private names, addresses, or details? (No residents' private data, no home addresses, nothing from Nextdoor, Dave's mail, or Dave's calendar.)

If any answer is wrong, the item does not print. This line is from Guardian Buddy's Oct 25, 2026 audit and does not bend.

## Front-page markers
`index.html` carries named comment markers (`EDITION:NAME`, `LEAD:*`, `WEATHER:BUG`, section div ids `safety-wire`, `today-events`, `week-events`, `community-wire`, `around-town`, `weather`, and `#safety-banner`) so the edition builder replaces content in place without redesigning the page.

## Standing feature — This Day in History (added Oct 31, 2026, Dave's word)
- A standing box on the front page: sidebar card under Weather (`<h2>This Day in History</h2>` + `<div class="card" id="history">`).
- Keyed to the calendar date of the edition. **Local first** — Fiddletown, Amador County, Gold Country (1849 founding era, the mining years, Shenandoah Valley milestones); a wider California/national item only when the local well runs dry on that date (say so honestly if it does).
- A few crisp items per day, each with its year, written in the paper's own words from public historical sources, attributed in the box's source line.
- **The Morning Edition sets it for the day; Midday and Evening carry it forward unchanged** (unless correcting an error).
- First appearance: the Midday Edition of Sat Oct 31, 2026 (the first edition after the site went live). Researched items for a date may be staged ahead in `history/YYYY-MM-DD.md`.

## Standing feature — Star Chart (added Oct 31, 2026, Dave's word)
- Its own section: `<h2>🔭 Star Chart — Tonight over Fiddletown</h2>` + `<div class="card" id="star-chart">`, sidebar under This Day in History.
- Contents every day: an evening star chart for Fiddletown (a simple labeled schematic of the evening sky is fine), the moon phase, which planets are up and when, and notable events (meteor showers, bright passes, eclipses) when they come.
- Pitch: dark-sky country is part of foothill life. Sources: public astronomy data (e.g. TheSkyLive, StarWalk/Sky Tonight, Astronomy Magazine, timeanddate) and the fleet's Astronomy Buddy as the sky desk when reachable — always in the paper's own words, with a source line.
- **Set by the Morning Edition; carried forward by Midday/Evening** (Evening may refresh the viewing note). Always carry an honest viewing note tied to the actual forecast — if it's cloudy, say so; never oversell a sky nobody can see.
- Staged research may live in `sky/YYYY-MM-DD.md`.

## Standing treatment — Weather Events (added Oct 31, 2026, Dave's word: "obviously the weather events")
- Weather *events* are news, not just a forecast box: storm systems moving in, first rain/snow of the season, heat and freeze events, burn-day status changes, wind events.
- When a weather event is in progress or credibly forecast, the edition carries it as a news item in the main flow (Lead or Around Town, as its importance earns) in addition to the Weather box.
- **Safety-relevant weather events lead the Safety Wire**, as chartered (Red Flag, storm damage risk, chain control, PSPS-relevant wind, flood risk). The hourly safety poll treats a newly-issued severe weather alert as qualifying.
- Weather events *develop* between editions (unlike the history/sky boxes): each edition updates the coverage — rain totals, clearing timing, chain-control changes — with fresh timestamps.
- Worked example, Oct 31, 2026: the season's first real autumn storm system (rain + afternoon thunderstorms, chain control on SR-4) leads the launch editions.

## Language rule (Dave, Oct 31, 2026)
Fiddletown is in the Sierra **foothills** (Gold Country) — never frame the beat generically as "the valley." The events section is **Today in the Foothills**. "Shenandoah Valley" is a proper name and stays (including the masthead line); other proper names (Death Valley) are untouched.

## Community Wire — watch list & importance bar (Dave, Oct 31, 2026)
Dave's ask, adopted: yes — important messages/posts from Facebook (and other social media where a public, connected route exists) belong in the paper, via the Community Wire. Wired as follows:
- **Watch topics/places:** FPPOA, Fiddletown, Plymouth, Drytown, and Sutter Creek (Amador foothills towns in the paper's orbit; Sutter Creek rides the wire/Around Town, the dateline stays Fiddletown).
- **Sources:** official/public pages first — Amador County, City of Plymouth, City of Sutter Creek, Amador County Sheriff, CAL FIRE AEU, CHP, FPPOA's public presence, winery/business pages (Feist/Drytown Social Club and peers) — plus only the community groups Dave names and already belongs to. The paper never joins a group on its own.
- **Importance bar (what earns print):** safety and emergency information, civic decisions and public meetings, road/water/power disruptions, public events, business openings/closures, lost-and-found style factual notices. NOT printed: gossip, arguments, private residents' personal posts beyond a short factual notice (no photos, no personal details).
- **Form:** summarized in the paper's own words, attributed to the posting page, linked to the original post. Never copied wholesale. Every item passes the privacy gate like everything else.
- **Not sources:** Nextdoor (excluded by the privacy line, always). Other platforms only when they offer a public page/post readable through a connected route — same rules as Facebook.

## Events sweep — corrected (Oct 31, 2026, after Dave's "how many events today?")
The launch edition printed 3 of the day's 11 public events. Two process errors, now fixed:
1. **Hallo-Wine on Omo was in the desk's records marked public and got held anyway.** The events desk's local intake files DO carry the gate: ~/workspace/goals/event-manager/hidden_files/event-buddy/intake-*.json — every record has `isPublic`. READ THOSE FILES at press time; print every isPublic=true item in the beat for the edition day. (Earlier editions of this playbook wrongly said the flag wasn't visible.)
2. **Press-time sweep was too narrow.** Every edition ALSO sweeps the public calendars: amadorwine.com/events, bestofamador.com events, events.lodedown.com (Amador), Visit Amador, plus venue pages for anything the desk lists thin. Public events found there print with the calendar credited.
- Count honestly in the report: desk items + calendar finds. If the area is having a big day, the section should show it.
