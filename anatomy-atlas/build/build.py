"""Whole-body scene for the anatomy atlas (overview: meshes simplified by fixed ratios)."""
import sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build.py", "common.py")).read())

# ---------- body scene ----------
def sysids(s):
    return [p["id"] for p in atlas["parts"] if p["system"] == s]


ORGANS = [  # (key, FMA concept name as in the dataset, color)
    ("brain", "brain", 0xd9a7a0), ("heart", "heart", 0xb8333a), ("left-lung", "left lung", 0xd98b8b),
    ("right-lung", "right lung", 0xd98b8b), ("liver", "liver", 0x8a3b2c), ("gallbladder", "gallbladder", 0x5f8a3a),
    ("stomach", "stomach", 0xd08a6a), ("spleen", "spleen", 0x7a2f4a), ("pancreas", "pancreas", 0xe0b070),
    ("kidney", "kidney", 0x9c3f3a), ("small-intestine", "small intestine", 0xe2a487),
    ("large-intestine", "large intestine", 0xc98466), ("urinary-bladder", "urinary bladder", 0xd9b27a),
    ("esophagus", "esophagus", 0xc77b6b), ("trachea", "trachea", 0xcfd6dc), ("diaphragm", "diaphragm", 0xa2584e),
]
# Data errors found by the workstation checks (build3.py, build5.py) are left out everywhere.
# Only meshes with a data error in the source (misplaced, or name contradicting position); meshes left out of a
# workstation for other reasons (e.g. not brain tissue) stay in the body view.
used = {e["id"] for f in ("lungs.json", "brain.json") for e in json.loads((OUT / f).read_text())["excluded"] if "source data" in e["why"]}
organ_groups = []
for key, cname, col in ORGANS:
    c = concepts[cname]
    ids = [e for e in elements(cname) if e not in used]
    if key == "brain":  # same brain meshes as the brain workstation (the dataset's brain concept is incomplete)
        bj = json.loads((OUT / "brain.json").read_text())
        ids = [m["id"] for m in bj["meshes"] if m["group"] != "context" and m["id"] not in used]
    if key == "heart":
        ids += [e for e in elements("wall of ventricle") if e not in used]
    used.update(ids)
    organ_groups.append({"key": key, "label": cname, "fma": c["id"], "layer": "organs", "color": col,
                         "ids": ids, "keep": 0.17, "clickable": True})

# Bones: the regions from build6.py (dataset FMA concepts). Muscles the dataset files as skeletal (FMA: muscle organ)
# go to the muscles layer.
_sk = json.loads((OUT / "skeleton-regions.json").read_text())
SKEL = set(_sk["skeleton"])
MUSCLE_ORGAN = {e for c in atlas["concepts"] if c["name"] == "muscle organ" for e in c["elements"]}
REGION_FMA = {"skull": ["skull"], "spine": ["vertebral column"], "thorax": ["rib cage"], "upper": ["left upper limb", "right upper limb"],
              "pelvis": ["bony pelvis"], "lower": ["left lower limb", "right lower limb"]}  # the concepts build6.py builds each region from
BONE_GROUPS = []
for key, label in _sk["regions"].items():
    ids = [i for i, r in _sk["region_of"].items() if r == key and i not in used]
    BONE_GROUPS.append({"key": "bones-" + key, "label": label, "fma": ", ".join(concepts[n]["id"] for n in REGION_FMA[key]), "layer": "skeleton", "color": 0xe8e0cf,
                        "ids": ids, "keep": 0.08, "bone": True})
body = [
    {"key": "skin", "label": "Skin", "fma": concepts["skin"]["id"], "layer": "skin", "color": 0xc9a48c,
     "ids": elements("skin"), "keep": 0.17},
] + BONE_GROUPS + [
    {"key": "skeleton-other", "label": "Other meshes the dataset files under the skeletal system", "layer": "skeleton", "color": 0xe8e0cf,
     "ids": [i for i in sysids("skeletal") if i not in used and i not in SKEL and i not in MUSCLE_ORGAN], "keep": 0.08},
    {"key": "muscles", "label": "Muscles", "layer": "muscles", "color": 0xa8474a,
     "ids": [i for i in sysids("muscular") + [j for j in sysids("skeletal") if j in MUSCLE_ORGAN] if i not in used], "keep": 0.04},
    {"key": "arteries", "label": "Arteries", "layer": "vessels", "color": 0xc62f36,
     "ids": [i for i in sysids("arterial") if i not in used], "keep": 0.1},
    {"key": "veins", "label": "Veins", "layer": "vessels", "color": 0x3d5fa8,
     "ids": [i for i in sysids("venous") if i not in used], "keep": 0.1},
    {"key": "nerves", "label": "Nervous system", "layer": "nerves", "color": 0xe6c45a,
     "ids": [i for i in sysids("nervous") if i not in used and i not in elements("brain")], "keep": 0.1},
] + organ_groups
write_scene("body", body)

