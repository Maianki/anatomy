"""Read meshes straight from the official BodyParts3D 4.0 archive (isa_BP3D_4.0_obj_99.zip) into the app's axes.

The transform was found by verify_bp3d.py: millimetres to metres, Z-up to Y-up, feet at the origin. With it, the
centres of all 2,234 meshes in @dagno/anatomy-model match the original to 0.00 mm. Parsed meshes are cached as .npz.
"""
import os, re, zipfile
import numpy as np
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=np.float64)
T = np.array([0.0, 0.0781, -0.1])
_z, _names = None, None


def _open(zip_path):
    global _z, _names
    if _z is None:
        _z = zipfile.ZipFile(zip_path)
        _names = {re.search(r"(FJ\w+)\.obj$", n).group(1): n for n in _z.namelist() if n.endswith(".obj")}
    return _z, _names


def mesh(zip_path, pid, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    c = os.path.join(cache_dir, pid + ".npz")
    if os.path.exists(c):
        d = np.load(c)
        return d["v"], d["f"]
    z, names = _open(zip_path)
    v, f = [], []
    for line in z.read(names[pid]).decode("utf-8", "replace").splitlines():
        if line.startswith("v "):
            v.append(line.split()[1:4])
        elif line.startswith("f "):
            ix = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            f += [(ix[0], ix[k], ix[k + 1]) for k in range(1, len(ix) - 1)]  # fan-triangulate polygons
    v = ((np.array(v, dtype=np.float64) / 1000.0) @ R.T + T).astype(np.float32)
    f = np.array(f, dtype=np.uint32)
    np.savez(c, v=v, f=f)
    return v, f
