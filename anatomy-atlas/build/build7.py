"""Male reproductive workstation and the pelvis context.

The organs are the meshes the dataset files under the reproductive system (12 meshes), plus the urethra, the
vessels named for the testes and the penis, and the urinary bladder for context. Every candidate mesh must fall
into exactly one group (the build fails otherwise). The testicular vessels run up to the kidneys, so they are
kept out of the framing box (group keys starting with "great", as for the heart's great vessels).
BodyParts3D is one male body: it has no female organs.
"""
import re, sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build7.py", "common.py")).read())

REPRO = [p["id"] for p in atlas["parts"] if p["system"] == "reproductive"]
VESSELS = [p["id"] for p in atlas["parts"] if re.search(r"testicular (artery|vein)|dorsal (artery|vein) of penis", p["name"], re.I)]
pool = REPRO + VESSELS + [p["id"] for p in atlas["parts"] if p["name"] in ("Urethra", "Urinary bladder")]
rx = lambda pat: (lambda n: re.search(pat, n, re.I))
GROUPS = [  # key, label, colour, rule on the dataset name
    ("testes", "Testes", 0xe0b38a, rx(r"^(left|right) testis$")),
    ("epididymis", "Epididymides", 0xc98f6a, rx(r"epididymis$")),
    ("deferent", "Ductus deferens", 0xd9c27a, rx(r"deferent duct$")),
    ("seminal", "Seminal vesicles", 0xb7a2c9, rx(r"seminal vesicle$")),
    ("prostate", "Prostate", 0xa98ab0, rx(r"^prostate$")),
    ("penis", "Penis", 0xd99a8a, rx(r"^(corpus cavernosum|corpus spongiosum|glans) (of )?penis$|^glans penis$")),
    ("urethra", "Urethra", 0xf0d9a8, rx(r"^urethra$")),
    ("penile-arteries", "Dorsal arteries of the penis", 0xd84a3f, rx(r"dorsal artery of penis")),
    ("penile-veins", "Dorsal veins of the penis", 0x4f78c8, rx(r"dorsal vein of penis")),
    ("great-tarteries", "Testicular arteries", 0xc62f36, rx(r"testicular artery")),
    ("great-tveins", "Testicular veins", 0x3d5fa8, rx(r"testicular vein")),
    ("bladder", "Urinary bladder (context)", 0xd9b27a, rx(r"^urinary bladder$")),
]
groups = [{"key": k, "label": lab, "color": c, "ids": [], "keep": "auto"} for k, lab, c, _ in GROUPS]
for pid in dict.fromkeys(pool):
    hits = [i for i, g in enumerate(GROUPS) if g[3](parts[pid]["name"])]
    assert len(hits) == 1, (parts[pid]["name"], hits)
    groups[hits[0]]["ids"].append(pid)
for g in groups:
    assert g["ids"], g["key"]
write_scene("repro-male", groups)
print({g["label"]: len(g["ids"]) for g in groups})


names = lambda *n: [p["id"] for p in atlas["parts"] if p["name"] in n]
write_scene("pelvis", [
    {"key": "bones", "label": "Hip bones, sacrum and lumbar spine", "color": 0xd9d2c3, "keep": 0.12,
     "ids": names("Left hip bone", "Right hip bone", "Sacrum", "Fifth lumbar vertebra", "Fourth lumbar vertebra")},
    {"key": "bladder", "label": "Urinary bladder and rectum", "color": 0xd9b27a, "keep": 0.2, "ids": names("Urinary bladder", "Rectum")},
    {"key": "repro-male", "label": "Male reproductive organs", "color": 0xd99a8a, "keep": 0.3, "ids": REPRO + names("Urethra")},
])
