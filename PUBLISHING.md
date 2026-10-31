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
