"""Build content.json: verbatim OpenStax A&P 2e (19.1 Heart Anatomy, module m46676) sentences, matched by prefix."""
import json, re, sys, xml.etree.ElementTree as ET
CNXML, HEART, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ns = "{http://cnx.rice.edu/cnxml}"
root = ET.parse(CNXML).getroot()
paras, section_of = {}, {}


def walk(el, sec):
    for ch in el:
        tag = ch.tag.replace(ns, "")
        if tag == "section":
            t = ch.find(ns + "title")
            walk(ch, re.sub(r"\s+", " ", "".join(t.itertext())).strip() if t is not None else sec)
        elif tag == "para":
            paras[ch.get("id")] = re.sub(r"\s+", " ", "".join(ch.itertext())).strip()
            section_of[ch.get("id")] = sec
        else:
            walk(ch, sec)


walk(root.find(ns + "content"), "Heart Anatomy")


def sent(pid, prefix):
    p = paras[pid]
    i = p.index(prefix)  # raises if the text is not in the source
    m = re.search(r"\.[\u201d\"\u2019]?(?=\s|$)", p[i:])
    s = p[i:i + m.end()]
    assert not re.search(r"\(\s*\)|\(see \)|\([a-z]\)| shows | in \.$", s), s  # skip sentences that point at missing figures
    return {"text": s, "pid": pid, "label": "19.1 " + section_of[pid],
            "url": "https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy"}


T = {
 "overview": [("fs-id1892589", "The human heart is located within"), ("fs-id1892589", "The dorsal surface of the heart"),
              ("fs-id1892589", "The great veins, the superior"), ("fs-id1892589", "The inferior tip of the heart"),
              ("fs-id2694723", "A typical heart is approximately"), ("fs-id1478856", "The human heart consists of four"),
              ("fs-id1478856", "The ventricles serve as")],
 "ra": [("fs-id3890004", "The right atrium serves"), ("fs-id3890004", "The two major systemic veins"),
        ("fs-id1705865", "The opening between the atrium and ventricle")],
 "rv": [("fs-id1534517", "The right ventricle receives blood"), ("fs-id2151950", "When the right ventricle contracts")],
 "la": [("fs-id2769216", "After exchange of gases"), ("fs-id2769216", "The opening between the left atrium")],
 "lv": [("fs-id2663012", "The left ventricle is the major"), ("fs-id2183171", "Although the ventricles on the right")],
 "vwall": [("fs-id2183171", "Although the ventricles on the right"), ("fs-id2062267", "The middle and thickest layer"),
           ("fs-id2062267", "It is the contraction of the myocardium"), ("fs-id1422157", "Between the two ventricles"),
           ("fs-id1422157", "It is substantially thicker")],
 "tricuspid": [("fs-id2718087", "Between the right atrium and the right ventricle is"), ("fs-id2718087", "It typically consists of three"),
               ("fs-id2718087", "The flaps are connected")],
 "mitral": [("fs-id2326948", "Located at the opening"), ("fs-id2326948", "Structurally, this valve"),
            ("fs-id2326948", "The two cusps of the mitral valve")],
 "pvalve": [("fs-id2795451", "Emerging from the right ventricle"), ("fs-id2795451", "The pulmonary valve is comprised"),
            ("fs-id2795451", "Unlike the atrioventricular valves")],
 "avalve": [("fs-id2743769", "At the base of the aorta"), ("fs-id2743769", "It normally is composed"),
            ("fs-id2743769", "When the ventricle relaxes and blood")],
 "pap-rv": [("fs-id1534517", "Each flap of the valve"), ("fs-id1534517", "They connect each of the flaps"),
            ("fs-id1534517", "There are three papillary muscles")],
 "pap-lv": [("fs-id2588005", "The mitral valve is connected"), ("fs-id2588005", "There are two papillary muscles")],
 "coronary": [("fs-id1247110", "Coronary arteries supply"), ("fs-id1247110", "The first portion of the aorta"),
              ("fs-id1247110", "Coronary vessel branches that remain")],
 "lca": [("fs-id2516174", "The left coronary artery distributes")],
 "circumflex": [("fs-id2516174", "The circumflex artery arises"), ("fs-id2516174", "Eventually, it will fuse")],
 "lad": [("fs-id2516174", "The larger anterior interventricular"), ("fs-id2516174", "It follows the anterior interventricular"),
         ("fs-id2516174", "Along the way it gives rise")],
 "rca": [("fs-id2757402", "The right coronary artery proceeds")],
 "marginal": [("fs-id2757402", "Normally, one or more marginal"), ("fs-id2757402", "The marginal arteries supply")],
 "pda": [("fs-id2757402", "On the posterior surface of the heart"), ("fs-id2757402", "It runs along the posterior")],
 "cveins": [("fs-id1382712", "Cardiac veins parallel")],
 "gcv": [("fs-id2197060", "The great cardiac vein can be seen"), ("fs-id2197060", "The great cardiac vein initially")],
 "scv": [("fs-id2197060", "The small cardiac vein parallels")],
 "sinus": [("fs-id2197060", "The coronary sinus is a large"), ("fs-id3890004", "Immediately superior and slightly medial")],
 "svc": [("fs-id3890004", "The superior vena cava drains"), ("fs-id3890004", "It empties into the superior")],
 "ivc": [("fs-id3890004", "The inferior vena cava drains"), ("fs-id3890004", "It, too, empties")],
 "ptrunk": [("fs-id1236860", "The right ventricle pumps deoxygenated"), ("fs-id1236860", "The pulmonary trunk arteries")],
 "pveins": [("fs-id1236860", "Highly oxygenated blood returning"), ("fs-id2769216", "After exchange of gases")],
 "aorta": [("fs-id2663012", "The left ventricle is the major"), ("fs-id1247110", "The first portion of the aorta")],
}
topics = {k: [sent(p, s) for p, s in v] for k, v in T.items()}

NO_SPECIFIC = "This source has no passage about this specific vessel. The passage below covers the group it belongs to."
FROM_NAME = "The dataset names this vessel as a branch of the artery described below."


def topic_for(n):
    l = n.lower()
    rules = [
        ("right atrium" in l, "ra", None), ("left atrium" in l, "la", None),
        (l == "cavity of right ventricle", "rv", None), (l == "cavity of left ventricle", "lv", None),
        (l == "wall of ventricle", "vwall", None), ("tricuspid" in l, "tricuspid", None), ("mitral" in l, "mitral", None),
        ("pulmonary valve" in l, "pvalve", None), ("aortic valve" in l, "avalve", None),
        ("papillary muscle of right ventricle" in l, "pap-rv", None), ("papillary muscle of left ventricle" in l, "pap-lv", None),
        (l == "trunk of left coronary artery", "lca", None), ("circumflex" in l, "circumflex", None),
        (l == "trunk of anterior interventricular branch of left coronary artery", "lad", None),
        ("anterior interventricular branch" in l or "anterior descending branch" in l, "lad", FROM_NAME),
        (l == "trunk of right coronary artery", "rca", None), (l == "marginal branch of right coronary artery", "marginal", None),
        ("posterior interventricular branch" in l, "pda", None), ("of right coronary artery" in l, "rca", FROM_NAME),
        ("conus artery" in l, "coronary", NO_SPECIFIC),
        (l == "great cardiac vein", "gcv", None), (l == "small cardiac vein", "scv", None), (l == "coronary sinus", "sinus", None),
        ("cardiac vein" in l or "marginal vein" in l, "cveins", NO_SPECIFIC),
        (l == "superior vena cava", "svc", None), (l == "inferior vena cava", "ivc", None),
        (l in ("pulmonary trunk", "left pulmonary artery", "right pulmonary artery"), "ptrunk", None),
        ("pulmonary vein" in l, "pveins", None), ("aorta" in l, "aorta", None),
    ]
    for ok, t, note in rules:
        if ok:
            return t, note
    return None, None


heart = json.load(open(HEART))
mesh_topic, missing = {}, []
for m in heart["meshes"]:
    t, note = topic_for(m["name"])
    if t:
        mesh_topic[m["id"]] = {"topic": t, "note": note}
    else:
        missing.append(m["name"])

FLOW = [  # each step: dataset part names to highlight + one verbatim sentence
    (["Superior vena cava", "Inferior vena cava"], ("fs-id2175356", "The blood in the superior and inferior venae cavae")),
    (["Cavity of right atrium"], ("fs-id1705865", "The opening between the atrium and ventricle")),
    (["Anterior leaflet of tricuspid valve", "Posterior leaflet of tricuspid valve", "Septal leaflet of tricuspid valve"],
     ("fs-id1534517", "The right ventricle receives blood")),
    (["Cavity of right ventricle"], ("fs-id1236860", "The right ventricle pumps deoxygenated")),
    (["Left anterior cusp of pulmonary valve", "Right anterior cusp of pulmonary valve", "Posterior cusp of pulmonary valve"],
     ("fs-id2151950", "At the base of the pulmonary trunk")),
    (["Pulmonary trunk", "Left pulmonary artery", "Right pulmonary artery"], ("fs-id2151950", "When the right ventricle contracts")),
    (["Left inferior pulmonary vein", "Left superior pulmonary vein", "Right inferior pulmonary vein", "Right superior pulmonary vein"],
     ("fs-id2769216", "After exchange of gases")),
    (["Cavity of left atrium"], ("fs-id2769216", "The opening between the left atrium")),
    (["Anterior leaflet of mitral valve", "Posterior leaflet of mitral valve"], ("fs-id2326948", "Located at the opening")),
    (["Cavity of left ventricle"], ("fs-id2663012", "The left ventricle is the major")),
    (["Anterior cusp of aortic valve", "Left posterior cusp of aortic valve", "Right posterior cusp of aortic valve"],
     ("fs-id2743769", "At the base of the aorta")),
    (["Ascending aorta", "Arch of aorta", "Descending thoracic aorta"], ("fs-id1236860", "The pulmonary veins conduct blood")),
]
names = {m["name"] for m in heart["meshes"]}
flow = []
for parts_, (pid, pre) in FLOW:
    for n in parts_:
        assert n in names, n
    flow.append({"parts": parts_, "passage": sent(pid, pre)})

json.dump({"source": {"title": "Anatomy and Physiology 2e", "section": "19.1 Heart Anatomy", "module": "m46676",
                      "url": "https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy",
                      "license": "CC BY-NC-SA 4.0"},
           "topics": topics, "meshTopic": mesh_topic, "flow": flow}, open(OUT, "w"), indent=0)
print(len(topics), "topics,", len(mesh_topic), "of", len(heart["meshes"]), "meshes mapped; unmapped:", missing)
