"""Build compact scene files for the anatomy design demo from @dagno/anatomy-model (BodyParts3D 4.0).

Chunk layout per part (inferred, verified by offsets): float32 xyz positions, int16 xyz normals
(padded to 4 bytes), uint32 indices. Output: <name>.json manifest + <name>.bin.gz with uint16
quantized positions and uint16/uint32 indices. Normals are recomputed in the browser.
"""
import gzip, json, struct, sys
from pathlib import Path
import numpy as np
import fast_simplification

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

atlas = json.loads((SRC / "atlas.json").read_text())
parts = {p["id"]: p for p in atlas["parts"]}
concepts = {}
for c in atlas["concepts"]:
    concepts.setdefault(c["name"], c)
chunks = {}


def chunk(i):
    if i not in chunks:
        chunks[i] = gzip.decompress((SRC / atlas["chunks"][i]["gzip"]).read_bytes())
    return chunks[i]


def geom(pid):
    p = parts[pid]
    b = chunk(p["chunk"])
    pos = np.frombuffer(b, np.float32, p["vertexCount"] * 3, p["positions"]).reshape(-1, 3)
    idx = np.frombuffer(b, np.uint32, p["indexCount"], p["indices"]).reshape(-1, 3)
    return pos.copy(), idx.copy()


def simplify(pos, idx, keep):
    if keep >= 1 or len(idx) < 200:
        return pos, idx
    try:
        p2, i2 = fast_simplification.simplify(pos, idx, target_reduction=1 - keep)
        if len(i2) < 20:
            return pos, idx
        return p2.astype(np.float32), i2.astype(np.uint32)
    except Exception:
        return pos, idx


def elements(name):
    return [e for e in concepts[name]["elements"] if e in parts]


def write_scene(name, groups):
    """groups: list of dicts {key,label,layer,color,ids,keep,clickable,fma}"""
    meshes = []
    for g in groups:
        for pid in g["ids"]:
            pos, idx = simplify(*geom(pid), g.get("keep", 1))
            meshes.append((g, pid, pos, idx))
    allpos = np.concatenate([m[2] for m in meshes])
    lo, hi = allpos.min(0), allpos.max(0)
    scale = (hi - lo).max()
    buf = bytearray()
    out = []
    for g, pid, pos, idx in meshes:
        q = np.round((pos - lo) / scale * 65535).clip(0, 65535).astype(np.uint16)
        while len(buf) % 4:
            buf += b"\0"
        po = len(buf)
        buf += q.tobytes()
        while len(buf) % 4:
            buf += b"\0"
        io = len(buf)
        wide = len(pos) > 65535
        buf += idx.astype(np.uint32 if wide else np.uint16).tobytes()
        p = parts[pid]
        out.append({"id": pid, "name": p["name"], "fma": p["conceptId"], "group": g["key"],
                    "p": po, "v": len(pos), "i": io, "n": idx.size, "w": int(wide)})
    (OUT / f"{name}.bin.gz").write_bytes(gzip.compress(bytes(buf), 9))
    meta = {"origin": lo.tolist(), "scale": float(scale), "meshes": out,
            "groups": [{k: g[k] for k in g if k != "ids"} for g in groups]}
    (OUT / f"{name}.json").write_text(json.dumps(meta, separators=(",", ":")))
    tris = sum(m[3].shape[0] for m in meshes)
    print(name, len(out), "meshes", tris, "tris", (OUT / f"{name}.bin.gz").stat().st_size // 1024, "KB")


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
# Placement errors found by the lung workstation check (build3.py): two "Right anterior segmental artery"
# meshes sit below the diaphragm. Left out everywhere.
used = {e["id"] for e in json.loads((OUT / "lungs.json").read_text())["excluded"]}
organ_groups = []
for key, cname, col in ORGANS:
    c = concepts[cname]
    ids = [e for e in elements(cname) if e not in used]
    if key == "heart":
        ids += [e for e in elements("wall of ventricle") if e not in used]
    used.update(ids)
    organ_groups.append({"key": key, "label": cname, "fma": c["id"], "layer": "organs", "color": col,
                         "ids": ids, "keep": 0.5, "clickable": True})

body = [
    {"key": "skin", "label": "Skin", "fma": concepts["skin"]["id"], "layer": "skin", "color": 0xc9a48c,
     "ids": elements("skin"), "keep": 0.5},
    {"key": "skeleton", "label": "Skeletal system", "layer": "skeleton", "color": 0xe8e0cf,
     "ids": [i for i in sysids("skeletal") if i not in used], "keep": 0.25},
    {"key": "muscles", "label": "Muscles", "layer": "muscles", "color": 0xa8474a,
     "ids": [i for i in sysids("muscular") if i not in used], "keep": 0.12},
    {"key": "arteries", "label": "Arteries", "layer": "vessels", "color": 0xc62f36,
     "ids": [i for i in sysids("arterial") if i not in used], "keep": 0.3},
    {"key": "veins", "label": "Veins", "layer": "vessels", "color": 0x3d5fa8,
     "ids": [i for i in sysids("venous") if i not in used], "keep": 0.3},
    {"key": "nerves", "label": "Nervous system", "layer": "nerves", "color": 0xe6c45a,
     "ids": [i for i in sysids("nervous") if i not in used and i not in elements("brain")], "keep": 0.3},
] + organ_groups
write_scene("body", body)

