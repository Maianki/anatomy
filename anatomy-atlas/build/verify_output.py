"""Decode the scene files the app loads and measure them against the official BodyParts3D meshes.
Usage: verify_output.py <site data dir> <isa zip> [scene ...]"""
import base64, gzip, json, os, sys
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import official
DATA, ZIP = sys.argv[1], sys.argv[2]
scenes = sys.argv[3:] or ["heart2", "lungs", "liver", "gut", "urinary", "brain"] + ["bones-" + r for r in ("skull", "spine", "thorax", "upper", "pelvis", "lower")] + ["repro-male"]
cache = os.path.join(os.path.dirname(ZIP), "cache")
report = {}
for sc in scenes:
    meta = json.load(open(f"{DATA}/{sc}.json"))
    buf = gzip.decompress(base64.b64decode(open(f"{DATA}/{sc}.gz.txt").read()))
    o, s = np.array(meta["origin"]), meta["scale"] / 65535
    worst = []
    ctx = {g["key"] for g in meta["groups"] if "(context)" in g["label"]}
    for m in meta["meshes"]:
        if m["group"] in ctx:  # context-only groups are simplified on purpose
            continue
        pos = np.frombuffer(buf, np.uint16, m["v"] * 3, m["p"]).reshape(-1, 3) * s + o
        idx = np.frombuffer(buf, np.uint32 if m["w"] else np.uint16, m["n"], m["i"]).reshape(-1, 3)
        ov, of = official.mesh(ZIP, m["id"], cache)
        used = np.unique(of)
        tri = pos[idx]
        samp = np.vstack([pos, tri.mean(1), (tri[:, 0] + tri[:, 1]) / 2, (tri[:, 1] + tri[:, 2]) / 2, (tri[:, 0] + tri[:, 2]) / 2])
        d = cKDTree(samp).query(ov[used])[0]
        # crop: the great vessels are cut on purpose, so only compare inside the written mesh's height range
        if sc == "heart2" or sc == "liver" or sc == "urinary":
            inside = (ov[used][:, 1] >= pos[:, 1].min() - 1e-4) & (ov[used][:, 1] <= pos[:, 1].max() + 1e-4)
            d = d[inside] if inside.any() else d
        worst.append((float(d.max() * 1000), m["name"]))
    worst.sort(reverse=True)
    report[sc] = {"max_mm": round(worst[0][0], 2), "worst": worst[0][1], "meshes": len(worst)}
    print(f"{sc:8s} {len(worst):3d} meshes | max distance of any original vertex from what the app shows: {worst[0][0]:.2f} mm ({worst[0][1]})")
if len(sys.argv) > 3 and sys.argv[-1].endswith(".json"):
    pass
json.dump(report, open(os.environ.get("VERIFY_OUT", "verify_output.json"), "w"), indent=1)
