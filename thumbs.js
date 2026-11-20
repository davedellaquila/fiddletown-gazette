/* Thumbs test — The Fiddletown Gazette (Dave's test, Nov 19, 2026).
   SECTION MODEL (Dave's change, Thu Nov 19, 2026 evening): one small, quiet
   👍 at the foot of each SECTION of the paper — not per article or item.
   The reader is voting on whether the section itself belongs in the paper.
   Counted by Analytics Buddy's votes API on the same Cloudflare Worker as
   the visitor counter (collector/API.md), target_type "section". Up-only:
   there is no 👎 in this test. One vote per browser per section per day;
   the server stores only a salted hash of a random browser marker.
   Tallies are day-scoped (section target_id "<date>/<section-id>"), so one
   tally runs across the day's three editions and clears at day's end;
   Analytics Buddy archives each day's results. The footer block
   (#fg-tallies) re-reads GET /votes on a poll and after every vote, so the
   tallies update live.
   NOTE: this file is deliberately separate from votes.js — archived edition
   snapshots load ../votes.js, which stays an inert stub so frozen editions
   never sprout controls. Only the live front page loads thumbs.js. */
(function () {
  "use strict";
  var CFG = { endpoint: "https://visitor-counter.dave-5d7.workers.dev", site: "fiddletown-gazette" };

  function lsGet(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  function edition() {
    // Day-scoped: the tally is TODAY's — one key per calendar day (the
    // fg-edition meta minus its -morning/-midday/-evening suffix), so votes
    // ride across the day's three editions and the count clears at day's
    // end. Analytics Buddy archives each day under this key.
    var m = document.querySelector('meta[name="fg-edition"]');
    var v = (m && m.content) ? m.content : "";
    var d = v.match(/^(\d{4}-\d{2}-\d{2})/);
    if (d) return d[1];
    try { return new Date().toLocaleDateString("en-CA", { timeZone: "America/Los_Angeles" }); } catch (e) { return "front"; }
  }
  var EDITION = edition();
  var picks = lsGet("fg-thumbs-v1", {});   // target_id -> 1
  var TITLES = {};                          // target_id -> section title (for the footer)

  function marker() {
    var m = null;
    try { m = localStorage.getItem("fg-voter"); } catch (e) { /* ignore */ }
    if (!m) {
      if (window.crypto && crypto.getRandomValues) {
        var a = new Uint8Array(16); crypto.getRandomValues(a);
        m = Array.prototype.map.call(a, function (x) { return ("0" + x.toString(16)).slice(-2); }).join("");
      } else { m = "m" + Math.random().toString(16).slice(2) + Date.now().toString(16); }
      try { localStorage.setItem("fg-voter", m); } catch (e) { /* ignore */ }
    }
    return m;
  }
  function api(path, opts) {
    return fetch(CFG.endpoint + path, opts).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }

  function ensureStyle() {
    if (document.getElementById("fg-thumbs-style")) return;
    var s = document.createElement("style");
    s.id = "fg-thumbs-style";
    s.textContent =
      ".fg-vote-row{margin-top:6px}" +
      ".fg-vote{display:inline-flex;align-items:center;gap:5px;font-size:13px;color:var(--muted,#777)}" +
      ".fg-up{font-size:13px;line-height:1;padding:3px 7px;border:1px solid var(--border,#ddd);border-radius:999px;background:transparent;cursor:pointer}" +
      ".fg-up:hover{border-color:var(--accent,#b8860b)}" +
      ".fg-up[aria-pressed=\"true\"]{background:#f7e7bd;border-color:#d9b64a}" +
      ".fg-c{min-width:1ch}" +
      ".fg-note{font-size:12.5px;font-style:italic;transition:opacity .45s ease}" +
      "#fg-tallies .fg-tally-list p{margin-top:3px;font-size:13.5px}";
    document.head.appendChild(s);
  }

  function sectionTitle(h) {
    var t = (h.textContent || "").replace(/\s+/g, " ").trim();
    t = t.replace(/^[^A-Za-z0-9]+/, "");                       // leading emoji / dingbats
    t = t.replace(/\s+—\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}$/, ""); // dated headings (This Day in History — Nov 19)
    return t || "Section";
  }

  function makeControl(id) {
    var wrap = document.createElement("span");
    wrap.className = "fg-vote"; wrap.setAttribute("data-id", id);
    wrap.innerHTML =
      '<button type="button" class="fg-up" aria-label="Give this section a thumbs up" aria-pressed="false">👍</button>' +
      '<span class="fg-c" hidden></span>' +
      '<span class="fg-note" role="status" hidden></span>';
    if (picks[id]) wrap.querySelector(".fg-up").setAttribute("aria-pressed", "true");
    wrap.querySelector(".fg-up").addEventListener("click", function () { castVote(wrap, id); });
    return wrap;
  }
  function paint(wrap, ups) {
    var c = wrap.querySelector(".fg-c");
    c.textContent = ups; c.hidden = false;
    if (picks[wrap.getAttribute("data-id")]) wrap.querySelector(".fg-up").setAttribute("aria-pressed", "true");
  }
  function showNote(wrap, msg) {
    var n = wrap.querySelector(".fg-note");
    if (!n) return;
    n.innerHTML = msg; // desk-constant strings only — the footer phrase carries the #fg-tallies link
    n.hidden = false; n.style.opacity = "0";
    void n.offsetWidth; n.style.opacity = "1";
    if (wrap._nt) clearTimeout(wrap._nt);
    if (wrap._nt2) clearTimeout(wrap._nt2);
    wrap._nt = setTimeout(function () {
      n.style.opacity = "0";
      wrap._nt2 = setTimeout(function () { n.hidden = true; }, 500);
    }, 5000);
  }
  function castVote(wrap, id) {
    if (picks[id]) { showNote(wrap, "Already counted — today's tallies are <a href='#fg-tallies'>in the footer</a>."); return; }
    picks[id] = 1; lsSet("fg-thumbs-v1", picks);
    wrap.querySelector(".fg-up").setAttribute("aria-pressed", "true");
    var c = wrap.querySelector(".fg-c");
    var cur = parseInt(c.textContent, 10);
    c.textContent = (isNaN(cur) ? 0 : cur) + 1; c.hidden = false; // tick up now; the server tally reconciles on return
    showNote(wrap, "Counted — thanks! Today's tallies are <a href='#fg-tallies'>in the footer</a>.");
    api("/vote", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site: CFG.site, target_type: "section", target_id: id, edition: EDITION, value: 1, marker: marker() })
    }).then(function (res) {
      if (res && res.tally) paint(wrap, res.tally.ups);
      refresh();
    });
  }

  function renderFooter(targets) {
    var box = document.querySelector("#fg-tallies .fg-tally-list");
    if (!box) return;
    var rows = (targets || []).filter(function (tg) {
      return tg.target_type === "section" && tg.ups > 0 && TITLES[tg.target_id];
    }).sort(function (a, b) { return b.ups - a.ups; }).slice(0, 8);
    if (!rows.length) {
      box.innerHTML = '<p class="meta">No thumbs yet today — tap the small 👍 at the foot of any section to vote for keeping it in the paper.</p>';
      return;
    }
    box.innerHTML = rows.map(function (tg) {
      var title = TITLES[tg.target_id].replace(/</g, "&lt;");
      return '<p>👍 ' + tg.ups + ' — ' + title + '</p>';
    }).join("");
  }

  function refresh() {
    api("/votes?site=" + encodeURIComponent(CFG.site) + "&edition=" + encodeURIComponent(EDITION)).then(function (res) {
      if (!res || !res.targets) return;
      var byId = {};
      res.targets.forEach(function (tg) { if (tg.target_type === "section") byId[tg.target_id] = tg; });
      Array.prototype.forEach.call(document.querySelectorAll(".fg-vote"), function (w) {
        var tg = byId[w.getAttribute("data-id")];
        paint(w, tg ? tg.ups : 0);
      });
      renderFooter(res.targets);
    });
  }

  // House furniture, not content sections — no vote: the link index, the
  // reference shelf, and the Free Stuff pointer card.
  var SKIP = { "more-gazette": 1, "resources": 1, "free-stuff": 1 };

  function decorate() {
    ensureStyle();
    Array.prototype.forEach.call(document.querySelectorAll("main h2, aside h2"), function (h) {
      // The section's host is the first following sibling element carrying an
      // id (its .card or wrapper div) before the next section heading.
      var host = null, n = h.nextElementSibling;
      while (n) {
        if (n.tagName === "H2") break;
        if (n.nodeType === 1 && n.id) { host = n; break; }
        n = n.nextElementSibling;
      }
      if (!host || SKIP[host.id]) return;
      if (host.querySelector(":scope > .fg-vote-row")) return;
      var id = EDITION + "/" + host.id;
      TITLES[id] = sectionTitle(h);
      var row = document.createElement("div");
      row.className = "fg-vote-row";
      row.appendChild(makeControl(id));
      host.appendChild(row);
    });
    refresh();
    setInterval(refresh, 45000);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", decorate); else decorate();
})();
