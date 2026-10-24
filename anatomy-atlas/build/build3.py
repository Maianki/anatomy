"""Lung workstation scene: trachea, main bronchi, segmental bronchial trees and segmental pulmonary vessels by lobe."""
import re, sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build3.py", "common.py")).read())

LOBES = [("rul", "upper lobe of right lung", 0x7fb3d5), ("rml", "middle lobe of lung", 0x9fd3a8),
         ("rll", "lower lobe of right lung", 0xe0b06c), ("lul", "upper lobe of left lung", 0xc39bd3),
         ("lll", "lower lobe of left lung", 0xe08a7a)]
SEG = re.compile(r"((?:anterior|posterior|lateral|medial) basal|apical|posterior|anterior|lateral|medial|superior) segmental|"
                 r"(superior|inferior) lingular", re.I)


def segment(name):
    m = SEG.search(name)
    if not m:
        return None
    return (m.group(1) or (m.group(2) + " lingular")).lower()


mesh_info, seen = {}, set()
for key, cname, _ in LOBES:
    for e in elements(cname):
        assert e not in seen, ("in two lobes", parts[e]["name"])
        seen.add(e)
        mesh_info[e] = {"lobe": key, "seg": segment(parts[e]["name"])}
lung_all = set(elements("left lung") + elements("right lung"))
assert lung_all == seen, (len(lung_all), len(seen))

TYPE = {"respiratory": "bronchi", "arterial": "arteries", "venous": "veins"}
groups = [
    {"key": "airway", "label": "Trachea and main bronchi", "color": 0xd7dde3,
     "ids": elements("trachea") + elements("right main bronchus") + elements("left main bronchus"), "keep": 1},
    {"key": "bronchi", "label": "Segmental bronchial trees", "color": 0xe9e2d0, "ids": [], "keep": 1},
    {"key": "arteries", "label": "Segmental pulmonary arteries", "color": 0x4f78c8, "ids": [], "keep": 1},
    {"key": "veins", "label": "Segmental pulmonary veins", "color": 0xd2453f, "ids": [], "keep": 1},
]
gi = {g["key"]: g for g in groups}
for e in sorted(seen):
    gi[TYPE[parts[e]["system"]]]["ids"].append(e)
named = lambda n: [p["id"] for p in atlas["parts"] if p["name"] == n]
groups.append({"key": "hilum-arteries", "label": "Pulmonary trunk and arteries", "color": 0x3c5fae,
               "ids": named("Pulmonary trunk") + named("Left pulmonary artery") + named("Right pulmonary artery"), "keep": 1})
groups.append({"key": "hilum-veins", "label": "Pulmonary veins", "color": 0xb8333a,
               "ids": [i for n in ["Left inferior pulmonary vein", "Left superior pulmonary vein", "Right inferior pulmonary vein",
                                   "Right superior pulmonary vein"] for i in named(n)], "keep": 1})
# Exclude meshes lying outside the region of the bronchial trees (+2 cm): these are placement errors in the data.
def box(ids):
    lo = np.min([parts[i]["bounds"][0] for i in ids], 0); hi = np.max([parts[i]["bounds"][1] for i in ids], 0)
    return lo, hi
blo, bhi = box(gi["bronchi"]["ids"] + gi["airway"]["ids"])
blo, bhi = blo - 0.02, bhi + 0.02
excluded = []
for g in groups:
    keep = []
    for i in g["ids"]:
        lo, hi = map(np.array, parts[i]["bounds"])
        if np.all(hi >= blo) and np.all(lo <= bhi):
            keep.append(i)
        else:
            excluded.append({"id": i, "name": parts[i]["name"], "fma": parts[i]["conceptId"],
                             "yRange": [round(float(lo[1]), 3), round(float(hi[1]), 3)]})
    g["ids"] = keep
print("excluded:", excluded)
write_scene("lungs", groups)

# attach lobe / segment to the manifest
meta = json.loads((OUT / "lungs.json").read_text())
for m in meta["meshes"]:
    if m["id"] in mesh_info:
        m.update(mesh_info[m["id"]])
meta["excluded"] = excluded
meta["lobes"] = [{"key": k, "label": c, "fma": concepts[c]["id"], "color": col} for k, c, col in LOBES]
(OUT / "lungs.json").write_text(json.dumps(meta, separators=(",", ":")))

import collections
segs = collections.defaultdict(lambda: collections.Counter())
for e, inf in mesh_info.items():
    segs[(inf["lobe"], inf["seg"])][parts[e]["system"]] += 1
for k in sorted(segs, key=lambda x: (x[0], str(x[1]))):
    print(k, dict(segs[k]))
print("no segment:", sorted(parts[e]["name"] for e, i in mesh_info.items() if not i["seg"]))
