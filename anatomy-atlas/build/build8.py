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
FILES = ["Pelvis", "Urinary_Bladder", "Uterus", "Fallopian_Tube_L", "Fallopian_Tube_R", "Ovary_L", "Ovary_R",
         "Blood_Vasculature",   # only the uterine arteries and veins are used
         "Knee_L", "Knee_R",    # only the femoral heads, to measure how the fitted hip joints line up
         "Skin"]                # only to put the feet at the floor (the female skin itself is not shown)
# Left out, with the reason shown on the Sources page and in DECISIONS. The female body is the male reference body
# except the pelvic region, so the other female organ files are not used.
LEFT_OUT = {"VH_F_Placenta.glb": "A full-term placenta belongs to pregnancy; this body is shown as not pregnant."}

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
    return [p for p in GEOM if p.startswith("HRA:") and FILE_OF[p] in {f"VH_F_{f}.glb" for f in files}]


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
    p.write_text(json.dumps(m, separators=(",", ":")))


VEIN = r"vein|vena_cava|coronary_sinus"
vessels = of("Blood_Vasculature")
assert all(re.search(VEIN + r"|arter|aort|trunk|branch", node(p)) for p in vessels), [node(p) for p in vessels if not re.search(VEIN + r"|arter|aort|trunk|branch", node(p))]
hip = of("Pelvis")

# ---------------- female body ----------------
# The female body is the male reference body (same skeleton, muscles, vessels, nerves, organs) except the pelvic
# region, which comes from the Visible Human Female as one block: hip bones, sacrum, coccyx, bladder, uterus, uterine
# tubes, ovaries and uterine vessels. The block is placed by one rigid fit (rotation + translation, no scaling) of the
# female pelvis onto the male pelvis, so the female organs keep their real arrangement and size. Removed from the male
# body: hip bones, sacrum, bladder, urethra, the reproductive organs, and the penile and testicular vessels. The male
# skin is kept with the external genital region cut away (there is no female skin in a matching pose).
from scipy.spatial import cKDTree
MALE_ONLY = re.compile(r"\b(penis|penile|scrot\w*|testis|testicular|spermatic|cremaster|prostate|seminal|deferent|epididymis)\b", re.I)
PELVIC_MALE = {"Left hip bone", "Right hip bone", "Sacrum", "Urinary bladder", "Urethra"}
male_groups = json.loads((OUT / "body-groups.json").read_text())
named_ids = lambda *n: [p["id"] for p in atlas["parts"] if p["name"] in n]
fpel = [p for p in hip if "spongy" not in node(p)]
block = fpel + of("Urinary_Bladder", "Uterus", "Fallopian_Tube_L", "Fallopian_Tube_R", "Ovary_L", "Ovary_R") + where(vessels, r"uterine")


def sphere_centre(P):
    A = np.c_[2 * P, np.ones(len(P))]
    return np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)[0][:3]


def femoral_head(P):  # centre of a sphere fitted to the medial half of the top 4 cm of the femur
    Q = P[P[:, 1] > P[:, 1].max() - 0.04]
    return sphere_centre(Q[np.abs(Q[:, 0]) < np.median(np.abs(Q[:, 0]))])


M = np.concatenate([_official_geom(i)[0] for i in named_ids("Left hip bone", "Right hip bone", "Sacrum")]).astype(float)
Fp = np.concatenate([GEOM[p][0] for p in fpel]).astype(float)
mh = [femoral_head(_official_geom(named_ids(f"{s} femur")[0])[0].astype(float)) for s in ("Left", "Right")]
fh = [femoral_head(GEOM[f"HRA:VH_F_femur_{s}"][0].astype(float)) for s in "LR"]
R, t = np.eye(3), np.mean(mh, 0) - np.mean(fh, 0)          # start: hip-joint midpoints together
tree, S = cKDTree(M), Fp[np.random.default_rng(0).choice(len(Fp), 20000, replace=False)]
for _ in range(60):                                          # rigid ICP, nearest 90% of points
    X = S @ R.T + t
    d, j = tree.query(X)
    k = d < np.percentile(d, 90)
    A, B = X[k], M[j[k]]
    U, _, Vt = np.linalg.svd((A - A.mean(0)).T @ (B - B.mean(0)))
    dR = Vt.T @ np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))]) @ U.T
    R, t = dR @ R, dR @ t + B.mean(0) - dR @ A.mean(0)
d = tree.query(Fp @ R.T + t)[0]
fit = {"rotationDeg": round(float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))), 1), "translationM": np.round(t, 4).tolist(),
       "pelvisSurfaceGapMm": {"median": round(float(np.median(d)) * 1000, 1), "p90": round(float(np.percentile(d, 90)) * 1000, 1)},
       "hipJointOffsetMm": {s: round(float(np.linalg.norm(h @ R.T + t - m)) * 1000, 1) for s, h, m in zip(("left", "right"), fh, mh)}}
for p in block:
    pos, idx = GEOM[p]
    pid = "FIT:" + node(p)
    parts[pid] = dict(parts[p], id=pid)
    GEOM[pid] = ((pos.astype(float) @ R.T + t).astype(np.float32), idx)
    FILE_OF[pid] = FILE_OF[p]
fitted = lambda ids: ["FIT:" + node(p) for p in ids]

# skin: cut away the male external genital region (box around the penis, testes and epididymides, 1 cm margin, front only)
G = np.concatenate([_official_geom(i)[0] for i in named_ids("Corpus cavernosum of penis", "Corpus spongiosum of penis", "Glans penis",
                                                             "Left testis", "Right testis", "Left epididymis", "Right epididymis")])
lo, hi = G.min(0) - 0.01, G.max(0) + 0.01
skin_id = named_ids("Skin")[0]
sv, sf = _official_geom(skin_id)
cen = sv[sf].mean(1)
cut = np.all((cen > lo) & (cen < hi), 1)
parts["CUT:Skin"] = dict(parts[skin_id], id="CUT:Skin")
GEOM["CUT:Skin"] = (sv, sf[~cut])
fit["skinTrianglesRemoved"] = int(cut.sum())
fit["skinCutBoxM"] = [np.round(lo, 3).tolist(), np.round(hi, 3).tolist()]

female = []
removed = []
for g in male_groups:
    g = dict(g)
    keep = [i for i in g["ids"] if parts[i]["name"] not in PELVIC_MALE and not MALE_ONLY.search(parts[i]["name"]) and parts[i]["system"] != "reproductive"]
    removed += [parts[i]["name"] for i in g["ids"] if i not in keep]
    g["ids"] = ["CUT:Skin" if i == skin_id else i for i in keep]
    if g["key"] == "bones-pelvis":
        g.update(ids=fitted(fpel), label="Pelvis (female)", fma="")
    if g["key"] == "urinary-bladder":
        g.update(ids=fitted(of("Urinary_Bladder")), fma="")
    if g["key"] == "arteries":
        g["ids"] += fitted(where(vessels, r"uterine_artery"))
    if g["key"] == "veins":
        g["ids"] += fitted(where(vessels, r"uterine_vein"))
    if g["ids"]:
        female.append(g)
female += [
    {"key": "uterus", "label": "uterus", "fma": "", "layer": "organs", "color": 0xd98a9a, "keep": 0.3, "clickable": True,
     "ids": fitted(where(of("Uterus"), r"^(?!.*abdominal_ostium)"))},
    {"key": "uterine-tube", "label": "uterine tube", "fma": "", "layer": "organs", "color": 0xe0a8b0, "keep": 0.3, "clickable": True,
     "ids": fitted(of("Fallopian_Tube_L", "Fallopian_Tube_R") + where(of("Uterus"), r"abdominal_ostium"))},
    {"key": "ovary", "label": "ovary", "fma": "", "layer": "organs", "color": 0xe8c49a, "keep": 0.3, "clickable": True, "ids": fitted(of("Ovary_L", "Ovary_R"))},
]
fit["removedFromMaleBody"] = sorted(set(removed))


def inside(P, V, F):
    """Generalised winding number: True where a point is inside the closed surface (V, F)."""
    out = np.zeros(len(P), bool)
    for s in range(0, len(P), 100):
        Q = P[s:s + 100]
        a, b, c = (V[F[:, k]][None] - Q[:, None] for k in range(3))
        la, lb, lc = (np.linalg.norm(x, axis=2) for x in (a, b, c))
        det = np.einsum("ijk,ijk->ij", a, np.cross(b, c))
        div = la * lb * lc + np.einsum("ijk,ijk->ij", a, b) * lc + np.einsum("ijk,ijk->ij", b, c) * la + np.einsum("ijk,ijk->ij", c, a) * lb
        out[s:s + 100] = np.abs(np.arctan2(det, div).sum(1) / (2 * np.pi)) > 0.5
    return out


# report where the fitted female organs pass into male organs that stay in the body (share of surface points)
kept_male = {i for g in female for i in g["ids"] if i in parts and not i.startswith(("FIT:", "CUT:"))}
overlaps = {}
rng = np.random.default_rng(1)
for key, ids in (("uterus", female[-3]["ids"]), ("uterine tubes", female[-2]["ids"]), ("ovaries", female[-1]["ids"]), ("bladder", fitted(of("Urinary_Bladder")))):
    P = np.concatenate([GEOM[i][0] for i in ids]).astype(float)
    P = P[rng.choice(len(P), min(1000, len(P)), replace=False)]
    hits = {}
    for i in kept_male:
        V, F = _official_geom(i)
        m = np.all((P > V.min(0)) & (P < V.max(0)), 1)
        if m.sum():
            n = int(inside(P[m], V.astype(float), F).sum())
            if n:
                hits[parts[i]["name"]] = round(100 * n / len(P), 1)
    overlaps[key] = dict(sorted(hits.items(), key=lambda kv: -kv[1]))
fit["overlapPercent"] = overlaps
ft = cKDTree(np.concatenate([GEOM[i][0] for i in fitted(of("Urinary_Bladder"))]))
fit["ureterEndToBladderMm"] = {n: round(float(ft.query(V[V[:, 1] < V[:, 1].min() + 0.01])[0].min()) * 1000, 1)
                               for n in ("Left ureter", "Right ureter") for V in [_official_geom(named_ids(n)[0])[0]]}
write_scene("body-f", female)
tag("body-f")
(OUT / "female-fit.json").write_text(json.dumps(fit, indent=1))
print("female fit:", json.dumps({k: v for k, v in fit.items() if k not in ("removedFromMaleBody",)}))

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
