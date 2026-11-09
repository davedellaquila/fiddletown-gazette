/* Reader voting is PAUSED at the publisher's direction (Dave, Nov 8, 2026):
   "Remove the vote thumbs until we're ready to track them."
   This stub intentionally does nothing, so the live page and every archived
   snapshot (which loads ../votes.js) show no vote controls.
   TO RESTORE when Dave says tracking is ready: recover the full votes.js
   from git history (built Nov 7, 2026, commit 8d25e9c), set CFG.endpoint,
   and re-add the wiring per PUBLISHING.md. */
window.FG_VOTES_API = null;
