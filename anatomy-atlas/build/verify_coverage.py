"""For every mesh: what share of the original BodyParts3D vertices lies more than 2 mm from the geometry we display?
Usage: verify_coverage.py <package model dir> <isa zip> <out json>"""
import sys, json, re, zipfile, tempfile
from scipy.spatial import cKDTree
ZIP, OUTF = sys.argv[2], sys.argv[3]
sys.argv = [sys.argv[0], sys.argv[1], tempfile.mkdtemp()]
exec(open(__file__.replace("verify_coverage.py", "common.py")).read())
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]]); T = np.array([0.0, 0.0781, -0.1])
rows = []
with zipfile.ZipFile(ZIP) as z:
    names = {re.search(r"(FJ\w+)\.obj$", n).group(1): n for n in z.namelist() if n.endswith(".obj")}
    for pid in parts:
        v = np.array([list(map(float, l.split()[1:4])) for l in z.read(names[pid]).decode("utf-8", "replace").splitlines() if l.startswith("v ")])
        o = (v / 1000.0) @ R.T + T
        ours, idx = geom(pid)
        # sample our surface densely: vertices plus triangle centroids and edge midpoints
        tri = ours[idx]
        samp = np.vstack([ours, tri.mean(1), (tri[:, 0] + tri[:, 1]) / 2, (tri[:, 1] + tri[:, 2]) / 2, (tri[:, 0] + tri[:, 2]) / 2])
        d, _ = cKDTree(samp).query(o)
        far = d > 0.002
        rows.append({"id": pid, "name": parts[pid]["name"], "share_far": float(far.mean()), "max_mm": float(d.max() * 1000),
                     "far_centre": np.round(o[far].mean(0), 3).tolist() if far.any() else None, "n": int(len(o))})
rows.sort(key=lambda r: -r["share_far"])
json.dump(rows, open(OUTF, "w"), indent=0)
s = np.array([r["share_far"] for r in rows])
print("meshes:", len(rows), "| share of original vertices >2 mm from displayed geometry: median %.4f%%, 99th %.3f%%" % (np.median(s) * 100, np.percentile(s, 99) * 100))
for thr in (0.01, 0.05, 0.10):
    print(f"meshes with more than {thr:.0%} of original vertices further than 2 mm:", int((s > thr).sum()))
for r in rows[:15]:
    print("  %5.1f%%  max %6.1f mm  %-8s %s  far part centre %s" % (r["share_far"] * 100, r["max_mm"], r["id"], r["name"], r["far_centre"]))
