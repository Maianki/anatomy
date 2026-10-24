"""Quoted content for the male reproductive workstation. Usage: content_repro.py <openstax dir> <site data dir>

Sentences come from OpenStax 27.1 (which the current edition titles "Anatomy and Physiology of the Testicular
Reproductive System") and, for the urethra and bladder, 25.2. Each is picked by its opening words; contentlib
checks it word for word and rejects sentences that point at a figure. Passages about disorders (prostate
enlargement, prostate cancer, vasectomy) are left for version 2.
"""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contentlib import Module, slug
OS, OUT = sys.argv[1], sys.argv[2]


def mod(mid, number, title):
    return Module(f"{OS}/{mid}.cnxml", number, slug(number, title), title)


REP = mod("m46400", "27.1", "Anatomy and Physiology of the Testicular Reproductive System")
URT = mod("m46427", "25.2", "Gross Anatomy of Urine Transport")


def S(M, prefix):
    """The sentence starting with these words; it must occur in exactly one paragraph of running text
    (Chapter Review summaries, notes and figure captions are not used)."""
    pids = [p for p, t in M.paras.items() if prefix in t and p not in M.boxed and "Chapter Review" not in M.path[p]]
    assert len(pids) == 1, (prefix, pids)
    return M.sent(pids[0], prefix)


T = {
    "overview": [S(REP, "The testes (singular = testis) are the male gonads"), S(REP, "They produce both sperm and androgens"),
                 S(REP, "The bulk of semen is produced by three critical accessory glands")],
    "testes": [S(REP, "The testes (singular = testis) are the male gonads"), S(REP, "Beneath the tunica vaginalis is the tunica albuginea"),
               S(REP, "Not only does the tunica albuginea cover"), S(REP, "Within the lobules, sperm develop"),
               S(REP, "During the seventh month of the developmental period")],
    "epididymis": [S(REP, "Though the epididymis does not take up much room"), S(REP, "Sperm enter the head of the epididymis"),
                   S(REP, "The more mature sperm are then stored in the tail")],
    "deferent": [S(REP, "During ejaculation, sperm exit the tail of the epididymis"), S(REP, "From each epididymis, each ductus deferens"),
                 S(REP, "From here, the ductus deferens continues posteriorly")],
    "seminal": [S(REP, "The paired seminal vesicles are glands"), S(REP, "Seminal vesicle fluid contains large amounts of fructose"),
                S(REP, "The fluid, now containing both sperm and seminal vesicle secretions")],
    "prostate": [S(REP, "About the size of a walnut"), S(REP, "It excretes an alkaline, milky fluid"), S(URT, "The prostatic urethra passes through")],
    "penis": [S(REP, "The penis is the male organ of copulation"), S(REP, "The shaft is composed of three column-like chambers"),
              S(REP, "Each of the two larger lateral chambers is called a corpus cavernosum"), S(REP, "Together, these make up the bulk of the penis")],
    "spongiosum": [S(REP, "The corpus spongiosum, which can be felt"), S(REP, "The shaft is composed of three column-like chambers")],
    "glans": [S(REP, "The skin from the shaft extends down over the glans"), S(REP, "The foreskin also contains a dense concentration")],
    "urethra": [S(URT, "The length of the male urethra"), S(URT, "It is divided into four regions"), S(URT, "The prostatic urethra passes through")],
    "penile-vessels": [S(REP, "Penile erections are the result of vasocongestion"), S(REP, "Release of NO activates a signaling pathway")],
    "bladder": [S(URT, "In males, the anatomy is similar"), S(URT, "The bladder is a retroperitoneal")],
}
NOTES = {
    "glans": "The textbook's sentence that defines the glans points at a figure we don't show, so it is left out; the passage on the prepuce is shown.",
    "great-tarteries": "OpenStax 27.1 does not describe the testicular arteries by name; the passage on the testes is shown.",
    "great-tveins": "OpenStax 27.1 does not describe the testicular veins by name; the passage on the testes is shown.",
    "bladder": "Shown for context. This source passage is about the neighbouring organ.",
}
GROUP_TOPIC = {"testes": "testes", "epididymis": "epididymis", "deferent": "deferent", "seminal": "seminal", "prostate": "prostate",
               "urethra": "urethra", "penile-arteries": "penile-vessels", "penile-veins": "penile-vessels",
               "great-tarteries": "testes", "great-tveins": "testes", "bladder": "bladder"}
PENIS_PART = {"Corpus cavernosum of penis": "penis", "Corpus spongiosum of penis": "spongiosum", "Glans penis": "glans"}

meta = json.load(open(f"{OUT}/repro-male.json"))
mt = {}
for m in meta["meshes"]:
    topic = PENIS_PART[m["name"]] if m["group"] == "penis" else GROUP_TOPIC[m["group"]]
    mt[m["id"]] = {"topic": topic, "note": NOTES.get(topic if m["group"] == "penis" else m["group"])}
names = {m["name"] for m in meta["meshes"]}
flow = [
    ("Testes", {"groups": ["testes"]}, S(REP, "Within the lobules, sperm develop")),
    ("Epididymis", {"groups": ["epididymis"]}, S(REP, "Sperm enter the head of the epididymis")),
    ("Ductus deferens", {"groups": ["deferent"]}, S(REP, "During ejaculation, sperm exit the tail of the epididymis")),
    ("Into the pelvis", {"groups": ["deferent"]}, S(REP, "From each epididymis, each ductus deferens")),
    ("Seminal vesicles", {"groups": ["seminal"]}, S(REP, "The fluid, now containing both sperm and seminal vesicle secretions")),
    ("Prostate", {"groups": ["prostate"]}, S(REP, "The paired ejaculatory ducts transport the seminal fluid")),
    ("Urethra and penis", {"groups": ["urethra", "penis"]}, S(REP, "The corpus spongiosum, which can be felt")),
]
for _, sel, _ in flow:
    assert all(g in {x["key"] for x in meta["groups"]} for g in sel["groups"])
out = {"topics": T, "meshTopic": mt,
       "flow": [dict(title=t, passage=p, **sel) for t, sel, p in flow],
       "gaps": ["The dataset has no meshes for the scrotum, the spermatic cord, the ejaculatory ducts, the bulbourethral glands or the prepuce.",
                "The urethra is one mesh in the dataset; its four regions are not shown separately.",
                "BodyParts3D is one male body. It has no female organs, so there is no female reproductive workstation yet."],
       "notes": ["OpenStax's current edition calls this the testicular reproductive system (section 27.1).",
                 "The ejaculatory ducts are named in the tour text but are not in the 3D model.",
                 "Size: each testis in this model is 2.9 cm along its longest axis (build/measure.py). OpenStax 27.1 gives about 4 to 5 cm for an adult testis."]}
json.dump(out, open(f"{OUT}/content-repro-male.json", "w"), indent=0)
print("repro-male", len(T), "topics,", len(mt), "of", len(meta["meshes"]), "meshes mapped,", len(flow), "tour steps")
