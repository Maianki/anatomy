"""Minimal GLB reader: node tree with world transforms, mesh primitives as numpy arrays (positions, indices)."""
import json, struct
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def load(path):
    b = open(path, "rb").read()
    assert b[:4] == b"glTF", path
    n = struct.unpack_from("<I", b, 12)[0]
    js = json.loads(b[20:20 + n])
    o = 20 + n
    bn = struct.unpack_from("<I", b, o)[0]
    return js, b[o + 8:o + 8 + bn]


def accessor(js, bin_, i):
    a = js["accessors"][i]
    v = js["bufferViews"][a["bufferView"]]
    dt, nc = CT[a["componentType"]], NC[a["type"]]
    off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = v.get("byteStride")
    item = np.dtype(dt).itemsize * nc
    if stride and stride != item:
        raw = np.frombuffer(bin_, np.uint8, a["count"] * stride, off).reshape(a["count"], stride)[:, :item]
        arr = np.frombuffer(raw.tobytes(), dt).reshape(a["count"], nc)
    else:
        arr = np.frombuffer(bin_, dt, a["count"] * nc, off).reshape(a["count"], nc)
    assert not a.get("sparse")
    return arr


def local(node):
    if "matrix" in node:
        return np.array(node["matrix"], float).reshape(4, 4).T
    t = np.array(node.get("translation", [0, 0, 0]), float)
    x, y, z, w = node.get("rotation", [0, 0, 0, 1])
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    s = np.array(node.get("scale", [1, 1, 1]), float)
    M = np.eye(4)
    M[:3, :3] = R * s
    M[:3, 3] = t
    return M


def meshes(path):
    """Yield (node name, path of node names, positions in world space Nx3, triangle indices Mx3)."""
    js, bin_ = load(path)
    out = []

    def walk(i, M, trail):
        nd = js["nodes"][i]
        W = M @ local(nd)
        name = nd.get("name", "")
        if "mesh" in nd:
            for pr in js["meshes"][nd["mesh"]]["primitives"]:
                assert pr.get("mode", 4) == 4
                p = accessor(js, bin_, pr["attributes"]["POSITION"]).astype(float)
                idx = accessor(js, bin_, pr["indices"]).reshape(-1, 3).astype(np.int64) if "indices" in pr else np.arange(len(p)).reshape(-1, 3)
                pw = p @ W[:3, :3].T + W[:3, 3]
                out.append((name, trail + [name], pw, idx))
        for c in nd.get("children", []):
            walk(c, W, trail + [name])

    for sc in js["scenes"][js.get("scene", 0)]["nodes"]:
        walk(sc, np.eye(4), [])
    return out
