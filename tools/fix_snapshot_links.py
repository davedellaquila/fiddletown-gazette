#!/usr/bin/env python3
"""Rebase a snapshot's site-root-relative URLs for life inside editions/.

Snapshots are copies of the front page, which lives at the site root; archived
under editions/, every root-relative reference (index.html, archive.html,
media/…, sky/…, icons, …) would resolve inside editions/ and 404. The archive
step runs this over the snapshot copy: in href/src/poster attributes ONLY,
a value that does not start with a scheme, //, #, ../ or / gets ../ prepended.
In-page #anchors, absolute URLs, mailto/tel and already-rebased values are
untouched. Idempotent — running it twice changes nothing the second time.

Usage: fix_snapshot_links.py editions/YYYY-MM-DD-<slot>.html [...]
"""
import re, sys
ATTR = re.compile(r'((?:href|src|poster)=")([^"]+)(")')
def needs(v):
    return v and not v.startswith(('#','/','../')) and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', v)
for path in sys.argv[1:]:
    t=open(path, encoding='utf-8').read()
    n=[0]
    def rep(m):
        if needs(m.group(2)):
            n[0]+=1
            return m.group(1)+'../'+m.group(2)+m.group(3)
        return m.group(0)
    out=ATTR.sub(rep, t)
    if out!=t:
        open(path,'w',encoding='utf-8').write(out)
    print(path, 'rebased', n[0], 'attributes')
