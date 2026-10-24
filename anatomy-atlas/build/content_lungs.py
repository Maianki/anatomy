import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contentlib import Module
OS, LUNGS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
BASE = "https://openstax.org/books/anatomy-and-physiology-2e/pages/"
L = Module(OS + "/m46551.cnxml", "22.2", BASE + "22-2-the-lungs", "The Lungs")
A = Module(OS + "/m46548.cnxml", "22.1", BASE + "22-1-organs-and-structures-of-the-respiratory-system", "Organs and Structures of the Respiratory System")
T = {
 "overview": [(L, "fs-id2627237", "The lungs are pyramid-shaped"), (L, "fs-id2627237", "The right lung is shorter and wider"),
              (L, "fs-id2627237", "The apex of the lung"), (L, "fs-id2627237", "The costal surface"),
              (L, "fs-id2627237", "The mediastinal surface"), (L, "fs-id2717313", "The right lung consists of three"),
              (L, "fs-id2717313", "The left lung consists of two")],
 "lobes": [(L, "fs-id2717313", "Each lung is composed of smaller"), (L, "fs-id2717313", "Fissures separate"),
           (L, "fs-id2717313", "The right lung consists of three"), (L, "fs-id2717313", "The left lung consists of two")],
 "segment": [(L, "fs-id2717313", "A bronchopulmonary segment is"), (L, "fs-id2717313", "Each segment receives air")],
 "trachea": [(A, "fs-id2058199", "The trachea is formed by"), (A, "fs-id2058199", "The esophagus borders"),
             (A, "fs-id2033350", "The trachea branches into")],
 "mainbronchi": [(A, "fs-id2033350", "The trachea branches into"), (A, "fs-id2033350", "Rings of cartilage"),
                 (A, "fs-id2033350", "The primary bronchi enter")],
 "btree": [(A, "fs-id2033350", "The bronchi continue to branch"), (A, "fs-id2033350", "A bronchial tree (or respiratory tree)"),
           (L, "fs-id2717313", "Each segment receives air")],
 "segart": [(L, "fs-id2144132", "The pulmonary artery branches multiple"), (L, "fs-id2717313", "Each segment receives air")],
 "ptrunk": [(L, "fs-id2144132", "The pulmonary artery is an artery"), (L, "fs-id2144132", "The pulmonary artery branches multiple")],
 "veins": [(L, "fs-id2144132", "Once the blood is oxygenated")],
}
topics = {k: [m.sent(p, s) for m, p, s in v] for k, v in T.items()}
GENERAL_SEG = "This source describes bronchopulmonary segments in general. It does not describe individual segments by name."
meta = json.load(open(LUNGS))
mt = {}
for m in meta["meshes"]:
    n, g = m["name"], m["group"]
    if n == "Trachea": t, note = "trachea", None
    elif "main bronchus" in n: t, note = "mainbronchi", None
    elif g == "bronchi": t, note = "btree", GENERAL_SEG
    elif g == "arteries": t, note = "segart", (GENERAL_SEG if m.get("seg") else "This source has no passage about this specific vessel. The passage below covers the group it belongs to.")
    elif g == "veins": t, note = "veins", GENERAL_SEG
    elif g == "hilum-arteries": t, note = "ptrunk", None
    elif g == "hilum-veins": t, note = "veins", None
    else: raise SystemExit("unmapped " + n)
    mt[m["id"]] = {"topic": t, "note": note}
flow = [
 {"title": "Trachea", "parts": ["Trachea"], "passage": A.sent("fs-id2033350", "The trachea branches into")},
 {"title": "Main bronchi", "parts": ["Right main bronchus proper", "Left main bronchus"], "passage": A.sent("fs-id2033350", "The primary bronchi enter")},
 {"title": "Segmental bronchial trees", "groups": ["bronchi"], "passage": L.sent("fs-id2717313", "Each segment receives air")},
 {"title": "Pulmonary trunk and arteries", "groups": ["hilum-arteries"], "passage": L.sent("fs-id2144132", "The pulmonary artery is an artery")},
 {"title": "Segmental pulmonary arteries", "groups": ["arteries"], "passage": L.sent("fs-id2144132", "The pulmonary artery branches multiple")},
 {"title": "Segmental and pulmonary veins", "groups": ["veins", "hilum-veins"], "passage": L.sent("fs-id2144132", "Once the blood is oxygenated")},
]
names = {m["name"] for m in meta["meshes"]}
for f in flow:
    for n in f.get("parts", []): assert n in names, n
json.dump({"topics": topics, "meshTopic": mt, "flow": flow}, open(OUT, "w"), indent=0)
print(len(topics), "topics,", len(mt), "of", len(meta["meshes"]), "meshes mapped")
for k in ("overview", "segment"): print(k, [p["text"] for p in topics[k]])
