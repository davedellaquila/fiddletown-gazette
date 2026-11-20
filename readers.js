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
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fill); else fill();
  setInterval(fill, 300000);
})();
