"""Quoted content for the female reproductive workstation and the female pelvis.
Usage: content_female.py <openstax dir> <site data dir>

Text: OpenStax 27.2 (the current edition's "Anatomy and Physiology of the Ovarian Reproductive System"), 8.3, 7.3
and 25.2. Each sentence is picked by its opening words and checked word for word by contentlib, which also rejects
sentences that point at a figure. Passages about disorders are left for version 2.
"""
import json, re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contentlib import Module, slug
OS, OUT = sys.argv[1], sys.argv[2]


def mod(mid, number, title):
    return Module(f"{OS}/{mid}.cnxml", number, slug(number, title), title)


FEM = mod("m46392", "27.2", "Anatomy and Physiology of the Ovarian Reproductive System")
PEL = mod("m46375", "8.3", "The Pelvic Girdle and Pelvis")
VER = mod("m46352", "7.3", "The Vertebral Column")
URT = mod("m46427", "25.2", "Gross Anatomy of Urine Transport")


def S(M, prefix):
    """The sentence starting with these words, from exactly one paragraph of running text."""
    pids = [p for p, t in M.paras.items() if prefix in t and p not in M.boxed and "Chapter Review" not in M.path[p]
            and "Critical Thinking Questions" not in M.path[p]]
    assert len(pids) == 1, (prefix, pids)
    return M.sent(pids[0], prefix)


def build(scene, T, rules, flow, gaps, notes):
    meta = json.load(open(f"{OUT}/{scene}.json"))
    mt = {}
    for m in meta["meshes"]:
        hit = next(((t, n) for pat, t, n in rules if re.search(pat, m["name"])), None)
        assert hit, "unmapped " + m["name"]
        assert hit[0] in T, hit
        mt[m["id"]] = {"topic": hit[0], "note": hit[1]}
    keys, names = {g["key"] for g in meta["groups"]}, {m["name"] for m in meta["meshes"]}
    fl = []
    for title, sel, passage in flow:
        assert all(g in keys for g in sel.get("groups", [])) and all(n in names for n in sel.get("parts", [])), sel
        fl.append(dict(title=title, passage=passage, **sel))
    json.dump({"topics": T, "meshTopic": mt, "flow": fl, "gaps": gaps, "notes": notes}, open(f"{OUT}/content-{scene}.json", "w"), indent=0)
    print(scene, len(T), "topics,", len(mt), "of", len(meta["meshes"]), "meshes mapped,", len(fl), "tour steps")


NOT_NAMED = "OpenStax 27.2 does not name this part; the passage on the {} is shown."
SOURCE_NOTE = ("3D models: Human Reference Atlas (HuBMAP), made from the Visible Human Female (National Library of Medicine). "
               "The donor was 59 years old (NLM). OpenStax gives sizes for adults in general.")

# ---------------- female reproductive workstation ----------------
build("repro-female", {
    "overview": [S(FEM, "The female, or ovarian, reproductive system functions"), S(FEM, "The ovaries are located within the pelvic cavity"),
                 S(URT, "The bladder lies anterior to the uterus in females")],
    "ovaries": [S(FEM, "Paired ovals, they are each about 2 to 3 cm in length"), S(FEM, "The ovaries are located within the pelvic cavity"),
                S(FEM, "Finally, the ovary itself is attached to the uterus via the ovarian ligament"), S(FEM, "Beneath the tunica albuginea is the cortex")],
    "tubes": [S(FEM, "Each of the two uterine tubes is close to"), S(FEM, "The uterine tubes also have three layers")],
    "isthmus": [S(FEM, "The isthmus is the narrow medial end"), S(FEM, "Each of the two uterine tubes is close to")],
    "infundibulum": [S(FEM, "The wide distal infundibulum flares out"), S(FEM, "The nearby uterine tube, either left or right, receives the oocyte")],
    "ampulla": [S(FEM, "The middle region of the tube, called the ampulla"), S(FEM, "Each of the two uterine tubes is close to")],
    "uterus": [S(FEM, "Its average size is approximately 5 cm wide by 7 cm long"), S(FEM, "It has three sections"),
               S(FEM, "The portion of the uterus superior to the opening of the uterine tubes"), S(FEM, "The middle section of the uterus is called the body")],
    "fundus": [S(FEM, "The portion of the uterus superior to the opening of the uterine tubes")],
    "body": [S(FEM, "The middle section of the uterus is called the body")],
    "wall": [S(FEM, "The wall of the uterus is made up of three layers"), S(FEM, "The most superficial layer is the serous membrane"),
             S(FEM, "The middle layer, or myometrium")],
    "cervix": [S(FEM, "The cervix is the narrow inferior portion of the uterus"), S(FEM, "The cervix produces mucus secretions")],
    "vessels": [S(FEM, "In the luteal phase of the menstrual cycle, special branches off of the uterine artery")],
    "bladder": [S(URT, "The bladder lies anterior to the uterus in females"), S(URT, "The bladder is a retroperitoneal")],
}, [
    (r"ovary$", "ovaries", None),
    (r"^Isthmus", "isthmus", None), (r"^(Infundibulum|Fimbria)", "infundibulum", None), (r"^Ampulla", "ampulla", None),
    (r"^Abdominal ostium", "tubes", NOT_NAMED.format("uterine tubes")),
    (r"^Fundus of uterus", "fundus", None), (r"^Body of uterus", "body", None), (r"wall of uterus$", "wall", None),
    (r"^(Cornua|Lower uterine segment)$", "uterus", NOT_NAMED.format("uterus")),
    (r"^Uterine cervix$", "cervix", None), (r"cervical os$", "cervix", NOT_NAMED.format("cervix")),
    (r"uterine (artery|vein)$", "vessels", "This sentence is the only one in OpenStax 27.2 that names the uterine artery. The uterine veins are not named."),
    (r"bladder|ureteral orifice", "bladder", "Shown for context. This source passage is about the neighbouring organ."),
], [
    ("Ovary", {"groups": ["ovaries"]}, S(FEM, "Following ovulation, the secondary oocyte surrounded by a few granulosa cells")),
    ("Infundibulum and fimbriae", {"parts": ["Infundibulum of left uterine tube", "Fimbria of left uterine tube", "Infundibulum of right uterine tube",
                                             "Fimbria of right uterine tube"]}, S(FEM, "The nearby uterine tube, either left or right, receives the oocyte")),
    ("Ampulla", {"parts": ["Ampulla of left uterine tube", "Ampulla of right uterine tube"]}, S(FEM, "The middle region of the tube, called the ampulla")),
    ("Isthmus", {"parts": ["Isthmus of left uterine tube", "Isthmus of right uterine tube"]}, S(FEM, "Once inside, the muscular contractions and beating cilia")),
    ("Uterus", {"groups": ["uterus"]}, S(FEM, "If the oocyte is successfully fertilized")),
    ("Cervix", {"groups": ["cervix"]}, S(FEM, "The cervix is the narrow inferior portion of the uterus")),
], [
    "The files used here have no meshes for the vagina, the vulva, the breasts, the female urethra or the ligaments of the uterus and ovaries.",
    "The uterine tubes, ovaries and uterus are shown as separate surfaces; the uterine wall's three layers are not modelled separately.",
], [
    SOURCE_NOTE,
    "HRA's metadata for the uterus model says it was made from the Visible Human Male. A uterus cannot come from a male body, so this looks like an "
    "error in the metadata; the model sits in the female body with the other female organs. Flagged for review.",
    "OpenStax's current edition calls this the ovarian reproductive system (section 27.2).",
    "Size: in this model the uterus with the cervix measures 6.3 by 5.2 cm along its two longest axes, and the ovaries are 2.5 cm (left) and "
    "2.6 cm (right) long. OpenStax 27.2 gives about 5 by 7 cm for a uterus that is not pregnant, and 2 to 3 cm for each ovary.",
])

# ---------------- female pelvis ----------------
build("bones-pelvis-f", {
    "overview": [S(PEL, "The differences between the adult female and male pelvis"), S(PEL, "The ischial tuberosities of females are also farther apart"),
                 S(PEL, "Because of this increased pelvic width, the subpubic angle"), S(PEL, "The female sacrum is wider, shorter, and less curved")],
    "hip": [S(PEL, "The hip bone, or coxal bone, forms the pelvic girdle"), S(PEL, "Each adult hip bone is formed by three separate bones")],
    "ilium": [S(PEL, "The ilium is the fan-like, superior region"), S(PEL, "This curved, superior margin of the ilium is the iliac crest")],
    "ischium": [S(PEL, "The ischium forms the posteroinferior region"), S(PEL, "The large, roughened area of the inferior ischium")],
    "pubis": [S(PEL, "The pubis curves medially"), S(PEL, "The enlarged medial portion of the pubis is the pubic body")],
    "sacrum": [S(PEL, "The female sacrum is wider, shorter, and less curved"), S(VER, "The sacral promontory is the anterior lip")],
    "coccyx": [S(VER, "Similarly, the coccyx, or tailbone, results from the fusion"), S(VER, "It articulates with the inferior tip of the sacrum")],
    "compare": [S(PEL, "In general, the bones of the male pelvis are thicker and heavier"), S(PEL, "The greater sciatic notch of the male hip bone"),
                S(PEL, "The lesser pelvic cavity of females is also wider")],
}, [
    (r"ilium \(compact", "ilium", None), (r"ischium \(compact", "ischium", None), (r"pubis \(compact", "pubis", None),
    (r"spongy bone", "hip", "The inner spongy (trabecular) bone of the hip bone. The textbook passage describes the hip bone as a whole."),
    (r"sacrum", "sacrum", None), (r"^Coccyx$", "coccyx", None),
], [
    ("Ilium", {"groups": ["ilium"]}, S(PEL, "The ilium is the fan-like, superior region")),
    ("Ischium", {"groups": ["ischium"]}, S(PEL, "The ischium forms the posteroinferior region")),
    ("Pubis", {"groups": ["pubis"]}, S(PEL, "The pubis curves medially")),
    ("Sacrum", {"groups": ["sacrum"]}, S(PEL, "The female sacrum is wider, shorter, and less curved")),
    ("Coccyx", {"groups": ["coccyx"]}, S(VER, "Similarly, the coccyx, or tailbone, results from the fusion")),
    ("Female and male pelvis", {"groups": ["ilium", "ischium", "pubis", "sacrum", "coccyx"]}, S(PEL, "Because of this increased pelvic width, the subpubic angle")),
], [
    "Each hip bone is modelled as its three regions (ilium, ischium, pubis), each as an outer compact layer and an inner spongy layer. The spongy layer starts hidden.",
], [
    SOURCE_NOTE,
    "Compare with the male pelvis in the male body's Pelvis workstation. The male data has no coccyx; this female pelvis has one.",
])
