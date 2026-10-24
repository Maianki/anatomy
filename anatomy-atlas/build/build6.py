"""Bone workstations: skull, vertebral column, thoracic cage, upper limbs, pelvis, lower limbs, plus a skeleton context.

A mesh counts as part of the skeleton if the dataset's FMA hierarchy calls it a bone organ, or it is a part of the
sternum, a costal cartilage or an intervertebral disk. (The dataset's "system" field is not used: it files some
muscles and fascia as skeletal and some bones as sensory or respiratory.)
Each region is the dataset's own FMA concept for it. Inside a region, bones are grouped by the OpenStax section
whose heading names them (see BONE_SECTIONS); the build fails if a bone matches no section or two.
"""
import re, sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build6.py", "common.py")).read())


def cel(name):
    return {e for c in atlas["concepts"] if c["name"] == name for e in c["elements"] if e in parts}


SKELETON = cel("bone organ") | cel("costal cartilage") | cel("intervertebral disk") | \
    {p["id"] for p in atlas["parts"] if p["name"] in ("Body of sternum", "Manubrium", "Xiphoid process")}
bare = lambda pid: re.sub(r"^(Left|Right) ", "", parts[pid]["name"])

REGIONS = [  # key, label, dataset concepts, extra rule
    ("skull", "Skull", ["skull"]),
    ("spine", "Vertebral column", ["vertebral column"]),
    ("thorax", "Thoracic cage", ["rib cage"]),
    ("upper", "Upper limbs", ["left upper limb", "right upper limb"]),
    ("pelvis", "Pelvis", ["bony pelvis"]),
    ("lower", "Lower limbs", ["left lower limb", "right lower limb"]),
]
# (region, group key, label = OpenStax section heading, section number, rule on the bare dataset name)
BONE_SECTIONS = [
    ("skull", "braincase", "Bones of the Brain Case", "7.2", lambda n: re.search(r"^(parietal|temporal|Frontal|Occipital|Sphenoid) bone$|^Ethmoid$", n, re.I)),
    ("skull", "facial", "Facial Bones of the Skull", "7.2", lambda n: re.search(r"^(maxilla|palatine bone|zygomatic bone|nasal bone|lacrimal bone|inferior nasal concha|Vomer|Mandible)$", n, re.I)),
    ("skull", "hyoid", "Hyoid Bone", "7.2", lambda n: n == "Hyoid bone"),
    ("spine", "cervical", "Cervical Vertebrae", "7.3", lambda n: re.search(r"^(Atlas|Axis)$|^\w+ cervical vertebra$", n)),
    ("spine", "thoracic", "Thoracic Vertebrae", "7.3", lambda n: re.search(r"^\w+ thoracic vertebra$", n)),
    ("spine", "lumbar", "Lumbar Vertebrae", "7.3", lambda n: re.search(r"^\w+ lumbar vertebra$", n)),
    ("spine", "sacrum", "Sacrum and Coccyx", "7.3", lambda n: n == "Sacrum"),
    ("spine", "disc", "Intervertebral Disc", "7.3", lambda n: n.startswith("Intervertebral disk")),
    ("thorax", "sternum", "Sternum", "7.4", lambda n: n in ("Body of sternum", "Manubrium", "Xiphoid process")),
    ("thorax", "ribs", "Ribs", "7.4", lambda n: re.search(r"^\w+ rib$", n)),
    ("thorax", "cartilage", "Costal cartilages", "7.4", lambda n: n.endswith("costal cartilage")),
    ("upper", "clavicle", "Clavicle", "8.1", lambda n: n == "clavicle"),
    ("upper", "scapula", "Scapula", "8.1", lambda n: n == "scapula"),
    ("upper", "humerus", "Humerus", "8.2", lambda n: n == "humerus"),
    ("upper", "ulna", "Ulna", "8.2", lambda n: n == "ulna"),
    ("upper", "radius", "Radius", "8.2", lambda n: n == "radius"),
    ("upper", "carpal", "Carpal Bones", "8.2", lambda n: n in ("scaphoid", "lunate", "triquetral", "pisiform", "trapezium", "trapezoid", "capitate", "hamate")),
    ("upper", "metacarpal", "Metacarpal Bones", "8.2", lambda n: n.endswith("metacarpal bone")),
    ("upper", "phalanx", "Phalanx Bones", "8.2", lambda n: re.search(r"phalanx of (left|right) (thumb|index|middle|ring|little)", n)),
    ("pelvis", "hip", "Hip Bone", "8.3", lambda n: n == "hip bone"),
    ("pelvis", "sacrum", "Sacrum", "7.3", lambda n: n == "Sacrum"),
    ("lower", "femur", "Femur", "8.4", lambda n: n == "femur"),
    ("lower", "patella", "Patella", "8.4", lambda n: n == "patella"),
    ("lower", "tibia", "Tibia", "8.4", lambda n: n == "tibia"),
    ("lower", "fibula", "Fibula", "8.4", lambda n: n == "fibula"),
    ("lower", "tarsal", "Tarsal Bones", "8.4", lambda n: re.search(r"^(calcaneus|talus|cuboid bone|(intermediate|lateral|medial) cuneiform bone|Navicular bone of (left|right) foot)$", n)),
    ("lower", "metatarsal", "Metatarsal Bones", "8.4", lambda n: n.endswith("metatarsal bone")),
    ("lower", "phalanges", "Phalanges", "8.4", lambda n: re.search(r"phalanx of (left|right) (big|second|third|fourth|little) toe", n)),
    ("lower", "sesamoid", "Sesamoid bones of the foot", "8.4", lambda n: re.search(r"^Sesamoid bone of (left|right) foot$", n)),
]
COLORS = [0xe8dcc4, 0xd9c7a3, 0xc9b38a, 0xe6cfa8, 0xd4bf98, 0xbfae8f, 0xf0e3c8, 0xcdb894]
EXCLUDE_FROM_LOWER = {"hip bone"}  # shown in the Pelvis workstation, as in OpenStax 8.3
region_of = {}
summary = {}
for key, label, concepts_ in REGIONS:
    pool = set().union(*[cel(c) for c in concepts_]) & SKELETON
    if key == "lower":
        pool = {i for i in pool if bare(i) not in EXCLUDE_FROM_LOWER} | {p["id"] for p in atlas["parts"] if re.search(r"^Sesamoid bone of (left|right) foot$", p["name"])}
    secs = [s for s in BONE_SECTIONS if s[0] == key]
    groups = [{"key": g, "label": lab, "section": num, "color": COLORS[i % len(COLORS)], "ids": [], "keep": "auto"} for i, (_, g, lab, num, _) in enumerate(secs)]
    for pid in sorted(pool):
        hits = [gi for gi, s in enumerate(secs) if s[4](bare(pid))]
        assert len(hits) == 1, (key, parts[pid]["name"], hits)
        groups[hits[0]]["ids"].append(pid)
        region_of.setdefault(pid, key)
    groups = [g for g in groups if g["ids"]]
    write_scene("bones-" + key, groups)
    summary[key] = {g["label"]: len(g["ids"]) for g in groups}
print(summary)
left = sorted(set(bare(i) for i in SKELETON if i not in region_of))
print("skeleton meshes in no region:", left)

# skeleton context for the picture-in-picture view
write_scene("skeleton", [{"key": k, "label": lab, "color": 0xd9d2c3, "keep": 0.08,
                          "ids": sorted(i for i, r in region_of.items() if r == k)} for k, lab, _ in REGIONS] +
            [{"key": "other", "label": "Other", "color": 0xd9d2c3, "keep": 0.08, "ids": sorted(i for i in SKELETON if i not in region_of)}])
(OUT / "skeleton-regions.json").write_text(json.dumps({"regions": {k: lab for k, lab, _ in REGIONS},
                                                       "skeleton": sorted(SKELETON), "region_of": region_of}))
