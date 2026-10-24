"""Quoted text for organs shown only in the whole-body view (single meshes, no workstation).
Usage: content_body.py <openstax dir> <site data dir>"""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contentlib import Module, slug
OS, OUT = sys.argv[1], sys.argv[2]
LYM = Module(f"{OS}/m46563.cnxml", "21.1", slug("21.1", "Anatomy of the Lymphatic and Immune Systems"), "Anatomy of the Lymphatic and Immune Systems")
LUN = Module(f"{OS}/m46551.cnxml", "22.2", slug("22.2", "The Lungs"), "The Lungs")
out = {
    "spleen": [LYM.sent("fs-id1468423", "It is about 12 cm"), LYM.sent("fs-id1468423", "The spleen is a fragile organ")],
    "diaphragm": [LUN.sent("fs-id2627237", "The diaphragm is a dome-shaped muscle")],
}
notes = {"spleen": "The spleen in this model measures 10.7 cm along its longest axis (build/measure.py). The quoted text gives about 12 cm."}
json.dump({"text": out, "notes": notes}, open(f"{OUT}/content-body.json", "w"), indent=0)
print({k: len(v) for k, v in out.items()})
