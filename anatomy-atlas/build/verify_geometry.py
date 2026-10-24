"""Compare the vertices we display with the original OBJ vertices, mesh by mesh (bounding boxes in metres).
Usage: verify_geometry.py <package model dir> <isa zip> <verify_bp3d.json>"""
import sys, json, re, zipfile
ZIP, VJ = sys.argv[2], sys.argv[3]
import os, tempfile
sys.argv = [sys.argv[0], sys.argv[1], tempfile.mkdtemp()]
exec(open(__file__.replace("verify_geometry.py", "common.py")).read())
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]]); T = np.array([0.0, 0.0781, -0.1])  # from verify_bp3d.py
worst = []
with zipfile.ZipFile(ZIP) as z:
    names = {re.search(r"(FJ\w+)\.obj$", n).group(1): n for n in z.namelist() if n.endswith(".obj")}
    for pid in parts:
        v = np.array([list(map(float, l.split()[1:4])) for l in z.read(names[pid]).decode("utf-8", "replace").splitlines() if l.startswith("v ")])
        o = (v / 1000.0) @ R.T + T
        ours_v, _ = geom(pid)
        d = max(np.abs(o.min(0) - ours_v.min(0)).max(), np.abs(o.max(0) - ours_v.max(0)).max())
        size = (o.max(0) - o.min(0)).max()
        worst.append((float(d) * 1000, float(size) * 1000, pid, parts[pid]["name"]))
worst.sort(reverse=True)
d = np.array([w[0] for w in worst])
print("bounding-box difference, displayed vs original: median %.2f mm, 99th %.2f mm, max %.2f mm" % (np.median(d), np.percentile(d, 99), d.max()))
print("largest:", [(round(a, 2), round(b, 1), c, n) for a, b, c, n in worst[:5]])
res = json.load(open(VJ)); res["displayed_bbox_mm"] = {"median": float(np.median(d)), "p99": float(np.percentile(d, 99)), "max": float(d.max())}
json.dump(res, open(VJ, "w"), indent=1)
