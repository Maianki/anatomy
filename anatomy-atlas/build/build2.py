"""Heart workstation scenes: heart + great vessels (full res, vessels cropped near the heart) and a thorax context scene."""
import sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build2.py", "common.py")).read())


def named(n):
    return [p["id"] for p in atlas["parts"] if p["name"] == n]


def crop(pos, idx, ylo, yhi):
    keep = np.all((pos[idx][:, :, 1] >= ylo) & (pos[idx][:, :, 1] <= yhi), axis=1)
    return pos, idx[keep]


_geom = geom
CROP = {}


def geom(pid):  # noqa: F811  (crop the long vessels to the region around the heart)
    pos, idx = _geom(pid)
    if pid in CROP:
        pos, idx = crop(pos, idx, *CROP[pid])
    return pos, idx


HEART_GROUPS = [
    ("walls", "Chamber walls", 0xb8333a, lambda n: n.startswith("Wall of")),
    ("cavities", "Chamber cavities", 0x7d93c9, lambda n: n.startswith("Cavity of")),
    ("valves", "Valve leaflets and cusps", 0xf0e2c8, lambda n: "valve" in n),
    ("papillary", "Papillary muscles", 0xd06a5a, lambda n: "papillary" in n),
    ("coronary-arteries", "Coronary arteries", 0xff5a4a,
     lambda n: "coronary artery" in n or "conus artery" in n or "branch" in n),
    ("cardiac-veins", "Cardiac veins", 0x5a7fd6, lambda n: "vein" in n or "sinus" in n),
]
hids = elements("heart") + elements("wall of ventricle")
groups, left = [], set(hids)
for key, label, col, f in HEART_GROUPS:
    ids = [i for i in hids if i in left and f(parts[i]["name"])]
    left -= set(ids)
    groups.append({"key": key, "label": label, "color": col, "ids": ids, "keep": 1})
assert not left, [parts[i]["name"] for i in left]

ART = ["Ascending aorta", "Arch of aorta", "Descending thoracic aorta", "Pulmonary trunk",
       "Left pulmonary artery", "Right pulmonary artery"]
VEN = ["Superior vena cava", "Left inferior pulmonary vein", "Left superior pulmonary vein",
       "Right inferior pulmonary vein", "Right superior pulmonary vein"]
art = [i for n in ART for i in named(n)]
ven = [i for n in VEN for i in named(n)] + ["FJ3441"]  # thoracic segment of the inferior vena cava
CROP["FJ1931"] = (1.22, 9)
CROP["FJ3441"] = (1.20, 9)
groups.append({"key": "great-arteries", "label": "Great arteries", "color": 0xd2453f, "ids": art, "keep": 1})
groups.append({"key": "great-veins", "label": "Great veins", "color": 0x4f6fc0, "ids": ven, "keep": 1})
write_scene("heart2", groups)

# ---- thorax context ----
def inband(pid, lo=1.13, hi=1.46):
    b = parts[pid]["bounds"]
    return b[1][1] > lo and b[0][1] < hi


bone_kw = (" rib", "costal cartilage", "sternum", "Xiphoid", "thoracic vertebra", "clavicle", "scapula")
bones = [p["id"] for p in atlas["parts"] if p["system"] == "skeletal" and inband(p["id"])
         and any(k.lower() in (" " + p["name"]).lower() for k in bone_kw)]
lungs = [e for e in elements("left lung") + elements("right lung") if parts[e]["system"] == "respiratory"]
CROP.clear()
thorax = [
    {"key": "bones", "label": "Ribs, sternum and spine", "color": 0xd9d2c3, "ids": bones, "keep": 0.35},
    {"key": "lungs", "label": "Lungs", "color": 0x8fa7c4, "ids": lungs, "keep": 0.3},
    {"key": "airway", "label": "Trachea", "color": 0xb9c3cc, "ids": elements("trachea"), "keep": 0.5},
    {"key": "diaphragm", "label": "Diaphragm", "color": 0x9a6058, "ids": elements("diaphragm"), "keep": 0.4},
    {"key": "heart", "label": "Heart", "color": 0xd8434a,
     "ids": [i for i in hids if parts[i]["name"].startswith("Wall of")] + art + ven, "keep": 0.5},
]
CROP["FJ1931"] = (1.22, 9)
CROP["FJ3441"] = (1.20, 9)
write_scene("thorax", thorax)
print("bones", len(bones), sorted(set(parts[b]["name"] for b in bones))[:8])
