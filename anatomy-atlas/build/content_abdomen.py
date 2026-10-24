"""Quoted content for the liver/gallbladder/pancreas, digestive tract and urinary workstations.
Usage: content_abdomen.py <openstax dir> <site data dir>"""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from contentlib import Module, slug
OS, OUT = sys.argv[1], sys.argv[2]


def mod(mid, number, title):
    return Module(f"{OS}/{mid}.cnxml", number, slug(number, title), title)


ESO = mod("m46511", "23.3", "The Mouth, Pharynx, and Esophagus")
STO = mod("m46517", "23.4", "The Stomach")
INT = mod("m46512", "23.5", "The Small and Large Intestines")
ACC = mod("m46496", "23.6", "Accessory Organs in Digestion: The Liver, Pancreas, and Gallbladder")
URT = mod("m46427", "25.2", "Gross Anatomy of Urine Transport")
KID = mod("m46429", "25.3", "Gross Anatomy of the Kidney")


def topics(spec):
    return {k: [m.sent(p, s) for m, p, s in v] for k, v in spec.items()}


def build(scene, spec, rules, flow, extra=None):
    meta = json.load(open(f"{OUT}/{scene}.json"))
    T = topics(spec)
    mt, names = {}, {m["name"] for m in meta["meshes"]}
    for m in meta["meshes"]:
        hit = next(((t, note) for f, t, note in rules if f(m)), None)
        assert hit, "unmapped " + m["name"]
        assert hit[0] in T, hit
        mt[m["id"]] = {"topic": hit[0], "note": hit[1]}
    fl = []
    for title, sel, (m, p, s) in flow:
        for n in sel.get("parts", []):
            assert n in names, n
        fl.append(dict(title=title, passage=m.sent(p, s), **sel))
    out = {"topics": T, "meshTopic": mt, "flow": fl}
    out.update(extra or {})
    json.dump(out, open(f"{OUT}/content-{scene}.json", "w"), indent=0)
    print(scene, len(T), "topics,", len(mt), "of", len(meta["meshes"]), "meshes mapped,", len(fl), "tour steps")


name = lambda *n: (lambda m: m["name"] in n)
has = lambda *s: (lambda m: any(x in m["name"] for x in s))
grp = lambda *g: (lambda m: m["group"] in g)
LOBES_ONLY = "This source describes the liver's lobes. It does not describe the numbered segments used in this 3D model."
CONTEXT = "Shown for context. This source passage is about the neighbouring organ."

# ---------------- liver, gallbladder, pancreas ----------------
build("liver", {
    "overview": [(ACC, "fs-id1907412", "The liver is the largest gland"), (ACC, "fs-id1907412", "The liver lies inferior"),
                 (ACC, "fs-id1479465", "The liver is divided into two primary lobes"), (ACC, "fs-id1479465", "In the right lobe, some anatomists"),
                 (ACC, "fs-id1842507", "The porta hepatis")],
    "lobes": [(ACC, "fs-id1479465", "The liver is divided into two primary lobes"), (ACC, "fs-id1479465", "In the right lobe, some anatomists")],
    "portal": [(ACC, "fs-id1842507", "The porta hepatis"), (ACC, "fs-id1842507", "The hepatic portal vein delivers"),
               (ACC, "fs-id1842507", "With this hepatic portal circulation")],
    "arteries": [(ACC, "fs-id1842507", "The porta hepatis"), (ACC, "fs-id1966736", "A hepatic sinusoid is an open")],
    "hveins": [(ACC, "fs-id1842507", "After processing the bloodborne"), (ACC, "fs-id1966736", "Blood then flows through a hepatic vein")],
    "biliary": [(ACC, "fs-id1356003", "The bile ducts unite"), (ACC, "fs-id1356003", "This duct then joins with the cystic duct")],
    "cystic": [(ACC, "fs-id1854598", "The cystic duct is"), (ACC, "fs-id1356003", "This duct then joins with the cystic duct")],
    "gallbladder": [(ACC, "fs-id1854598", "The gallbladder is 8"), (ACC, "fs-id1854598", "This muscular sac stores"),
                    (ACC, "fs-id1854598", "It is divided into three regions"), (ACC, "fs-id1854598", "The fundus is the widest")],
    "pancreas": [(ACC, "fs-id2094509", "The soft, oblong"), (ACC, "fs-id2094509", "Its head is nestled")],
    "pducts": [(ACC, "fs-id1836151", "These acinar cells secrete"), (ACC, "fs-id1836151", "The larger duct fuses"),
               (ACC, "fs-id1836151", "The second and smaller pancreatic duct")],
    "duodenum": [(INT, "fs-id2271264", "The shortest region is"), (INT, "fs-id2271264", "Just past the pyloric sphincter")],
    "ivc": [(ACC, "fs-id1966736", "Blood then flows through a hepatic vein")],
}, [
    (name("Caudate lobe of liver"), "lobes", None),
    (name("Hepatovenous segment IX"), "lobes", LOBES_ONLY + " The dataset also does not file this mesh under its liver concept."),
    (grp("segments"), "lobes", LOBES_ONLY),
    (grp("portal"), "portal", None), (grp("arteries"), "arteries", None), (grp("hveins"), "hveins", None),
    (name("Cystic duct"), "cystic", None), (grp("biliary"), "biliary", None), (grp("gallbladder"), "gallbladder", None),
    (grp("pancreas", "pancreas-parenchyma"), "pancreas", None), (grp("pduct", "pduct-tree"), "pducts", None),
    (grp("duodenum"), "duodenum", CONTEXT.replace("neighbouring organ", "duodenum")), (grp("ivc"), "ivc", None),
], [
    ("Hepatic portal vein", {"groups": ["portal"]}, (ACC, "fs-id1842507", "The porta hepatis")),
    ("Hepatic arteries", {"groups": ["arteries"]}, (ACC, "fs-id1966736", "A hepatic sinusoid is an open")),
    ("Hepatic veins to the inferior vena cava", {"groups": ["hveins", "ivc"]}, (ACC, "fs-id1966736", "Blood then flows through a hepatic vein")),
    ("Bile ducts", {"groups": ["biliary"]}, (ACC, "fs-id1356003", "The bile ducts unite")),
    ("Cystic duct and gallbladder", {"parts": ["Cystic duct", "Gallbladder"]}, (ACC, "fs-id1356003", "This duct then joins with the cystic duct")),
    ("Pancreatic duct", {"groups": ["pduct-tree"]}, (ACC, "fs-id1836151", "The larger duct fuses")),
    ("Into the duodenum", {"groups": ["duodenum"]}, (INT, "fs-id2227124", "This ampulla opens into the duodenum")),
], {"gaps": ["The dataset has no mesh for the common bile duct, the hepatopancreatic ampulla or the liver's ligaments."],
    "notes": ["The gallbladder in this model measures 6.0 cm along its longest axis (build/measure.py). The quoted text gives 8 to 10 cm."]})

# ---------------- digestive tract ----------------
build("gut", {
    "overview": [(ESO, "fs-id1984077", "The esophagus is a muscular tube"), (STO, "fs-id2052808", "The funnel-shaped pylorus"),
                 (INT, "fs-id2142144", "The longest part of the alimentary canal"), (INT, "fs-id1850868", "The large intestine runs from"),
                 (INT, "fs-id1422467", "The large intestine is subdivided")],
    "esophagus": [(ESO, "fs-id1984077", "The esophagus is a muscular tube"), (ESO, "fs-id1984077", "It is approximately 25.4"),
                  (ESO, "fs-id1984077", "To enter the abdomen")],
    "stomach": [(STO, "fs-id2052808", "The cardia (or cardiac region)"), (STO, "fs-id2052808", "Located inferior to the diaphragm"),
                (STO, "fs-id2052808", "Below the fundus is the body"), (STO, "fs-id2052808", "The funnel-shaped pylorus"),
                (STO, "fs-id1386858", "The convex lateral surface")],
    "duodenum": [(INT, "fs-id2271264", "The shortest region is"), (INT, "fs-id2271264", "Just past the pyloric sphincter")],
    "jejunum": [(INT, "fs-id2311182", "The jejunum is about"), (INT, "fs-id2311182", "No clear demarcation")],
    "ileum": [(INT, "fs-id1921294", "The ileum is the longest"), (INT, "fs-id1921294", "It is thicker"), (INT, "fs-id1921294", "The ileum joins the cecum")],
    "ileocecal": [(INT, "fs-id1422467", "The ileocecal valve, located"), (INT, "fs-id1921294", "The ileum joins the cecum")],
    "appendix": [(INT, "fs-id2020835", "The appendix (or vermiform appendix)")],
    "mesoappendix": [(INT, "fs-id2020835", "The mesoappendix, the mesentery")],
    "ascending": [(INT, "fs-id1583646", "Upon entering the colon"), (INT, "fs-id1583646", "At the inferior surface of the liver")],
    "transverse": [(INT, "fs-id1583646", "At the inferior surface of the liver"), (INT, "fs-id1583646", "Food residue passing through the transverse")],
    "descending": [(INT, "fs-id1583646", "From there, food residue passes"), (INT, "fs-id1583646", "The ascending and descending colon")],
    "mesocolon": [(INT, "fs-id1583646", "The transverse and sigmoid colon are tethered")],
    "rectum": [(INT, "fs-id1247327", "Food residue leaving the sigmoid colon"), (INT, "fs-id1247327", "The final 20.3 cm")],
    "teniae": [(INT, "fs-id789222", "The teniae coli are three bands"), (INT, "fs-id789222", "Tonic contractions of the teniae coli")],
    "mesentery": [(INT, "fs-id1921294", "The jejunum and ileum are tethered")],
    "context": [],
}, [
    (grp("esophagus"), "esophagus", None), (grp("stomach"), "stomach", None), (grp("duodenum"), "duodenum", None),
    (grp("jejunum"), "jejunum", None), (grp("ileum"), "ileum", None),
    (name("Ileocecal junction"), "ileocecal", None), (name("Appendix"), "appendix", None), (name("Mesoappendix"), "mesoappendix", None),
    (name("Ascending colon"), "ascending", None), (name("Transverse colon"), "transverse", None),
    (name("Descending colon"), "descending", None), (name("Transverse mesocolon"), "mesocolon", None), (name("Rectum"), "rectum", None),
    (grp("teniae"), "teniae", None), (name("Mesentery of small intestine"), "mesentery", None),
    (grp("accessory"), "context", "Shown for context only. Open the liver, gallbladder and pancreas workstation for these organs."),
], [
    ("Esophagus", {"groups": ["esophagus"]}, (ESO, "fs-id1984077", "To enter the abdomen")),
    ("Stomach", {"groups": ["stomach"]}, (STO, "fs-id2052808", "The cardia (or cardiac region)")),
    ("Duodenum", {"groups": ["duodenum"]}, (STO, "fs-id2052808", "The funnel-shaped pylorus")),
    ("Jejunum", {"groups": ["jejunum"]}, (INT, "fs-id2311182", "The jejunum is about")),
    ("Ileum", {"groups": ["ileum"]}, (INT, "fs-id1921294", "The ileum joins the cecum")),
    ("Ileocecal junction", {"parts": ["Ileocecal junction"]}, (INT, "fs-id1422467", "The ileocecal valve, located")),
    ("Ascending colon", {"parts": ["Ascending colon"]}, (INT, "fs-id1583646", "Upon entering the colon")),
    ("Transverse colon", {"parts": ["Transverse colon"]}, (INT, "fs-id1583646", "Food residue passing through the transverse")),
    ("Descending colon", {"parts": ["Descending colon"]}, (INT, "fs-id1583646", "From there, food residue passes")),
    ("Rectum", {"parts": ["Rectum"]}, (INT, "fs-id1247327", "Food residue leaving the sigmoid colon")),
], {"gaps": ["The dataset has no mesh for the cecum, the sigmoid colon or the anal canal, so the tour goes from the descending colon to the rectum."]})

# ---------------- urinary system ----------------
build("urinary", {
    "overview": [(KID, "fs-id1542887", "The kidneys lie on either side"), (KID, "fs-id1592078", "The left kidney is located"),
                 (URT, "fs-id2338701", "The kidneys and ureters are completely"), (URT, "fs-id2569293", "The urethra transports urine")],
    "kidneys": [(KID, "fs-id1542887", "The kidneys lie on either side"), (KID, "fs-id1542887", "They are roughly the size"),
                (KID, "fs-id1592078", "The left kidney is located"), (KID, "fs-id1592078", "They are about 11")],
    "ureters": [(URT, "fs-id2338701", "The renal pelvis narrows"), (URT, "fs-id2338701", "As urine passes through the ureter"),
                (URT, "fs-id2338701", "As the ureters enter the pelvis"), (URT, "fs-id2140392", "The ureters are approximately")],
    "bladder": [(URT, "fs-id1616696", "In males, the anatomy is similar"), (URT, "fs-id1616696", "The bladder is a retroperitoneal"),
                (URT, "fs-id2978014", "The bladder is a highly distensible"), (URT, "fs-id2978014", "Volumes in adults")],
    "urethra": [(URT, "fs-id2569293", "The urethra transports urine"), (URT, "fs-id2071647", "The length of the male urethra"),
                (URT, "fs-id2071647", "It is divided into four regions")],
    "renal": [(KID, "fs-id1764618", "The renal hilum is the entry"), (KID, "fs-id1764618", "The renal arteries form directly"),
              (KID, "fs-id1764618", "The artery, vein, and renal pelvis")],
    "great": [(KID, "fs-id1764618", "The renal arteries form directly")],
    "adrenal": [(KID, "fs-id2488605", "On the superior aspect of each kidney")],
    "prostate": [(URT, "fs-id2071647", "The prostatic urethra passes through")],
}, [
    (grp("kidneys"), "kidneys", None), (grp("ureters"), "ureters", None), (grp("bladder"), "bladder", None), (grp("urethra"), "urethra", None),
    (grp("renal-arteries", "renal-veins"), "renal", None), (grp("great"), "great", None), (grp("adrenal"), "adrenal", None),
    (grp("prostate"), "prostate", None),
], [
    ("Kidneys", {"groups": ["kidneys"]}, (URT, "fs-id2338701", "As urine is formed, it drains")),
    ("Ureters", {"groups": ["ureters"]}, (URT, "fs-id2338701", "The renal pelvis narrows")),
    ("Into the bladder", {"groups": ["ureters", "bladder"]}, (URT, "fs-id2338701", "As they approach the bladder")),
    ("Urethra", {"groups": ["urethra"]}, (URT, "fs-id2569293", "The urethra transports urine")),
    ("Blood in and out of the kidneys", {"groups": ["renal-arteries", "renal-veins", "great"]}, (KID, "fs-id1764618", "The renal arteries form directly")),
], {"gaps": ["Each kidney in this dataset is a single outer surface. The renal cortex, medulla and pyramids are not modelled."],
    "notes": ["The dataset's ureter meshes continue up into each kidney and branch there. The dataset does not name those branches separately, so this page does not label them as the renal pelvis or calyces.",
              "This is an adult male reference body, so the urethra shown is the male urethra.",
              "The kidneys in this model measure 10.8 cm (left) and 10.6 cm (right) along their longest axis (build/measure.py). The quoted text gives 11 to 14 cm."]})
