"""Quoted content for the brain workstation. Usage: content_brain.py <openstax dir> <site data dir> <bodyparts model dir>"""
import json, re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contentlib import Module, slug
OS, OUT, SRC, PARTOF = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
import csv, collections
_pc, _pn = collections.defaultdict(set), {}
for r in csv.reader(open(PARTOF, encoding="utf-8"), delimiter="\t"):  # official BodyParts3D PART-OF tree
    if len(r) >= 3 and r[2].startswith("FJ"):
        _pc[r[2]].add(r[1])
REGIONS = ("telencephalon", "diencephalon", "epithalamus", "hypothalamus", "midbrain", "pons", "medulla oblongata", "metencephalon",
           "hindbrain", "cerebellum", "brainstem", "ventricular system of brain")
partof = {f: sorted(c for c in cs if c in REGIONS) for f, cs in _pc.items()}
CNS = Module(f"{OS}/m46533.cnxml", "13.2", slug("13.2", "The Central Nervous System"), "The Central Nervous System")
CIR = Module(f"{OS}/m46719.cnxml", "13.3", slug("13.3", "Circulation and the Central Nervous System"), "Circulation and the Central Nervous System")
atlas = json.load(open(f"{SRC}/atlas.json"))
small = {}
for c in atlas["concepts"]:
    if len(c["elements"]) <= 60:
        for e in c["elements"]:
            small.setdefault(e, set()).add(c["name"])

S = lambda m, p, s: (m, p, s)
T = {
 "overview": [S(CNS, "fs-id1518907", "The spinal cord is a single structure"), S(CNS, "fs-id1476424", "The wrinkled portion is the cerebral cortex"),
              S(CNS, "fs-id1476424", "It separates the cerebrum into two distinct halves"), S(CNS, "fs-id1476424", "Deep within the cerebrum")],
 "cortex": [S(CNS, "fs-id1298164", "The cerebrum is covered by a continuous layer"), S(CNS, "fs-id1298164", "A gyrus (plural = gyri)"),
            S(CNS, "fs-id1298164", "The pattern of these folds"), S(CNS, "fs-id1137638", "Superior to the lateral sulcus"),
            S(CNS, "fs-id1137638", "The posterior region of the cortex")],
 "precentral": [S(CNS, "fs-id1119780", "Anterior to the central sulcus is the frontal lobe"), S(CNS, "fs-id1119780", "The precentral gyrus is the primary motor cortex")],
 "postcentral": [S(CNS, "fs-id1319713", "The main sensation associated with the parietal lobe"), S(CNS, "fs-id1319713", "Posterior to the central sulcus is the postcentral")],
 "occipital": [S(CNS, "fs-id1137638", "The posterior region of the cortex"), S(CNS, "fs-id1163314", "Areas 17 and 18 in the occipital lobe")],
 "suptemporal": [S(CNS, "fs-id2055928", "The temporal lobe is associated with primary auditory")],
 "white": [S(CNS, "fs-id1476424", "Deep within the cerebrum")],
 "basal": [S(CNS, "fs-id793857", "The basal nuclei are a set of nuclei"), S(CNS, "fs-id1433950", "The major structures of the basal nuclei")],
 "caudate": [S(CNS, "fs-id1433950", "The major structures of the basal nuclei"), S(CNS, "fs-id1433950", "The caudate is a long nucleus"),
             S(CNS, "fs-id1433950", "Together, the caudate and putamen")],
 "putamen": [S(CNS, "fs-id1433950", "The major structures of the basal nuclei"), S(CNS, "fs-id1433950", "The putamen is mostly deep"),
             S(CNS, "fs-id1433950", "Together, the caudate and putamen")],
 "pallidus": [S(CNS, "fs-id1433950", "The major structures of the basal nuclei"), S(CNS, "fs-id1433950", "The globus pallidus is a layered nucleus"),
              S(CNS, "fs-id1433950", "The globus pallidus has two subdivisions")],
 "hippo": [S(CNS, "fs-id793857", "The hippocampus and amygdala are medial-lobe")],
 "dien": [S(CNS, "fs-id2026939", "The diencephalon is deep beneath"), S(CNS, "fs-id2026939", "The diencephalon can be described as any region")],
 "thalamus": [S(CNS, "fs-id1234023", "The thalamus is a collection of nuclei"), S(CNS, "fs-id1234023", "All sensory information, except")],
 "hypothalamus": [S(CNS, "fs-id1490316", "Inferior and slightly anterior"), S(CNS, "fs-id1490316", "The hypothalamus is a collection"),
                  S(CNS, "fs-id1490316", "The hypothalamus is the executive region")],
 "pineal": [S(CNS, "fs-id2026939", "There are other structures, such as the epithalamus")],
 "brainstem": [S(CNS, "fs-id1523364", "The structure emerges from the ventral surface"), S(CNS, "fs-id1523364", "The midbrain coordinates"),
               S(CNS, "fs-id1523364", "The pons and the medulla regulate")],
 "midbrain": [S(CNS, "fs-id890816", "One of the original regions"), S(CNS, "fs-id890816", "The cerebral aqueduct passes through")],
 "inferiorcoll": [S(CNS, "fs-id1282943", "The tectum is composed of four bumps"), S(CNS, "fs-id1282943", "The inferior colliculus is the inferior pair")],
 "superiorcoll": [S(CNS, "fs-id1282943", "The tectum is composed of four bumps"), S(CNS, "fs-id1282943", "The superior colliculus is the superior pair")],
 "pons": [S(CNS, "fs-id1179935", "The word pons comes from"), S(CNS, "fs-id1179935", "It is visible on the anterior surface"),
          S(CNS, "fs-id1179935", "The pons is the main connection")],
 "medulla": [S(CNS, "fs-id2166609", "The medulla is the region known"), S(CNS, "fs-id2166609", "The initial portion of the name")],
 "cerebellum": [S(CNS, "fs-id1520379", "The cerebellum, as the name suggests"), S(CNS, "fs-id1520379", "The cerebellum is largely responsible"),
                S(CNS, "fs-id1520379", "It accounts for approximately 10 percent")],
 "lateralv": [S(CIR, "fs-id1490421", "There are four ventricles within the brain"), S(CIR, "fs-id1490421", "The first two are named the lateral")],
 "ivf": [S(CIR, "fs-id1490421", "These ventricles are connected to the third"), S(CIR, "fs-id2855889", "The interventricular foramina connect")],
 "thirdv": [S(CIR, "fs-id1490421", "The third ventricle is the space between"), S(CIR, "fs-id1136775", "The third ventricle is the space bounded")],
 "aqueduct": [S(CIR, "fs-id1136775", "The cerebral aqueduct opens just inferior"), S(CIR, "fs-id1136775", "The tectum and tegmentum of the midbrain")],
 "fourthv": [S(CIR, "fs-id1136775", "The aqueduct opens up into the fourth"), S(CIR, "fs-id1136775", "The floor of the fourth ventricle"),
             S(CIR, "fs-id1136775", "The fourth ventricle then narrows")],
 "canal": [S(CIR, "fs-id1136775", "The fourth ventricle then narrows")],
 "choroid": [S(CIR, "fs-id1187632", "In some of these spaces, CSF is produced"), S(CIR, "fs-id1298119", "The choroid plexuses are found in all four")],
 "pituitary": [S(CNS, "fs-id1490316", "The hypothalamus is the executive region")],
 "ica": [S(CIR, "fs-id1828457", "The next branches give rise to the common carotid"), S(CIR, "fs-id1333836", "The internal carotid artery enters the cranium")],
 "vert": [S(CIR, "fs-id1333836", "A second set of vessels that supply the CNS"), S(CIR, "fs-id1333836", "The vertebral arteries enter the cranium")],
 "basilar": [S(CIR, "fs-id1333836", "The two vertebral arteries then merge")],
 "spinal": [S(CIR, "fs-id1333836", "Branches off the left and right vertebral arteries merge")],
 "willis": [S(CIR, "fs-id1966794", "The circle of Willis is a specialized arrangement")],
 "none": [],
}
topics = {k: [m.sent(p, s) for m, p, s in v] for k, v in T.items()}
NAMELESS = "This source does not describe this structure by name."


def evidence(m):
    keep = [c for c in sorted(small.get(m["id"], ())) if c in ("hypothalamus", "gray matter of hypothalamus", "zone of diencephalon",
            "gyrus of neuraxis", "segment of gyrus of cerebral hemisphere", "lobe of cerebral hemisphere", "lobule of cerebral hemisphere",
            "white matter of neuraxis", "white matter of telencephalon", "segment of white matter of neuraxis", "commissure of neuraxis")]
    out = ("It is grouped here by its FMA concept in the dataset: " + ", ".join(keep) + ".") if keep else ""
    po = partof.get(m["id"])
    if po:
        out += (" " if out else "") + "The official BodyParts3D part-of tree places it in: " + ", ".join(po) + "."
    return out


WILLIS = {f for f, cs in _pc.items() if "cerebral arterial circle" in cs}
TREES = ["left internal carotid artery", "right internal carotid artery", "left vertebral artery", "right vertebral artery",
         "branch of middle cerebral artery", "branch of anterior cerebral artery", "zone of middle cerebral artery"]
_tree = {}
for c in atlas["concepts"]:
    if c["name"] in TREES:
        for e in c["elements"]:
            _tree.setdefault(e, []).append(c["name"])


def artery_note(m):
    t = [x for x in _tree.get(m["id"], []) if x != m["name"].lower()]
    out = "This source does not describe this artery by name."
    if t:
        out += " The dataset lists it under: " + ", ".join(sorted(set(t))) + "."
    return out


def topic_for(m):
    n, g = re.sub(r"^(Left|Right) ", "", m["name"]), m["group"]
    if g == "arteries":
        if n == "internal carotid artery": return "ica", "The lower part of this artery, below the brain, is cut short in this view."
        if n == "vertebral artery": return "vert", "The lower part of this artery, below the brain, is cut short in this view."
        if n == "Basilar artery": return "basilar", None
        if n == "Anterior spinal artery" or n == "anterior spinal artery": return "spinal", None
        if m["id"] in WILLIS: return "willis", "The official BodyParts3D part-of tree lists this artery as part of the cerebral arterial circle (circle of Willis). " + artery_note(m)
        return "none", artery_note(m)
    rules = [
        (n == "precentral gyrus", "precentral", None), (n == "postcentral gyrus", "postcentral", None),
        (n == "occipital lobe", "occipital", None),
        ("superior temporal gyrus" in n, "suptemporal", "The source speaks of the superior temporal lobe. The dataset names this mesh as part of the superior temporal gyrus."),
        (g == "cortex", "cortex", NAMELESS + " " + evidence(m)),
        (n == "Corpus callosum", "white", None), (g == "white", "none", NAMELESS + " " + evidence(m)),
        (n == "caudate nucleus", "caudate", None), (n == "putamen", "putamen", None), (n == "globus pallidus", "pallidus", None),
        (g == "hippo", "hippo", None),
        (n == "thalamus", "thalamus", None), (n == "Hypothalamus", "hypothalamus", None), (n == "Pineal body", "pineal", "The source calls this the pineal gland."),
        (n == "stria medullaris of thalamus", "dien", NAMELESS + " The source counts any brain region with “thalamus” in its name as part of the diencephalon."),
        (g == "dien", "dien", NAMELESS + " " + evidence(m)),
        (n == "Midbrain", "midbrain", None), (n == "inferior colliculus", "inferiorcoll", None), (n == "superior colliculus", "superiorcoll", None),
        (n == "Pons", "pons", None), (n == "Medulla oblongata", "medulla", None),
        (n == "Peduncle of midbrain", "midbrain", NAMELESS + " The dataset names it as part of the midbrain."),
        (n == "Cerebellum", "cerebellum", None),
        (n == "lateral ventricle", "lateralv", None), (n == "Interventricular foramen", "ivf", None), (n == "Third ventricle", "thirdv", None),
        (n == "Cerebral aqueduct", "aqueduct", None), (n == "Fourth ventricle", "fourthv", None), (n == "Central canal of spinal cord", "canal", None),
        (n == "Choroid plexus of cerebral hemisphere", "choroid", "The dataset files this mesh under the sensory system."),
        (g == "context", "pituitary", "Shown for context. The passage mentions the pituitary gland."),
        (g == "other", "none", "Neither this source nor the dataset's concepts say which brain region this structure belongs to, so it is listed on its own. " + evidence(m)),
    ]
    for ok, t, note in rules:
        if ok:
            return t, (note or None)
    raise SystemExit("unmapped " + m["name"])


meta = json.load(open(f"{OUT}/brain.json"))
mt = {}
for m in meta["meshes"]:
    t, note = topic_for(m)
    mt[m["id"]] = {"topic": t, "note": note.strip() if note else None}
flow = [
    {"title": "Lateral ventricles", "parts": ["Left lateral ventricle", "Right lateral ventricle"], "passage": CIR.sent("fs-id1490421", "The first two are named the lateral")},
    {"title": "Choroid plexus", "parts": ["Choroid plexus of cerebral hemisphere"], "passage": CIR.sent("fs-id1187632", "In some of these spaces, CSF is produced")},
    {"title": "Interventricular foramina", "parts": ["Interventricular foramen"], "passage": CIR.sent("fs-id1490421", "These ventricles are connected to the third")},
    {"title": "Third ventricle", "parts": ["Third ventricle"], "passage": CIR.sent("fs-id1490421", "The third ventricle is the space between")},
    {"title": "Cerebral aqueduct", "parts": ["Cerebral aqueduct"], "passage": CIR.sent("fs-id1136775", "The cerebral aqueduct opens just inferior")},
    {"title": "Fourth ventricle", "parts": ["Fourth ventricle"], "passage": CIR.sent("fs-id1136775", "The aqueduct opens up into the fourth")},
    {"title": "Central canal", "parts": ["Central canal of spinal cord"], "passage": CIR.sent("fs-id1136775", "The fourth ventricle then narrows")},
]
names = {m["name"] for m in meta["meshes"]}
for f in flow:
    for n in f["parts"]:
        assert n in names, n
json.dump({"topics": topics, "meshTopic": mt, "flow": flow,
           "gaps": ["The meninges and the spinal cord itself (apart from its central canal) are not included.", "Of the brain's blood vessels, only the internal carotid and vertebral artery branches are shown (the Arteries button). Veins are not shown."],
           "notes": ["The dataset's own brain concept leaves out many brain structures, so this workstation groups meshes by quoted textbook sentences where they exist and by each mesh's FMA concept otherwise. Structures neither source places in a region are listed under Other."]},
          open(f"{OUT}/content-brain.json", "w"), indent=0)
nameless = sum(1 for v in mt.values() if v["note"] and v["note"].startswith(NAMELESS))
print(len(topics), "topics,", len(mt), "of", len(meta["meshes"]), "meshes mapped,", nameless, "without a passage of their own")
