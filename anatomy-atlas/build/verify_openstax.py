"""Check every quote and section link against the live openstax.org pages.
Usage: verify_openstax.py <site data dir> <cache dir>"""
import glob, html, json, os, re, sys, urllib.request
OUT, CACHE = sys.argv[1], sys.argv[2]
os.makedirs(CACHE, exist_ok=True)
quotes = {}  # url -> {(text, pid, label)}


def walk(x):
    if isinstance(x, dict):
        if "text" in x and "url" in x:
            quotes.setdefault(x["url"], set()).add((x["text"], x["pid"], x["label"]))
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)


for f in glob.glob(f"{OUT}/content-*.json"):
    walk(json.load(open(f)))
src = json.load(open(f"{OUT}/sources.json"))
norm = lambda s: re.sub(r"\s+", " ", s.replace(" ", " ").replace(" ", " ")).strip()
bad = 0
for sec in src["text"]["sections"]:
    url = sec["url"]
    path = os.path.join(CACHE, url.rsplit("/", 1)[1] + ".html")
    if not os.path.exists(path):
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
            open(path, "wb").write(r.read())
    page = open(path, encoding="utf-8").read()
    title = re.search(r"<title>([^<]*)</title>", page).group(1)
    want = f'{sec["number"]} {sec["title"]}'
    title_ok = norm(html.unescape(title)).startswith(want)
    def para(pid):  # text of the live paragraph with this id, inline markup removed without adding spaces
        m = re.search(r'<p[^>]*id="%s"[^>]*>(.*?)</p>' % re.escape(pid), page, re.S)
        return norm(html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))) if m else None
    missing_q = [q for q in quotes[url] if para(q[1]) is None or norm(q[0]) not in para(q[1])]
    missing_id = sorted({q[1] for q in quotes[url] if f'id="{q[1]}"' not in page})
    print(f'{sec["number"]:5} title {"ok " if title_ok else "BAD"} quotes {len(quotes[url]) - len(missing_q)}/{len(quotes[url])} anchors missing {missing_id}  [{html.unescape(title)[:70]}]')
    for q in missing_q[:5]:
        live = para(q[1])
        print("     NOT ON LIVE PAGE:", q[1], "| ours:", q[0][:150])
        if live:
            import difflib
            sm = difflib.SequenceMatcher(None, norm(q[0]), live)
            m = max(sm.get_matching_blocks(), key=lambda b: b.size)
            print("       live:", live[max(0, m.b - 10): m.b + len(q[0]) + 20][:200])
    bad += (not title_ok) + len(missing_q) + len(missing_id)
print("problems:", bad)
json.dump({"pages": len(src["text"]["sections"]), "quotes": sum(len(v) for v in quotes.values()), "problems": bad},
          open(os.environ.get("VERIFY_OUT", "verify_openstax.json"), "w"), indent=1)
