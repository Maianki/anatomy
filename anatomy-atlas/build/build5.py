"""Brain workstation scene and head context.

The dataset's own "brain" concept leaves out many brain structures (corpus callosum, thalamus, basal nuclei...),
so the candidate pool is every nervous/cardiac/endocrine mesh in the head that is not a peripheral nerve, plus the
choroid plexus meshes (filed under "sensory" in the dataset). Each mesh is then placed in a group by a rule that
names its evidence: an OpenStax sentence (see content_brain.py) or the mesh's own FMA concepts.
"""
import re, sys
sys.argv = sys.argv[:3]
exec(open(__file__.replace("build5.py", "common.py")).read())

small = [c for c in atlas["concepts"] if len(c["elements"]) <= 60]
fma = {}
for c in small:
    for e in c["elements"]:
        fma.setdefault(e, set()).add(c["name"])
brain_concept = set(elements("brain"))
NOT_BRAIN = {"Interpeduncular fossa": "is a subarachnoid space, not brain tissue",
             "Tentorium cerebelli": "is part of the dura mater, not brain tissue"}
pool, left_out = [], []
for p in atlas["parts"]:
    if p["system"] in ("nervous", "cardiac", "endocrine") and p["bounds"][0][1] > 1.45 and \
            (p["id"] in brain_concept or not re.search(r"nerve|ganglion|branch", p["name"], re.I)):
        if p["name"] in NOT_BRAIN:
            left_out.append({"id": p["id"], "name": p["name"], "fma": p["conceptId"], "why": NOT_BRAIN[p["name"]]})
        else:
            pool.append(p["id"])
pool += [p["id"] for p in atlas["parts"] if p["name"] == "Choroid plexus of cerebral hemisphere"]
# Side check: a mesh whose name says left/right but whose centre lies on the other side of the midline (by more than 5 mm)
# contradicts itself. Patient left is +X in this dataset.
kept = []
for i in pool:
    s = re.search(r"\b(left|right)\b", parts[i]["name"], re.I)
    x = (parts[i]["bounds"][0][0] + parts[i]["bounds"][1][0]) / 2
    if s and (s.group(1).lower() == "left") != (x > 0) and abs(x) > 0.005:
        left_out.append({"id": i, "name": parts[i]["name"], "fma": parts[i]["conceptId"],
                         "why": "lies on the %s side of the body although its name says %s, so the name and position contradict each other in the source data"
                                % ("right" if x < 0 else "left", s.group(1).lower())})
    else:
        kept.append(i)
pool = kept
print("left out:", [(e["name"], e["why"][:40]) for e in left_out])


def F(*concepts):
    return lambda p: bool(fma.get(p["id"], set()) & set(concepts))


def N(*pat):
    r = re.compile("|".join(pat), re.I)
    return lambda p: bool(r.search(p["name"]))


ORDER = [  # first matching rule wins; the evidence for each rule is noted
    ("hippo", "Hippocampus and amygdala", 0xc9a0dc, N(r"hippocampus$", r"amygdala$")),            # OpenStax fs-id793857
    ("basal", "Basal nuclei", 0xe0b06c, N(r"caudate nucleus", r"putamen", r"globus pallidus")),     # OpenStax fs-id1433950
    ("ventricles", "Ventricles and CSF spaces", 0x6fb3e0,
     N(r"ventricle$", r"aqueduct", r"Interventricular foramen", r"Central canal", r"Choroid plexus")),  # OpenStax fs-id1490421 / FMA ventricular system
    ("cerebellum", "Cerebellum", 0x9fd3a8, N(r"^Cerebellum$")),                                    # OpenStax fs-id1520379
    ("brainstem", "Brain stem", 0xe08a7a,
     N(r"^Midbrain$", r"^Pons$", r"^Medulla oblongata$", r"^(Left|Right) (inferior|superior) colliculus$", r"^Peduncle of midbrain$")),  # OpenStax fs-id1523364, fs-id1282943
    ("dien", "Diencephalon", 0x7fc6c0,
     lambda p: N(r"thalamus$", r"^Hypothalamus$", r"^Pineal body$")(p) or F("hypothalamus", "gray matter of hypothalamus", "zone of diencephalon")(p)),
    ("cortex", "Cerebral cortex: gyri and lobes", 0xd9b8a8,
     F("gyrus of neuraxis", "segment of gyrus of cerebral hemisphere", "lobe of cerebral hemisphere", "lobule of cerebral hemisphere")),
    ("white", "White matter, tracts and commissures", 0xf0ece0,
     F("white matter of neuraxis", "white matter of telencephalon", "segment of white matter of neuraxis", "commissure of neuraxis")),
    ("context", "Pituitary gland (context)", 0xc98a5a, N(r"^Pituitary gland$")),
    ("other", "Other named brain structures", 0xa8b4c0, lambda p: True),
]
groups = [{"key": k, "label": l, "color": c, "ids": [], "keep": "auto"} for k, l, c, _ in ORDER]
gi = {g["key"]: g for g in groups}
for i in dict.fromkeys(pool):
    key = next(k for k, _, _, f in ORDER if f(parts[i]))
    gi[key]["ids"].append(i)
for g in groups:
    print(g["key"], len(g["ids"]), sorted(set(re.sub(r"^(Left|Right) ", "", parts[i]["name"]) for i in g["ids"]))[:40])
write_scene("brain", groups)
meta = json.loads((OUT / "brain.json").read_text())
meta["excluded"] = left_out
(OUT / "brain.json").write_text(json.dumps(meta, separators=(",", ":")))

# head context: skull and upper cervical spine, with the brain
bones = [p["id"] for p in atlas["parts"] if p["system"] == "skeletal" and p["bounds"][0][1] > 1.47 and
         not re.search(r"tooth|incisor|canine|molar|premolar|hyoid", p["name"], re.I)]
write_scene("head", [
    {"key": "bones", "label": "Skull", "color": 0xd9d2c3, "ids": bones, "keep": 0.1},
    {"key": "brain", "label": "Brain", "color": 0xd9a7a0, "ids": [i for g in groups if g["key"] != "context" for i in g["ids"]], "keep": 0.13},
])
print("head bones:", len(bones))
