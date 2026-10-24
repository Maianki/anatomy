"""Female body, female reproductive workstation and female pelvis, from the Human Reference Atlas (HRA).

Source: HRA 3D Reference Object Library (HuBMAP), files from github.com/hubmapconsortium/ccf-releases (env HRA_DIR,
a checkout of that repository). Only models whose own metadata says they were made from the Visible Human Female
are used, so the female body is one person, like the male body. Each model's metadata (licence CC BY 4.0, DOI,
creators, description) is read from the release's markdown file and written to hra-sources.json. Names and
ontology IDs come from the release's crosswalk table (asct-b-3d-models-crosswalk.csv); a mesh missing from it keeps
its node name. The organs share one body frame in metres (+X patient left, +Y up, +Z front, checked against the
heart and spinal cord), so the only change is a vertical shift that puts the feet at y = 0, as in the male body.
"""
import csv, re, sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build8.py", "common.py")).read())
import glb

HRA = Path(os.environ["HRA_DIR"])
MODELS = HRA / "v1.2" / "models"   # the files the v1.3 metadata links to ("3D Data")
FILES = ["Skin", "Pelvis", "Knee_L", "Knee_R", "Heart", "Lung", "Liver", "Pancreas", "Spleen", "Kidney_L", "Kidney_R",
         "Ureter_L", "Ureter_R", "Urinary_Bladder", "Small_Intestine", "Thymus", "Spinal_Cord", "Eye_L", "Eye_R",
         "Blood_Vasculature", "Uterus", "Fallopian_Tube_L", "Fallopian_Tube_R", "Ovary_L", "Ovary_R"]
# Left out, with the reason shown on the Sources page and in DECISIONS:
LEFT_OUT = {"VH_F_Placenta.glb": "A full-term placenta belongs to pregnancy; this body is shown as not pregnant.",
            "SBU_F_Intestine_Large.glb": "Made from Stony Brook University data as a custom sculpted model, not from the Visible Human Female.",
            "Allen_F_Brain.glb": "Made from the Allen Human Reference Atlas, not from the Visible Human Female."}

# ---- metadata of each file, from the release markdown (latest version that has it) ----
meta_md = {}
for md in sorted(HRA.glob("v1.*/markdown/ref-organs/*.md"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.parts[-4])]):
    t = md.read_text(encoding="utf-8")
    m = re.search(r"\*\*3D Data:\*\*\s*\|\s*\[([^\]]+)\]\(([^)]+)\)", t)
    if not m:
        continue
    row = lambda k: (re.search(r"\*\*%s:\*\*\s*\|\s*(.*?)\s*\|\s*$" % re.escape(k), t, re.M) or [None, ""])[1]
    meta_md[m.group(2).rsplit("/", 1)[1]] = {
        "title": t.splitlines()[0].lstrip("# ").strip(), "data": m.group(1), "url": m.group(2), "markdown": str(md.relative_to(HRA)),
        "description": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t.split("### Description", 1)[1].split("|", 1)[0]).strip(),
        "creators": row("Creator(s)"), "reviewers": row("Reviewer(s)"), "date": row("Date"), "license": re.sub(r"\s*\(\[.*", "", row("License")),
        "doi": re.sub(r"^\[([^\]]+)\].*", r"\1", row("DOI")), "cite": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", row("How to Cite This 3D Data")).replace("*", "")}
src = {}
for f in FILES:
    k = f"VH_F_{f}.glb"
    m = meta_md[k]
    assert m["license"].startswith("Creative Commons Attribution 4.0"), (k, m["license"])
    assert "Visible Human" in m["description"], (k, m["description"])
    src[k] = m
for k in LEFT_OUT:
    assert k in meta_md, k

# ---- names and IDs from the crosswalk ----
cw = {}
for r in csv.reader(open(HRA / "v2.0" / "models" / "asct-b-3d-models-crosswalk.csv", encoding="utf-8-sig")):
    if len(r) > 4 and r[2].startswith("VH_F_") and r[3] not in ("", "-"):
        cw.setdefault(r[2], (r[3], r[4]))

# ---- load geometry ----
def weld(pos, idx):
    """Merge vertices at exactly the same position (some files, such as the skin, store every triangle with its own
    corners). The surface is unchanged; without this, simplification would break the mesh apart."""
    uniq, inv = np.unique(pos.astype(np.float32), axis=0, return_inverse=True)
    tri = inv.reshape(-1)[idx]
    tri = tri[(tri[:, 0] != tri[:, 1]) & (tri[:, 1] != tri[:, 2]) & (tri[:, 0] != tri[:, 2])]
    return uniq.astype(np.float32), tri.astype(np.uint32)



human = lambda n: re.sub(r"^VH_F_", "", n).replace("_", " ")
HIP = re.compile(r"^VH_F_(ilium|ischium|pubis)_(compact|spongy)_bone_([LR])$")
GEOM, FILE_OF = {}, {}
for f in FILES:
    ms = glb.meshes(MODELS / f"VH_F_{f}.glb")
    labels = [cw.get(n, ("", ""))[0] for n, *_ in ms]
    for node, _, pos, idx in ms:
        pid = "HRA:" + node
        assert pid not in GEOM, pid
        label, oid = cw.get(node, (human(node), ""))
        h = HIP.match(node)
        if h:  # the crosswalk maps these to a tissue ("Compact bone tissue"), which would hide the bone and side
            label, oid = f"{'Left' if h[3] == 'L' else 'Right'} {h[1]} ({h[2]} bone)", ""
        elif labels.count(label) > 1:  # two meshes share a crosswalk label: use their own node names
            label, oid = human(node), oid
        parts[pid] = {"id": pid, "name": label[:1].upper() + label[1:], "conceptId": oid.replace("FMA:", "FMA"), "node": node}
        GEOM[pid] = weld(pos, idx)
        FILE_OF[pid] = f"VH_F_{f}.glb"
floor = min(GEOM[p][0][:, 1].min() for p in GEOM if FILE_OF[p] == "VH_F_Skin.glb")
for p, (pos, idx) in GEOM.items():
    pos = pos.copy()
    pos[:, 1] -= floor
    GEOM[p] = (pos, idx)
_official_geom = geom


def geom(pid):
    return GEOM[pid] if pid in GEOM else _official_geom(pid)


def of(*files):
    return [p for p in GEOM if FILE_OF[p] in {f"VH_F_{f}.glb" for f in files}]


node = lambda p: parts[p]["node"]


def where(pool, pattern):
    r = re.compile(pattern, re.I)
    return [p for p in pool if r.search(node(p))]


def assign(pool, rules):
    """Every mesh in the pool must match exactly one rule."""
    out = [dict(g, ids=[]) for g, _ in rules]
    for p in pool:
        hits = [i for i, (_, pat) in enumerate(rules) if re.search(pat, node(p), re.I)]
        assert len(hits) == 1, (node(p), [rules[i][0]["key"] for i in hits])
        out[hits[0]]["ids"].append(p)
    for g in out:
        assert g["ids"], g["key"]
    return out


def tag(name):
    """Record each mesh's source file in the scene manifest (for the per-part credit line)."""
    p = OUT / f"{name}.json"
    m = json.loads(p.read_text())
    for x in m["meshes"]:
        if x["id"] in FILE_OF:
            x["src"] = FILE_OF[x["id"]]
    m["source"] = "Human Reference Atlas 3D Reference Object Library (Visible Human Female)"
    p.write_text(json.dumps(m, separators=(",", ":")))


VEIN = r"vein|vena_cava|coronary_sinus"
vessels = of("Blood_Vasculature")
assert all(re.search(VEIN + r"|arter|aort|trunk|branch", node(p)) for p in vessels), [node(p) for p in vessels if not re.search(VEIN + r"|arter|aort|trunk|branch", node(p))]
lung = of("Lung")
hip = of("Pelvis")
knee = of("Knee_L", "Knee_R")

# ---------------- female body ----------------
body = [
    {"key": "skin", "label": "Skin", "fma": parts["HRA:VH_F_skin"]["conceptId"], "layer": "skin", "color": 0xc9a48c, "ids": of("Skin"), "keep": 0.17},
    {"key": "bones-pelvis", "label": "Pelvis", "fma": "", "layer": "skeleton", "color": 0xe8e0cf, "bone": True, "keep": 0.12,
     "ids": [p for p in hip if "spongy" not in node(p)]},
    {"key": "bones-lower", "label": "Lower limbs (femur, patella, tibia, fibula)", "fma": "", "layer": "skeleton", "color": 0xe8e0cf, "bone": True, "keep": 0.12,
     "ids": where(knee, r"_(femur|patella|tibia|fibula)_[LR]$")},
    {"key": "arteries", "label": "Arteries", "layer": "vessels", "color": 0xc62f36, "ids": [p for p in vessels if not re.search(VEIN, node(p))], "keep": 0.2},
    {"key": "veins", "label": "Veins", "layer": "vessels", "color": 0x3d5fa8, "ids": [p for p in vessels if re.search(VEIN, node(p))], "keep": 0.2},
    {"key": "nerves", "label": "Spinal cord", "layer": "nerves", "color": 0xe6c45a, "ids": of("Spinal_Cord"), "keep": 0.3},
]
ORG = [  # key, label, colour, mesh ids
    ("heart", "heart", 0xb8333a, of("Heart")),
    ("left-lung", "left lung", 0xd98b8b, where(lung, r"^VH_F_((left|lingula)_.*bronchopulmonary_segm|hilum(_upper|_lower)?_L$)")),
    ("right-lung", "right lung", 0xd98b8b, where(lung, r"^VH_F_(right_.*bronchopulmonary_segm|hilum(_upper|_middle|_lower)?_R$)")),
    ("trachea", "trachea, bronchi and larynx", 0xcfd6dc, where(lung, r"bronchus|bronchi$|trachea|carina|cartilage")),
    ("liver", "liver", 0x8a3b2c, of("Liver")), ("pancreas", "pancreas", 0xe0b070, of("Pancreas")), ("spleen", "spleen", 0x7a2f4a, of("Spleen")),
    ("kidney", "kidney", 0x9c3f3a, of("Kidney_L", "Kidney_R")), ("ureter", "ureter and renal pelvis", 0xc9a35a, of("Ureter_L", "Ureter_R")),
    ("urinary-bladder", "urinary bladder", 0xd9b27a, of("Urinary_Bladder")), ("small-intestine", "small intestine", 0xe2a487, of("Small_Intestine")),
    ("thymus", "thymus", 0xc9a0a0, of("Thymus")), ("eye", "eye", 0xd8d8e0, of("Eye_L", "Eye_R")),
    ("uterus", "uterus", 0xd98a9a, where(of("Uterus"), r"^(?!.*abdominal_ostium)")),
    ("uterine-tube", "uterine tube", 0xe0a8b0, of("Fallopian_Tube_L", "Fallopian_Tube_R") + where(of("Uterus"), r"abdominal_ostium")),
    ("ovary", "ovary", 0xe8c49a, of("Ovary_L", "Ovary_R")),
]
lung_ids = {p for k, _, _, ids in ORG if k in ("left-lung", "right-lung", "trachea") for p in ids}
assert lung_ids == set(lung) and sum(len(ids) for k, _, _, ids in ORG if k in ("left-lung", "right-lung", "trachea")) == len(lung)
for k, lab, col, ids in ORG:
    ids_f = sorted(set(ids))
    body.append({"key": k, "label": lab, "fma": "", "layer": "organs", "color": col, "ids": ids_f, "keep": 0.17, "clickable": True})
used = {p for g in body for p in g["ids"]}
unused = sorted(node(p) for p in GEOM if p not in used and not ("spongy" in node(p)) and FILE_OF[p] not in ("VH_F_Knee_L.glb", "VH_F_Knee_R.glb"))
assert not unused, unused
write_scene("body-f", body)
tag("body-f")

# ---------------- female reproductive workstation ----------------
repro = assign(of("Uterus", "Fallopian_Tube_L", "Fallopian_Tube_R", "Ovary_L", "Ovary_R", "Urinary_Bladder") + where(vessels, r"uterine"), [
    ({"key": "uterus", "label": "Uterus: fundus, body and walls", "color": 0xd98a9a}, r"fundus_of_uterus|body_of_uterus|cornua|uterine_segment|wall_of_uterus"),
    ({"key": "cervix", "label": "Cervix", "color": 0xc07a8a}, r"cervi"),
    ({"key": "tubes", "label": "Uterine tubes", "color": 0xe0a8b0}, r"uterine_tube|fallopian|fibria"),
    ({"key": "ovaries", "label": "Ovaries", "color": 0xe8c49a}, r"ovary"),
    ({"key": "great-uarteries", "label": "Uterine arteries", "color": 0xc62f36}, r"uterine_artery"),
    ({"key": "great-uveins", "label": "Uterine veins", "color": 0x3d5fa8}, r"uterine_vein"),
    ({"key": "bladder", "label": "Urinary bladder (context)", "color": 0xd9b27a}, r"bladder|ureteral_orifice|trigone"),
])
for g in repro:
    g["keep"] = "auto"
write_scene("repro-female", repro)
tag("repro-female")
print({g["label"]: len(g["ids"]) for g in repro})

# ---------------- female pelvis (bones) ----------------
pel = assign(hip, [
    ({"key": "ilium", "label": "Ilium", "color": 0xe8dcc4}, r"ilium_compact"),
    ({"key": "ischium", "label": "Ischium", "color": 0xd9c7a3}, r"ischium_compact"),
    ({"key": "pubis", "label": "Pubis", "color": 0xc9b38a}, r"pubis_compact"),
    ({"key": "sacrum", "label": "Sacrum", "color": 0xe6cfa8}, r"sacrum"),
    ({"key": "coccyx", "label": "Coccyx", "color": 0xd4bf98}, r"coccyx"),
    ({"key": "spongy", "label": "Spongy bone (inside the hip bone)", "color": 0xbfae8f}, r"spongy"),
])
for g in pel:
    g["keep"] = "auto"
write_scene("bones-pelvis-f", pel)
tag("bones-pelvis-f")
print({g["label"]: len(g["ids"]) for g in pel})

# ---------------- context for both female workstations ----------------
write_scene("pelvis-f", [
    {"key": "bones", "label": "Pelvis", "color": 0xd9d2c3, "keep": 0.12, "ids": [p for p in hip if "spongy" not in node(p)]},
    {"key": "bladder", "label": "Urinary bladder", "color": 0xd9b27a, "keep": 0.3, "ids": of("Urinary_Bladder")},
    {"key": "repro-female", "label": "Female reproductive organs", "color": 0xd98a9a, "keep": 0.3, "ids": of("Uterus", "Fallopian_Tube_L", "Fallopian_Tube_R", "Ovary_L", "Ovary_R")},
])
(OUT / "hra-sources.json").write_text(json.dumps({"files": src, "leftOut": {k: dict(meta_md[k], why=v) for k, v in LEFT_OUT.items()},
                                                   "floorShiftM": round(float(-floor), 4)}, indent=1))
print("floor shift", round(float(-floor), 4), "m;", len(GEOM), "HRA meshes")
