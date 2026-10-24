"""Build compact scene files for the anatomy atlas.

Geometry comes straight from the official BodyParts3D 4.0 archive (env BP3D_ZIP = isa_BP3D_4.0_obj_99.zip, see
official.py). Names, FMA IDs and the concept hierarchy come from @dagno/anatomy-model's atlas.json, which
verify_bp3d.py showed to match the official tables exactly. Output: <name>.json manifest + <name>.bin.gz with uint16
quantized positions and uint16/uint32 indices. Normals are recomputed in the browser.
"""
import gzip, json, os, struct, sys
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import official
from scipy.spatial import cKDTree
BP3D_ZIP = os.environ["BP3D_ZIP"]
BP3D_CACHE = os.environ.get("BP3D_CACHE", os.path.join(os.path.dirname(BP3D_ZIP), "cache"))
MAX_DEV = 0.001  # organ workstations: every original vertex within 1 mm of the displayed surface
deviation = {}   # pid -> max deviation (m) of the original from what is written


def geom(pid):
    return official.mesh(BP3D_ZIP, pid, BP3D_CACHE)


def max_dev(orig, pos, idx):
    tri = pos[idx]
    samp = np.vstack([pos, tri.mean(1), (tri[:, 0] + tri[:, 1]) / 2, (tri[:, 1] + tri[:, 2]) / 2, (tri[:, 0] + tri[:, 2]) / 2])
    return float(cKDTree(samp).query(orig)[0].max())


def simplify(pos, idx, keep):
    if keep == "auto":  # least triangles that keep every original vertex within MAX_DEV
        if len(idx) < 200:
            return pos, idx
        for k in (0.25, 0.4, 0.6, 0.8):
            p2, i2 = simplify(pos, idx, k)
            if len(i2) >= 20 and max_dev(pos, p2, i2) <= MAX_DEV:
                return p2, i2
        return pos, idx
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
            o, oi = geom(pid)
            pos, idx = simplify(o, oi, g.get("keep", 1))
            if g.get("keep", 1) == "auto" or g.get("keep", 1) >= 1:
                deviation[pid] = 0.0 if pos is o else max_dev(o, pos, idx)
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
    devs = [deviation[m[1]] for m in meshes if m[0].get("keep", 1) == "auto" or m[0].get("keep", 1) >= 1]
    meta = {"origin": lo.tolist(), "scale": float(scale), "meshes": out,
            "geometry": "BodyParts3D 4.0 isa_BP3D_4.0_obj_99.zip",
            "maxDeviationMm": round(max(devs) * 1000, 3) if devs else None,
            "groups": [{k: g[k] for k in g if k != "ids"} for g in groups]}
    (OUT / f"{name}.json").write_text(json.dumps(meta, separators=(",", ":")))
    tris = sum(m[3].shape[0] for m in meshes)
    print(name, len(out), "meshes", tris, "tris", (OUT / f"{name}.bin.gz").stat().st_size // 1024, "KB",
          "max deviation %.2f mm" % (max(devs) * 1000) if devs else "")


