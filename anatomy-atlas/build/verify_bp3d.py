"""Compare the repackaged model (@dagno/anatomy-model) with the original BodyParts3D 4.0 OBJ archive.
Usage: verify_bp3d.py <isa_BP3D_4.0_obj_99.zip> <package model dir> <out json>"""
import itertools, json, re, sys, zipfile
import numpy as np
ZIP, MODEL, OUTF = sys.argv[1:4]
atlas = json.load(open(f"{MODEL}/atlas.json"))
ours = {p["id"]: p for p in atlas["parts"]}
orig, header = {}, {}
with zipfile.ZipFile(ZIP) as z:
    for n in z.namelist():
        m = re.search(r"(FJ\w+)\.obj$", n)
        if not m:
            continue
        txt = z.read(n).decode("utf-8", "replace")
        v = np.array([list(map(float, l.split()[1:4])) for l in txt.splitlines() if l.startswith("v ")])
        orig[m.group(1)] = (v.min(0), v.max(0), len(v))
        if not header:
            header = [l for l in txt.splitlines()[:25] if l.startswith("#")]
print("original meshes:", len(orig), "| ours:", len(ours), "| missing:", sorted(set(ours) - set(orig))[:5], sorted(set(orig) - set(ours))[:5])
ids = sorted(set(ours) & set(orig))
oc = np.array([(orig[i][0] + orig[i][1]) / 2 for i in ids]) / 1000.0  # mm -> m
uc = np.array([(np.array(ours[i]["bounds"][0]) + np.array(ours[i]["bounds"][1])) / 2 for i in ids])
best = None
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1, -1), repeat=3):
        R = np.zeros((3, 3))
        for r, (c, s) in enumerate(zip(perm, sg)):
            R[r, c] = s
        t = np.median(uc - oc @ R.T, 0)
        res = np.linalg.norm(oc @ R.T + t - uc, axis=1)
        if best is None or np.median(res) < np.median(best[2]):
            best = (R, t, res)
R, t, res = best
print("axis mapping (rows = our x,y,z from original x,y,z):", R.astype(int).tolist(), "translation (m):", np.round(t, 4).tolist())
print("centre residual  median %.2f mm  95th %.2f mm  max %.2f mm" % tuple(np.percentile(res, [50, 95, 100]) * 1000))
off = [(ids[i], ours[ids[i]]["name"], round(float(res[i]) * 1000, 1)) for i in np.argsort(-res) if res[i] > 0.005]
print("meshes whose centre moved more than 5 mm:", off[:10])
def where(fj):
    lo, hi, n = orig[fj]
    c = ((lo + hi) / 2 / 1000.0) @ R.T + t
    return [round(float(x), 3) for x in c]
checks = {fj: {"name": ours[fj]["name"], "original_centre_in_our_axes": where(fj),
               "our_centre": [round(float(x), 3) for x in (np.array(ours[fj]["bounds"][0]) + np.array(ours[fj]["bounds"][1])) / 2]}
          for fj in ["FJ2041", "FJ2044", "FJ1735", "FJ1736", "FJ1779", "FJ1826"]}
for k, v in checks.items():
    print(k, v)
import csv
official_names = {}
for r in csv.reader(open(sys.argv[4], encoding="utf-8"), delimiter="\t") if len(sys.argv) > 4 else []:
    if len(r) >= 3 and r[2].startswith("FJ"):
        official_names.setdefault(r[2], {})[r[0]] = r[1]
name_mismatch = [i for i in ids if official_names and (official_names.get(i, {}).get(ours[i]["conceptId"]) or "").lower() != ours[i]["name"].lower()]
print("name/FMA mismatches against the official element table:", len(name_mismatch))
json.dump({"name_fma_mismatches": len(name_mismatch), "original_meshes": len(orig), "matched": len(ids), "median_mm": float(np.median(res) * 1000), "max_mm": float(res.max() * 1000),
           "moved_over_5mm": off, "checks": checks, "obj_header": header}, open(OUTF, "w"), indent=1)
print("\n".join(header[:12]))
