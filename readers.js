/* Reader counts, today / all-time — The Fiddletown Gazette (Dave's format,
   Thu Nov 20, 2026): the masthead and the sticky topbar show the reader
   count as "today / all-time" instead of one bare total. Filled from the
   same visitor-counter Worker as the beacon (GET /counts returns both
   figures per path). The numbers are also baked into the spans by
   tools/forecast_panel.py on every edition run, so a reader whose browser
   blocks this script still sees the edition-time figures. The colophon's
   sentence-form count keeps the beacon-filled [data-visitor-count] span —
   this script deliberately does not touch it. */
(function () {
  "use strict";
  var ENDPOINT = "https://visitor-counter.dave-5d7.workers.dev";
  var PATH = "/fiddletown-gazette/";

  function fill() {
    fetch(ENDPOINT + "/counts?site=fiddletown-gazette&paths=" + encodeURIComponent(PATH))
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (res) {
        if (!res || !res.counts || !res.counts[PATH]) return;
        var c = res.counts[PATH];
        Array.prototype.forEach.call(document.querySelectorAll("[data-rc-today]"), function (el) {
          el.textContent = c.today;
        });
        Array.prototype.forEach.call(document.querySelectorAll("[data-rc-total]"), function (el) {
          el.textContent = c.total;
        });
      })
      .catch(function () { /* baked figures stand */ });
  }
  /* Explainer tooltip (Dave, Nov 20, 2026): the title attribute covers
     hover; on touch, tapping either count toggles a small note beside it
     spelling out what the two numbers mean. */
  var TIP_TEXT = "Readers today / readers all-time: the first number is how many readers have visited today; the second is the all-time total since counting began on Nov 15, 2026. If the readers-today number is showing in red, you’re being counted for the first time today — you are that reader. Each reader counts once a day, by a scrambled code that is discarded nightly — no names, no tracking, just the count.";
  function setupTip() {
    var spots = document.querySelectorAll(".readers, .tb-readers");
    if (!spots.length) return;
    var st = document.createElement("style");
    st.textContent =
      "#fg-rc-tip{position:fixed;z-index:9997;max-width:290px;background:#2b2118;color:#f5ead2;" +
      "font:13px/1.5 -apple-system,system-ui,'Segoe UI',Roboto,sans-serif;padding:9px 12px;" +
      "border-radius:9px;box-shadow:0 4px 18px rgba(0,0,0,.35)}" +
      ".readers,.tb-readers{cursor:pointer}";
    document.head.appendChild(st);
    var tip = document.createElement("div");
    tip.id = "fg-rc-tip"; tip.hidden = true; tip.textContent = TIP_TEXT;
    document.body.appendChild(tip);
    var hideTimer = null;
    function hide() { tip.hidden = true; if (hideTimer) clearTimeout(hideTimer); }
    function toggle(anchor) {
      if (!tip.hidden) { hide(); return; }
      var r = anchor.getBoundingClientRect();
      tip.hidden = false;
      var x = Math.max(8, Math.min(r.left, window.innerWidth - 306));
      tip.style.left = x + "px";
      tip.style.top = (r.bottom + 8) + "px";
      hideTimer = setTimeout(hide, 7000);
    }
    Array.prototype.forEach.call(spots, function (el) {
      el.addEventListener("click", function (ev) { ev.stopPropagation(); toggle(el); });
    });
    document.addEventListener("click", function () { if (!tip.hidden) hide(); });
  }

  /* First-visit red (Dave, Sat Nov 21, 2026): when this visitor's arrival
     is the one that incremented today's count, Analytics Buddy's beacon
     adds the class "vc-new-today" to <html> (and fires "vc:counted" /
     sets window.vcCounted). Both today numbers — the masthead's (.readers)
     and the sticky topbar pair's (.tb-readers) — then show in the paper's
     accent red: "you are the Nth reader today." (Extended to both counters
     at Dave's direction, Mon Nov 23, 2026; originally masthead only.)
     The class is set once per page load and never removed, so the red
     sticks for the visit while fill() refreshes the number beneath it. */
  function setupNewToday() {
    var st = document.createElement("style");
    st.id = "fg-new-today-style";
    st.textContent = "html.vc-new-today .readers [data-rc-today],html.vc-new-today .tb-readers [data-rc-today]{color:var(--accent)}";
    document.head.appendChild(st);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { fill(); setupTip(); setupNewToday(); });
  else { fill(); setupTip(); setupNewToday(); }
  setInterval(fill, 300000);
})();
