"""Abdominal workstation scenes: liver/gallbladder/pancreas, digestive tract, urinary system, and the abdomen context.

Every mesh is picked by its dataset name or FMA concept, and every pool of candidate meshes must be
assigned to exactly one group (the script fails otherwise), so nothing is silently dropped or doubled.
"""
import re, sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build4.py", "common.py")).read())

byname = {}
for p in atlas["parts"]:
    byname.setdefault(p["name"], []).append(p["id"])


def named(*names):
    out = []
    for n in names:
        assert n in byname, n
        out += byname[n]
    return out


def like(pattern, system=None):
    r = re.compile(pattern, re.I)
    return [p["id"] for p in atlas["parts"] if r.search(p["name"]) and (system is None or p["system"] == system)]


def assign(pool, rules):
    """rules: list of (group dict, predicate on part). Each pool id must match exactly one rule."""
    pool = list(dict.fromkeys(pool))
    for g, _ in rules:
        g.setdefault("ids", [])
    for i in pool:
        hits = [g for g, f in rules if f(parts[i])]
        assert len(hits) == 1, (parts[i]["name"], [g["key"] for g in hits])
        hits[0]["ids"].append(i)
    return [g for g, _ in rules]


def nm(*subs):
    return lambda p: any(s in p["name"] for s in subs)


# ---------------- liver, gallbladder, pancreas ----------------
SEGMENTS = ["Caudate lobe of liver"] + ["Hepatovenous segment " + r for r in ["II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]]
liver_pool = elements("liver") + named("Hepatovenous segment IX", "Middle hepatic vein", "Hepatic portal vein", "Common hepatic artery",
                                       "Common hepatic duct", "Cystic duct", "Gallbladder", "Pancreas", "Parenchyma of pancreas",
                                       "Pancreatic duct", "Pancreatic duct tree", "Duodenum", "Inferior vena cava") \
    + like(r"tributary of (middle|right|left) hepatic vein")
liver_groups = assign(liver_pool, [
    ({"key": "segments", "label": "Liver segments", "color": 0x9c4a3c}, lambda p: p["name"] in SEGMENTS),
    ({"key": "portal", "label": "Portal veins", "color": 0x6a5fc0}, nm("portal vein")),
    ({"key": "arteries", "label": "Hepatic arteries", "color": 0xd84a3f}, nm("hepatic artery", "Hepatic artery proper")),
    ({"key": "hveins", "label": "Hepatic veins", "color": 0x4f78c8}, nm("hepatic vein")),
    ({"key": "biliary", "label": "Bile ducts", "color": 0x8fbf5a}, nm("biliary tree", "hepatic duct", "Cystic duct", "duct of caudate lobe")),
    ({"key": "gallbladder", "label": "Gallbladder", "color": 0x5f9a3a}, nm("Gallbladder")),
    ({"key": "pancreas", "label": "Pancreas", "color": 0xe0b070}, lambda p: p["name"] == "Pancreas"),
    ({"key": "pancreas-parenchyma", "label": "Parenchyma of pancreas (same surface)", "color": 0xd9a35f}, nm("Parenchyma of pancreas")),
    ({"key": "pduct-tree", "label": "Pancreatic duct tree", "color": 0xf2d48a}, nm("Pancreatic duct tree")),
    ({"key": "pduct", "label": "Pancreatic duct (overlaps duct tree)", "color": 0xf7e2a8}, lambda p: p["name"] == "Pancreatic duct"),
    ({"key": "duodenum", "label": "Duodenum (context)", "color": 0xe2a487}, nm("Duodenum")),
    ({"key": "ivc", "label": "Inferior vena cava (context)", "color": 0x3d5fa8}, nm("Inferior vena cava")),
])
for g in liver_groups:
    g["keep"] = "auto"
write_scene("liver", liver_groups)
seg_colors = [0xb07a5a, 0x7fb3d5, 0x9fd3a8, 0xe0b06c, 0xc39bd3, 0xe08a7a, 0x8fc7c0, 0xd6c27a, 0xa6a6d9]
meta = json.loads((OUT / "liver.json").read_text())
keys = {n: re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-") for n in SEGMENTS}
for m in meta["meshes"]:
    if m["name"] in keys:
        m["lobe"] = keys[m["name"]]
meta["lobes"] = [{"key": keys[n], "label": n, "fma": parts[byname[n][0]]["conceptId"], "color": c} for n, c in zip(SEGMENTS, seg_colors)]
(OUT / "liver.json").write_text(json.dumps(meta, separators=(",", ":")))

# ---------------- digestive tract ----------------
GUT_VESSEL_RX = r"mesenteric|\bgastric|gastro-?epiploic|colic|ileocolic|jejunal|ileal|sigmoid|rectal|appendicular|pancreaticoduodenal|esophageal (artery|vein)"
GUT_VESSELS = like(GUT_VESSEL_RX, "arterial") + like(GUT_VESSEL_RX, "venous")
gut_pool = named("Esophagus", "Stomach", "Duodenum", "Ileocecal junction", "Appendix", "Mesoappendix", "Ascending colon",
                 "Transverse colon", "Descending colon", "Rectum", "Taenia libera", "Taenia mesocolica", "Taenia omentalis",
                 "Mesentery of small intestine", "Transverse mesocolon") + like(r"part of (jejunum|ileum)$") + GUT_VESSELS
gut_groups = assign(gut_pool, [
    ({"key": "esophagus", "label": "Esophagus", "color": 0xc77b6b}, lambda p: p["name"] == "Esophagus"),
    ({"key": "stomach", "label": "Stomach", "color": 0xd08a6a}, nm("Stomach")),
    ({"key": "duodenum", "label": "Duodenum", "color": 0xe6b48f}, nm("Duodenum")),
    ({"key": "jejunum", "label": "Jejunum", "color": 0xe9a07e}, nm("jejunum")),
    ({"key": "ileum", "label": "Ileum", "color": 0xd98f9a}, nm("ileum")),
    ({"key": "large", "label": "Large intestine", "color": 0xb98a5e}, lambda p: p["name"] in ("Ascending colon", "Transverse colon", "Descending colon", "Rectum", "Appendix", "Ileocecal junction")),
    ({"key": "teniae", "label": "Teniae coli", "color": 0xf0dfb8}, nm("Taenia")),
    ({"key": "mesenteries", "label": "Mesenteries", "color": 0xe8d6a0}, nm("Mesentery", "mesocolon", "Mesoappendix")),
    ({"key": "gut-arteries", "label": "Arteries of the digestive tract", "color": 0xd84a3f}, lambda p: p["id"] in GUT_VESSELS and p["system"] == "arterial"),
    ({"key": "gut-veins", "label": "Veins of the digestive tract", "color": 0x4f78c8}, lambda p: p["id"] in GUT_VESSELS and p["system"] == "venous"),
])
for g in gut_groups:
    g["keep"] = "auto"
gut_groups.append({"key": "accessory", "label": "Liver, pancreas, gallbladder, spleen (context)", "color": 0x8a4a3c,
                   "ids": [i for n in SEGMENTS for i in byname[n]] + named("Pancreas", "Gallbladder", "Spleen"), "keep": 0.17})
write_scene("gut", gut_groups)

# ---------------- urinary system ----------------
uri_pool = named("Left kidney", "Right kidney", "Left ureter", "Right ureter", "Urinary bladder", "Urethra", "Prostate",
                 "Left adrenal gland", "Right adrenal gland", "Abdominal aorta", "Inferior vena cava") \
    + like(r"renal artery", "arterial") + like(r"renal vein", "venous")
uri_groups = assign(uri_pool, [
    ({"key": "kidneys", "label": "Kidneys", "color": 0x9c3f3a}, nm("kidney")),
    ({"key": "ureters", "label": "Ureters", "color": 0xe0c27a}, nm("ureter")),
    ({"key": "bladder", "label": "Urinary bladder", "color": 0xd9b27a}, nm("Urinary bladder")),
    ({"key": "urethra", "label": "Urethra", "color": 0xf0d9a8}, nm("Urethra")),
    ({"key": "renal-arteries", "label": "Renal arteries", "color": 0xd84a3f}, nm("renal artery")),
    ({"key": "renal-veins", "label": "Renal veins", "color": 0x4f78c8}, nm("renal vein")),
    ({"key": "great", "label": "Abdominal aorta and inferior vena cava (context)", "color": 0x8a6a7a}, nm("Abdominal aorta", "Inferior vena cava")),
    ({"key": "adrenal", "label": "Adrenal glands (context)", "color": 0xc9a35a}, nm("adrenal")),
    ({"key": "prostate", "label": "Prostate (context)", "color": 0xa98ab0}, nm("Prostate")),
])
for g in uri_groups:
    g["keep"] = "auto"
write_scene("urinary", uri_groups)

# ---------------- abdomen context ----------------
def inband(pid, lo, hi):
    b = parts[pid]["bounds"]
    return b[1][1] > lo and b[0][1] < hi


bone_kw = (" rib", "costal cartilage", "Xiphoid", "lumbar vertebra", "thoracic vertebra", "sacrum", "coccyx", "hip bone", "Sacrum", "Coccyx")
bones = [p["id"] for p in atlas["parts"] if p["system"] == "skeletal" and inband(p["id"], 0.82, 1.3)
         and any(k.lower() in (" " + p["name"]).lower() for k in bone_kw)]
ctx = [
    {"key": "bones", "label": "Ribs, spine and pelvis", "color": 0xd9d2c3, "ids": bones, "keep": 0.12},
    {"key": "liver", "label": "Liver, gallbladder, pancreas", "color": 0xa0503f,
     "ids": [i for n in SEGMENTS for i in byname[n]] + named("Gallbladder", "Pancreas"), "keep": 0.17},
    {"key": "gut", "label": "Digestive tract", "color": 0xd99a7a, "ids": [i for g in gut_groups[:6] for i in g["ids"]], "keep": 0.1},
    {"key": "urinary", "label": "Urinary system", "color": 0xc9a35a,
     "ids": named("Left kidney", "Right kidney", "Left ureter", "Right ureter", "Urinary bladder", "Urethra"), "keep": 0.2},
    {"key": "spleen", "label": "Spleen", "color": 0x7a2f4a, "ids": named("Spleen"), "keep": 0.2},
]
write_scene("abdomen", ctx)
print("abdomen bones:", len(bones), sorted(set(parts[b]["name"] for b in bones))[:10])
