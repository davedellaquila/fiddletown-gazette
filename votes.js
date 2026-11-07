/* Reader voting — The Fiddletown Gazette (standing element, Nov 7, 2026).
   Contract: Analytics Buddy's votes API (collector/API.md) — same Cloudflare
   Worker as the visitor counter. ENDPOINT stays "" until Dave's one-time
   deploy lands; while it is "", votes are kept ONLY in the reader's own
   browser (localStorage) and NO shared tallies are shown — the paper never
   prints a number it doesn't have. When the endpoint is wired in, local
   picks are submitted once and the real tallies light up.
   Targets (binding conventions):
     article: target_id "<edition>/<article-slug>", edition field repeats it
     section: target_id bare container slug, edition = edition being read
   Identity: a random marker minted on first vote, kept in localStorage as
   "fg-voter"; the server stores only a salted hash of it. */
(function () {
  "use strict";
  var CFG = { endpoint: "", site: "fiddletown-gazette" };
  window.FG_VOTES = CFG;

  function lsGet(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode: picks simply don't persist */ } }
  function edition() {
    var m = document.querySelector('meta[name="fg-edition"]');
    if (m && m.content) return m.content;
    var p = location.pathname.match(/(\d{4}-\d{2}-\d{2}-(?:morning|midday|evening))\.html/);
    return p ? p[1] : "front";
  }
  var EDITION = edition();
  var picks = lsGet("fg-votes-v1", {});   // "type|target_id|edition" -> 1 | -1
  var sent = lsGet("fg-votes-sent", {});  // same key -> value last submitted
  function key(t, id, ed) { return t + "|" + id + "|" + ed; }
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
    if (!CFG.endpoint) return Promise.resolve(null);
    return fetch(CFG.endpoint.replace(/\/$/, "") + path, opts).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }
  function postVote(t, id, value) {
    return api("/vote", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site: CFG.site, target_type: t, target_id: id, edition: EDITION, value: value, marker: marker() })
    }).then(function (res) {
      if (res && res.ok) { sent[key(t, id, EDITION)] = value; lsSet("fg-votes-sent", sent); }
      return res;
    });
  }

  /* ---------- decoration ---------- */
  function slugify(s) {
    var out = (s || "").toLowerCase().replace(/&[a-z#0-9]+;/g, " ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60).replace(/-+$/, "");
    return out || "item";
  }
  function firstText(el) {
    var sels = ["h2", "h3", "h4", "b", "strong"], h = null;
    for (var i = 0; i < sels.length && !h; i++) h = el.querySelector(sels[i]);
    return (h ? h.textContent : el.textContent).replace(/\s+/g, " ").trim().slice(0, 90);
  }
  var usedSlugs = {};
  function uniqueSlug(base) {
    if (!usedSlugs[base]) { usedSlugs[base] = 1; return base; }
    usedSlugs[base] += 1; return base + "-" + usedSlugs[base];
  }
  function makeControl(t, id) {
    var wrap = document.createElement("span");
    wrap.className = "fg-vote"; wrap.setAttribute("data-t", t); wrap.setAttribute("data-id", id);
    wrap.innerHTML =
      '<button type="button" class="fg-up" aria-label="Thumbs up" aria-pressed="false">👍</button>' +
      '<span class="fg-c fg-cu" hidden></span>' +
      '<button type="button" class="fg-dn" aria-label="Thumbs down" aria-pressed="false">👎</button>' +
      '<span class="fg-c fg-cd" hidden></span>';
    var mine = picks[key(t, id, EDITION)] || 0;
    paint(wrap, mine, null);
    wrap.querySelector(".fg-up").addEventListener("click", function () { castVote(wrap, t, id, 1); });
    wrap.querySelector(".fg-dn").addEventListener("click", function () { castVote(wrap, t, id, -1); });
    return wrap;
  }
  function paint(wrap, mine, tally) {
    var up = wrap.querySelector(".fg-up"), dn = wrap.querySelector(".fg-dn");
    up.setAttribute("aria-pressed", mine === 1 ? "true" : "false");
    dn.setAttribute("aria-pressed", mine === -1 ? "true" : "false");
    if (tally) {
      var cu = wrap.querySelector(".fg-cu"), cd = wrap.querySelector(".fg-cd");
      cu.textContent = tally.ups; cd.textContent = tally.downs;
      cu.hidden = false; cd.hidden = false;
    }
  }
  function castVote(wrap, t, id, value) {
    var k = key(t, id, EDITION);
    if (picks[k] === value) return; // same thumb again: no-op (per contract)
    picks[k] = value; lsSet("fg-votes-v1", picks);
    paint(wrap, value, null);
    if (CFG.endpoint) {
      postVote(t, id, value).then(function (res) { if (res && res.tally) paint(wrap, value, res.tally); });
    }
  }
  function decorate() {
    // Sections: every <h2> in the paper's columns whose content container carries the section id.
    var heads = document.querySelectorAll("h2");
    Array.prototype.forEach.call(heads, function (h2) {
      if (h2.closest("#the-lead")) return; // the lead is an article, below
      if (h2.closest("header, nav, #fg-lightbox, #toc")) return; // page chrome, not a section
      var c = h2.nextElementSibling;
      if (!c || !c.id) { var p = h2.parentElement; c = (p && p.id) ? p : null; }
      if (!c || c.querySelector(":scope > .fg-vote, :scope .fg-vote-row")) { /* still allow if container lacks control */ }
      if (h2.querySelector(".fg-vote")) return;
      h2.appendChild(makeControl("section", c ? c.id : slugify(h2.textContent)));
    });
    // Articles: event cards, wire/desk items, contributor pieces, plus the lead and the recipe feature.
    var hosts = [];
    function addAll(sel) { Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) { if (hosts.indexOf(el) < 0) hosts.push(el); }); }
    addAll("article.ev");
    addAll(".item");
    addAll("#nan-pieces > *, #marci-pieces > *, #kathy-pieces > *");
    var lead = document.querySelector("#the-lead"); if (lead) hosts.unshift(lead);
    var recipe = document.querySelector("#recipe-corner"); if (recipe && hosts.indexOf(recipe) < 0) hosts.push(recipe);
    hosts.forEach(function (el) {
      if (el.querySelector(":scope > .fg-vote-row")) return;
      if (el.closest("#toc")) return;
      var slug = el.id && el.id !== "the-lead" && el.id !== "recipe-corner" ? el.id : uniqueSlug(slugify(firstText(el)));
      var row = document.createElement("div");
      row.className = "fg-vote-row";
      row.appendChild(makeControl("article", EDITION + "/" + slug));
      el.appendChild(row);
    });
    // Live tallies (only when the endpoint exists) + one-time flush of local picks.
    if (CFG.endpoint) {
      api("/votes?site=" + encodeURIComponent(CFG.site) + "&edition=" + encodeURIComponent(EDITION)).then(function (res) {
        if (!res || !res.targets) return;
        var byKey = {};
        res.targets.forEach(function (tg) { byKey[tg.target_type + "|" + tg.target_id] = tg; });
        Array.prototype.forEach.call(document.querySelectorAll(".fg-vote"), function (w) {
          var tg = byKey[w.getAttribute("data-t") + "|" + w.getAttribute("data-id")];
          var mine = picks[key(w.getAttribute("data-t"), w.getAttribute("data-id"), EDITION)] || 0;
          paint(w, mine, tg || { ups: 0, downs: 0 });
        });
      });
      Object.keys(picks).forEach(function (k) {
        var parts = k.split("|");
        if (parts[2] !== EDITION) return;
        if (sent[k] !== picks[k]) postVote(parts[0], parts[1], picks[k]);
      });
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", decorate); else decorate();

  // Small API for votes.html (results + rankings).
  window.FG_VOTES_API = {
    cfg: CFG, edition: EDITION,
    getVotes: function (ed) {
      var q = "/votes?site=" + encodeURIComponent(CFG.site) + (ed ? "&edition=" + encodeURIComponent(ed) : "");
      return api(q);
    },
    myPicks: function () { return picks; }
  };
})();
