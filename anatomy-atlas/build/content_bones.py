"""Quoted content for the six bone workstations. Usage: content_bones.py <openstax dir> <site data dir>

Each bone gets the opening sentences of the OpenStax section whose heading names it; where one section covers several
bones (atlas and axis, parts of the sternum, individual carpal and tarsal bones), the first sentence that names the
bone is added. Every sentence goes through contentlib's word-for-word and figure-reference checks.
The script also checks that each bone's section really sits inside the group section it is shown under.
"""
import json, re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contentlib import Module, slug
OS, OUT = sys.argv[1], sys.argv[2]


def mod(mid, number, title):
    return Module(f"{OS}/{mid}.cnxml", number, slug(number, title), title)


DIV = mod("m46344", "7.1", "Divisions of the Skeletal System")
SKU = mod("m46355", "7.2", "The Skull")
VER = mod("m46352", "7.3", "The Vertebral Column")
THO = mod("m46350", "7.4", "The Thoracic Cage")
PEC = mod("m46374", "8.1", "The Pectoral Girdle")
UPP = mod("m46368", "8.2", "Bones of the Upper Limb")
PEL = mod("m46375", "8.3", "The Pelvic Girdle and Pelvis")
LOW = mod("m46364", "8.4", "Bones of the Lower Limb")
bare = lambda n: re.sub(r"^(Left|Right) ", "", n)
TEXT_NAME = {"triquetral": "triquetrum"}  # dataset name -> the textbook's name for the same bone

# bare dataset name (regex) -> (module, section heading, word to find a bone-specific sentence or None, parent section to check)
BONES = {
    "skull": [
        (r"^parietal bone$", SKU, "Parietal Bone", None, "Bones of the Brain Case"),
        (r"^temporal bone$", SKU, "Temporal Bone", None, "Bones of the Brain Case"),
        (r"^Frontal bone$", SKU, "Frontal Bone", None, "Bones of the Brain Case"),
        (r"^Occipital bone$", SKU, "Occipital Bone", None, "Bones of the Brain Case"),
        (r"^Sphenoid bone$", SKU, "Sphenoid Bone", None, "Bones of the Brain Case"),
        (r"^Ethmoid$", SKU, "Ethmoid Bone", None, "Bones of the Brain Case"),
        (r"^maxilla$", SKU, "Maxillary Bone", None, "Facial Bones of the Skull"),
        (r"^palatine bone$", SKU, "Palatine Bone", None, "Facial Bones of the Skull"),
        (r"^zygomatic bone$", SKU, "Zygomatic Bone", None, "Facial Bones of the Skull"),
        (r"^nasal bone$", SKU, "Nasal Bone", None, "Facial Bones of the Skull"),
        (r"^lacrimal bone$", SKU, "Lacrimal Bone", None, "Facial Bones of the Skull"),
        (r"^inferior nasal concha$", SKU, "Inferior Nasal Conchae", None, "Facial Bones of the Skull"),
        (r"^Vomer$", SKU, "Vomer Bone", None, "Facial Bones of the Skull"),
        (r"^Mandible$", SKU, "Mandible", None, "Facial Bones of the Skull"),
        (r"^Hyoid bone$", SKU, "Hyoid Bone", None, None),
    ],
    "spine": [
        (r"^Atlas$", VER, "Cervical Vertebrae", "atlas", "Regional Modifications of Vertebrae"),
        (r"^Axis$", VER, "Cervical Vertebrae", "axis", "Regional Modifications of Vertebrae"),
        (r"^\w+ cervical vertebra$", VER, "Cervical Vertebrae", None, "Regional Modifications of Vertebrae"),
        (r"^\w+ thoracic vertebra$", VER, "Thoracic Vertebrae", None, "Regional Modifications of Vertebrae"),
        (r"^\w+ lumbar vertebra$", VER, "Lumbar Vertebrae", None, "Regional Modifications of Vertebrae"),
        (r"^Sacrum$", VER, "Sacrum and Coccyx", "sacrum", "Regional Modifications of Vertebrae"),
        (r"^Intervertebral disk", VER, "Intervertebral Disc", None, "Intervertebral Discs and Ligaments of the Vertebral Column"),
    ],
    "thorax": [
        (r"^Body of sternum$", THO, "Sternum", "body", None),
        (r"^Manubrium$", THO, "Sternum", "manubrium", None),
        (r"^Xiphoid process$", THO, "Sternum", "xiphoid", None),
        (r"^\w+ rib$", THO, "Ribs", None, None),
        (r"costal cartilage$", THO, "Rib Classifications", "costal cartilage", "Ribs"),
    ],
    "upper": [
        (r"^clavicle$", PEC, "Clavicle", None, None), (r"^scapula$", PEC, "Scapula", None, None),
        (r"^humerus$", UPP, "Humerus", None, None), (r"^ulna$", UPP, "Ulna", None, None), (r"^radius$", UPP, "Radius", None, None),
        (r"^(scaphoid|lunate|triquetral|pisiform|trapezium|trapezoid|capitate|hamate)$", UPP, "Carpal Bones", "<name>", None),
        (r"metacarpal bone$", UPP, "Metacarpal Bones", None, None),
        (r"phalanx of", UPP, "Phalanx Bones", None, None),
    ],
    "pelvis": [(r"^hip bone$", PEL, "Hip Bone", None, None), (r"^Sacrum$", VER, "Sacrum and Coccyx", "sacrum", None)],
    "lower": [
        (r"^femur$", LOW, "Femur", None, None), (r"^patella$", LOW, "Patella", None, None),
        (r"^tibia$", LOW, "Tibia", None, None), (r"^fibula$", LOW, "Fibula", None, None),
        (r"^(calcaneus|talus|cuboid bone|(intermediate|lateral|medial) cuneiform bone|Navicular bone of (left|right) foot)$", LOW, "Tarsal Bones", "<tarsal>", None),
        (r"metatarsal bone$", LOW, "Metatarsal Bones", None, None),
        (r"phalanx of", LOW, "Phalanges", None, None),
        (r"^Sesamoid bone of (left|right) foot$", LOW, "Patella", "sesamoid", None),
    ],
}
GROUP_TEXT = {  # group key -> (module, section heading)
    "braincase": (SKU, "Bones of the Brain Case"), "facial": (SKU, "Facial Bones of the Skull"), "hyoid": (SKU, "Hyoid Bone"),
    "cervical": (VER, "Cervical Vertebrae"), "thoracic": (VER, "Thoracic Vertebrae"), "lumbar": (VER, "Lumbar Vertebrae"),
    "sacrum": (VER, "Sacrum and Coccyx"), "disc": (VER, "Intervertebral Disc"),
    "sternum": (THO, "Sternum"), "ribs": (THO, "Ribs"), "cartilage": (THO, "Rib Classifications"),
    "clavicle": (PEC, "Clavicle"), "scapula": (PEC, "Scapula"), "humerus": (UPP, "Humerus"), "ulna": (UPP, "Ulna"), "radius": (UPP, "Radius"),
    "carpal": (UPP, "Carpal Bones"), "metacarpal": (UPP, "Metacarpal Bones"), "phalanx": (UPP, "Phalanx Bones"),
    "hip": (PEL, "Hip Bone"), "femur": (LOW, "Femur"), "patella": (LOW, "Patella"), "tibia": (LOW, "Tibia"), "fibula": (LOW, "Fibula"),
    "tarsal": (LOW, "Tarsal Bones"), "metatarsal": (LOW, "Metatarsal Bones"), "phalanges": (LOW, "Phalanges"), "sesamoid": (LOW, "Patella"),
}
OVERVIEW = {"skull": SKU, "spine": VER, "thorax": THO, "upper": UPP, "pelvis": PEL, "lower": LOW}
GAPS = {
    "skull": ["The teeth are not part of this workstation. They appear in the whole-body view only."],
    "spine": ["The dataset has no mesh for the coccyx."],
    "thorax": ["The dataset has costal cartilage meshes for ribs 1 to 7 only."],
    "upper": [], "pelvis": [], "lower": [],
}
NOTES = {"pelvis": ["The sacrum also appears in the vertebral column workstation."],
         "lower": ["The hip bones are shown in the pelvis workstation, as in OpenStax section 8.3."]}

for region, rules in BONES.items():
    meta = json.load(open(f"{OUT}/bones-{region}.json"))
    topics, mt = {}, {}
    for m in meta["meshes"]:
        n = bare(m["name"])
        hit = [r for r in rules if re.search(r[0], n)]
        assert len(hit) == 1, (region, m["name"], len(hit))
        _, M, sec, word, parent = hit[0]
        if parent:  # the bone's own section must sit inside the group it is shown under
            assert all(parent in M.path[p] for p in M.section_pids(sec)), (sec, parent)
        w = {"<name>": n, "<tarsal>": re.sub(r" bone( of (left|right) foot)?$", "", n).replace("intermediate ", "").replace("lateral ", "").replace("medial ", "")}.get(word, word) if word else None
        alias = TEXT_NAME.get(w)
        w = alias or w
        key = sec + "|" + (w or "")
        if key not in topics:
            q = M.first(sec, 2)
            note = None
            if alias:
                note = f"The dataset calls this bone the {n}; the textbook calls it the {alias}."
            if w == "sesamoid":
                note = "The source describes sesamoid bones in general, in its section on the patella. It does not describe the sesamoid bones of the foot by name."
            if w:
                extra = M.mention(sec, w)
                if extra:
                    q = q + [extra] if extra["text"] not in [x["text"] for x in q] else q
                elif not note:
                    note = f"This section of the source does not mention the {w} by name; its general passage is shown."
            topics[key] = {"passages": q, "note": note}
        mt[m["id"]] = {"topic": key, "note": topics[key]["note"]}
    out_topics = {k: v["passages"] for k, v in topics.items()}
    out_topics["overview"] = OVERVIEW[region].intro(3) or OVERVIEW[region].first(meta["groups"][0]["label"], 2)
    for g in meta["groups"]:
        M, sec = GROUP_TEXT[g["key"]]
        out_topics["group:" + g["key"]] = M.first(sec, 1)
    flow = [{"title": g["label"], "groups": [g["key"]], "passage": out_topics["group:" + g["key"]][0]} for g in meta["groups"]]
    json.dump({"topics": out_topics, "meshTopic": mt, "flow": flow, "gaps": GAPS[region], "notes": NOTES.get(region, [])},
              open(f"{OUT}/content-bones-{region}.json", "w"), indent=0)
    unnamed = [k for k, v in topics.items() if v["note"]]
    print(region, len(mt), "meshes,", len(out_topics), "topics,", len(flow), "tour steps; bones with a note:", unnamed)
