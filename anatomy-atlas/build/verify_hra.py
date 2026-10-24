"""Decode the female scene files the app loads and measure them against the original Human Reference Atlas meshes.
Usage: HRA_DIR=<ccf-releases checkout> verify_hra.py <site data dir> [scene ...]
Also records the SHA-256 of every model file used and the checkout's commit, so the source can be pinned."""
import base64, glob, gzip, hashlib, json, os, subprocess, sys
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glb
DATA, HRA = sys.argv[1], os.environ["HRA_DIR"]
scenes = sys.argv[2:] or ["repro-female", "bones-pelvis-f"]
src = json.load(open(f"{DATA}/hra-sources.json"))
shift = src["floorShiftM"]
orig = {}
for f in src["files"]:
    for node, _, pos, idx in glb.meshes(f"{HRA}/v1.2/models/{f}"):
        p = pos.copy()
        p[:, 1] += shift
        orig["HRA:" + node] = p
report = {"commit": subprocess.run(["git", "-C", HRA, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
          "files": {f: hashlib.sha256(open(f"{HRA}/v1.2/models/{f}", "rb").read()).hexdigest() for f in src["files"]}}
for sc in scenes:
    meta = json.load(open(f"{DATA}/{sc}.json"))
    buf = gzip.decompress(base64.b64decode(open(f"{DATA}/{sc}.gz.txt").read()))
    o, s = np.array(meta["origin"]), meta["scale"] / 65535
    ctx = {g["key"] for g in meta["groups"] if "(context)" in g["label"]}
    worst = []
    for m in meta["meshes"]:
        if m["group"] in ctx:
            continue
        pos = np.frombuffer(buf, np.uint16, m["v"] * 3, m["p"]).reshape(-1, 3) * s + o
        idx = np.frombuffer(buf, np.uint32 if m["w"] else np.uint16, m["n"], m["i"]).reshape(-1, 3)
        tri = pos[idx]
        samp = np.vstack([pos, tri.mean(1), (tri[:, 0] + tri[:, 1]) / 2, (tri[:, 1] + tri[:, 2]) / 2, (tri[:, 0] + tri[:, 2]) / 2])
        d = cKDTree(samp).query(orig[m["id"]])[0]
        worst.append((float(d.max() * 1000), m["name"]))
    worst.sort(reverse=True)
    report[sc] = {"max_mm": round(worst[0][0], 2), "worst": worst[0][1], "meshes": len(worst)}
    print(f"{sc:14s} {len(worst):3d} meshes | max distance of any original vertex from what the app shows: {worst[0][0]:.2f} mm ({worst[0][1]})")
json.dump(report, open(os.environ.get("VERIFY_OUT", "verify_hra.json"), "w"), indent=1)
