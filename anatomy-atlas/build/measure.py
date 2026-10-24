"""Longest-axis length (principal component extent) of single-mesh organs, from source geometry, for size QA."""
import sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("measure.py", "common.py")).read())
import json as _j
res = {}
for n in ["Left kidney", "Right kidney", "Spleen", "Gallbladder", "Left testis", "Right testis"]:
    pid = next(p["id"] for p in atlas["parts"] if p["name"] == n)
    pos, _ = geom(pid)
    c = pos - pos.mean(0)
    _, _, vt = np.linalg.svd(c, full_matrices=False)
    proj = c @ vt[0]
    res[n] = round(float(proj.max() - proj.min()) * 100, 1)
print(res)
(OUT / "sizes.json").write_text(_j.dumps(res))
