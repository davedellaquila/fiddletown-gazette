/* Thumbs test — The Fiddletown Gazette (Dave's test, Nov 19, 2026).
   A small, quiet 👍 under every article, counted by Analytics Buddy's votes
   API on the same Cloudflare Worker as the visitor counter (collector/API.md).
   Up-only: there is no 👎 in this test. One vote per browser per article per
   edition; the server stores only a salted hash of a random browser marker.
   Tallies are edition-scoped (article target_id "<edition>/<slug>"), so the
   count starts fresh with each edition; Analytics Buddy archives each day's
   results. The footer block (#fg-tallies) re-reads GET /votes on a poll and
   after every vote, so the tallies update live.
   NOTE: this file is deliberately separate from votes.js — archived edition
   snapshots load ../votes.js, which stays an inert stub so frozen editions
   never sprout controls. Only the live front page loads thumbs.js. */
(function () {
  "use strict";
  var CFG = { endpoint: "https://visitor-counter.dave-5d7.workers.dev", site: "fiddletown-gazette" };

  function lsGet(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  function edition() {
    var m = document.querySelector('meta[name="fg-edition"]');
    return (m && m.content) ? m.content : "front";
  }
  var EDITION = edition();
  var picks = lsGet("fg-thumbs-v1", {});   // target_id -> 1
  var TITLES = {};                          // target_id -> article title (for the footer)

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
      "#fg-tallies .fg-tally-list p{margin-top:3px;font-size:13.5px}";
    document.head.appendChild(s);
  }

  function slugify(s) {
    var out = (s || "").toLowerCase().replace(/&[a-z#0-9]+;/g, " ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60).replace(/-+$/, "");
    return out || "item";
  }
  function firstText(el) {
    var sels = ["b", "strong", "h3", "h4"], h = null;
    for (var i = 0; i < sels.length && !h; i++) h = el.querySelector(sels[i]);
    return (h ? h.textContent : el.textContent).replace(/\s+/g, " ").trim().slice(0, 90);
  }
  var usedSlugs = {};
  function uniqueSlug(base) {
    if (!usedSlugs[base]) { usedSlugs[base] = 1; return base; }
    usedSlugs[base] += 1; return base + "-" + usedSlugs[base];
  }

  function makeControl(id) {
    var wrap = document.createElement("span");
    wrap.className = "fg-vote"; wrap.setAttribute("data-id", id);
    wrap.innerHTML =
      '<button type="button" class="fg-up" aria-label="Give this article a thumbs up" aria-pressed="false">👍</button>' +
      '<span class="fg-c" hidden></span>';
    if (picks[id]) wrap.querySelector(".fg-up").setAttribute("aria-pressed", "true");
    wrap.querySelector(".fg-up").addEventListener("click", function () { castVote(wrap, id); });
    return wrap;
  }
  function paint(wrap, ups) {
    var c = wrap.querySelector(".fg-c");
    c.textContent = ups; c.hidden = false;
    if (picks[wrap.getAttribute("data-id")]) wrap.querySelector(".fg-up").setAttribute("aria-pressed", "true");
  }
  function castVote(wrap, id) {
    if (picks[id]) return; // already thumbed: the API treats a repeat as a no-op
    picks[id] = 1; lsSet("fg-thumbs-v1", picks);
    wrap.querySelector(".fg-up").setAttribute("aria-pressed", "true");
    api("/vote", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site: CFG.site, target_type: "article", target_id: id, edition: EDITION, value: 1, marker: marker() })
    }).then(function (res) {
      if (res && res.tally) paint(wrap, res.tally.ups);
      refresh();
    });
  }

  function renderFooter(targets) {
    var box = document.querySelector("#fg-tallies .fg-tally-list");
    if (!box) return;
    var rows = (targets || []).filter(function (tg) {
      return tg.target_type === "article" && tg.ups > 0 && TITLES[tg.target_id];
    }).sort(function (a, b) { return b.ups - a.ups; }).slice(0, 8);
    if (!rows.length) {
      box.innerHTML = '<p class="meta">No thumbs yet in this edition — tap the small 👍 under any article to cast the first.</p>';
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
      res.targets.forEach(function (tg) { if (tg.target_type === "article") byId[tg.target_id] = tg; });
      Array.prototype.forEach.call(document.querySelectorAll(".fg-vote"), function (w) {
        var tg = byId[w.getAttribute("data-id")];
        paint(w, tg ? tg.ups : 0);
      });
      renderFooter(res.targets);
    });
  }

  function decorate() {
    ensureStyle();
    var hosts = [];
    function addAll(sel) { Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) { if (hosts.indexOf(el) < 0) hosts.push(el); }); }
    addAll("article.ev");
    addAll(".item");
    ["the-lead", "featured-story", "marker-of-the-day", "reading-the-roadside"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el && hosts.indexOf(el) < 0 && !el.querySelector(".item, article.ev")) hosts.push(el);
    });
    hosts.forEach(function (el) {
      if (el.querySelector(":scope > .fg-vote-row")) return;
      if (el.closest("#toc, #fg-lightbox, header, nav")) return;
      var title = firstText(el);
      if (title.indexOf("📬 Get the") === 0) return; // the mail join blocks are house ads, not articles
      var slug = el.id && el.id !== "the-lead" ? el.id : uniqueSlug(slugify(title));
      var id = EDITION + "/" + slug;
      TITLES[id] = title;
      var row = document.createElement("div");
      row.className = "fg-vote-row";
      row.appendChild(makeControl(id));
      el.appendChild(row);
    });
    refresh();
    setInterval(refresh, 45000);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", decorate); else decorate();
})();
