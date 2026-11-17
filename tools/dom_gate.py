#!/usr/bin/env python3
"""Parsed-structure gate for The Fiddletown Gazette front page.

Dave's standing check (Nov 17, 2026) — MANDATORY on every publish.
Runs against the page as a strict tag-stack parse (NOT a browser's
error-recovering parse, NOT a text grep) and verifies:

  1. Tag balance — every container tag opened is closed in order;
     a stray or unclosed tag fails instantly (the Nov 17, 2026 stray
     </div> after the Week Ahead card is the canonical failure: the
     raw text looked fine while browsers ejected the rail).
  2. The layout grid (.grid) has exactly two element children:
     <main> then <aside>.
  3. Every rail section sits inside the <aside> — the aside must
     hold exactly the expected rail <h2> count (10) and the known
     rail section ids.

Usage: python3 tools/dom_gate.py [file-or-url ...]
Default: index.html in the repo root. Exit 0 = PASS, 1 = FAIL.
A FAIL blocks the publish announcement until fixed.
"""
import sys, urllib.request
from html.parser import HTMLParser

VOID = {"area","base","br","col","embed","hr","img","input","link","meta",
        "param","source","track","wbr","circle","path","rect","line",
        "polyline","polygon","stop","use"}

RAIL_IDS = ["around-town","community-wire","editors-desk","free-stuff",
            "carl","kathys-corner","swagger","marcis-corner",
            "more-gazette","resources"]
EXPECTED_RAIL_H2 = 10

class Node:
    __slots__ = ("tag","attrs","children","parent")
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.children, self.parent = tag, attrs, [], parent

class Gate(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node("#root", {}, None)
        self.stack = [self.root]
        self.errors = []
    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.stack[-1])
        self.stack[-1].children.append(node)
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if len(self.stack) <= 1:
            self.errors.append(f"stray closing </{tag}> with nothing open (line {self.getpos()[0]})")
            return
        if self.stack[-1].tag == tag:
            self.stack.pop()
            return
        # mismatched close: find whether the tag is open at all
        names = [n.tag for n in self.stack]
        if tag in names:
            idx = len(names) - 1 - names[::-1].index(tag)
            unclosed = [n.tag for n in self.stack[idx+1:]]
            self.errors.append(
                f"</{tag}> at line {self.getpos()[0]} closes over unclosed {unclosed}")
            del self.stack[idx:]
        else:
            self.errors.append(f"stray closing </{tag}> (line {self.getpos()[0]}) — no matching open tag")
    def close(self):
        super().close()
        if len(self.stack) > 1:
            self.errors.append(f"unclosed tags at end of file: {[n.tag for n in self.stack[1:]]}")

def walk(node):
    yield node
    for c in node.children:
        yield from walk(c)

def check(html, label):
    g = Gate()
    g.feed(html)
    g.close()
    fails = list(g.errors)
    nodes = list(walk(g.root))
    grids = [n for n in nodes if "grid" in (n.attrs.get("class") or "").split()]
    if len(grids) != 1:
        fails.append(f"expected exactly one .grid element, found {len(grids)}")
        grid = None
    else:
        grid = grids[0]
    if grid is not None:
        kids = [c.tag for c in grid.children]
        if kids != ["main", "aside"]:
            fails.append(f".grid children are {kids}, expected ['main', 'aside']")
        asides = [c for c in grid.children if c.tag == "aside"]
        if asides:
            aside = asides[0]
            inside = list(walk(aside))
            h2s = [n for n in inside if n.tag == "h2"]
            if len(h2s) != EXPECTED_RAIL_H2:
                fails.append(f"aside holds {len(h2s)} rail <h2>s, expected {EXPECTED_RAIL_H2}")
            ids_inside = {n.attrs.get("id") for n in inside}
            missing = [i for i in RAIL_IDS if i not in ids_inside]
            if missing:
                fails.append(f"rail section ids missing from the aside: {missing}")
            # and none of the rail ids may live outside the aside
            outside_ids = {n.attrs.get("id") for n in nodes if n not in inside}
            leaked = [i for i in RAIL_IDS if i in outside_ids]
            if leaked:
                fails.append(f"rail section ids found OUTSIDE the aside: {leaked}")
    if fails:
        print(f"DOM GATE FAIL — {label}")
        for f in fails:
            print(f"  ✗ {f}")
        return False
    print(f"DOM GATE PASS — {label} (tag balance OK · grid = MAIN + ASIDE · {EXPECTED_RAIL_H2} rail h2s inside the aside)")
    return True

def main():
    targets = sys.argv[1:] or ["index.html"]
    ok = True
    for t in targets:
        if t.startswith("http"):
            req = urllib.request.Request(t, headers={"User-Agent": "Mozilla/5.0 (dom-gate)"})
            html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        else:
            html = open(t, encoding="utf-8").read()
        ok = check(html, t) and ok
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
