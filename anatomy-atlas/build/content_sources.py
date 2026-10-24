"""Build sources.json for the Sources screen from what the app actually uses.
Usage: content_sources.py <site data dir> <@dagno/anatomy-model package dir>"""
import glob, json, os, re, sys
OUT, PKG = sys.argv[1], sys.argv[2]
VER = sys.argv[3] if len(sys.argv) > 3 else None
TITLES = {  # OpenStax A&P 2e section titles, as passed to contentlib.slug in the content builders
    "13.2": "The Central Nervous System", "13.3": "Circulation and the Central Nervous System", "19.1": "Heart Anatomy",
    "21.1": "Anatomy of the Lymphatic and Immune Systems", "22.1": "Organs and Structures of the Respiratory System",
    "22.2": "The Lungs", "23.3": "The Mouth, Pharynx, and Esophagus", "23.4": "The Stomach", "23.5": "The Small and Large Intestines",
    "23.6": "Accessory Organs in Digestion: The Liver, Pancreas, and Gallbladder", "25.2": "Gross Anatomy of Urine Transport",
    "25.3": "Gross Anatomy of the Kidney", "Ch. 19": "Chapter Review"}
NAMES = {"heart": "Heart", "lungs": "Lungs", "liver": "Liver, gallbladder and pancreas", "gut": "Digestive tract",
         "urinary": "Urinary system", "brain": "Brain", "body": "Whole body (spleen, diaphragm)"}
sections = {}


def walk(x, organ):
    if isinstance(x, dict):
        if "text" in x and "url" in x and "label" in x:
            num = " ".join(x["label"].split()[:2]) if x["label"].startswith("Ch. ") else x["label"].split()[0]
            s = sections.setdefault(num, {"number": num, "title": TITLES[num], "url": x["url"], "quotes": set(), "used": set()})
            assert s["url"] == x["url"], (num, x["url"])
            s["quotes"].add(x["text"]); s["used"].add(NAMES[organ])
        for v in x.values():
            walk(v, organ)
    elif isinstance(x, list):
        for v in x:
            walk(v, organ)


for f in sorted(glob.glob(f"{OUT}/content-*.json")):
    walk(json.load(open(f)), re.match(r"content-(.+)\.json", os.path.basename(f)).group(1))
attr = open(f"{PKG}/ATTRIBUTION.md").read()
for must in ("10.1093/nar/gkn613", "Mitsuhashi et al. (2009)", "isa_BP3D_4.0_obj_99.zip", "CC BY 4.0", "f5d5b74"):
    assert must in attr, must
data = {
    "geometry": {
        "name": "BodyParts3D 4.0", "publisher": "The Database Center for Life Science (DBCLS), Japan", "license": "CC BY 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/4.0/", "url": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html",
        "citation": "Mitsuhashi et al. (2009), BodyParts3D: 3D structure database for anatomical concepts. Nucleic Acids Research.",
        "doi": "10.1093/nar/gkn613", "file": "isa_BP3D_4.0_obj_99.zip",
        "chain": ["Geometry: the official BodyParts3D 4.0 archive, isa_BP3D_4.0_obj_99.zip, converted from millimetres and Z-up to metres and Y-up",
                  "Names, FMA IDs and concept groups: @dagno/anatomy-model 0.1.2 on npm (prepared by Human Atlas), checked identical to the official BodyParts3D tables",
                  "Organ workstations: meshes simplified only where every original vertex stays within 1 mm",
                  "Whole-body view: simplified further, as an overview"],
        "body": "One adult male reference anatomy, based on MRI data with anatomical illustration refinements."},
    "text": {"name": "Anatomy and Physiology 2e", "publisher": "OpenStax, Rice University", "license": "CC BY-NC-SA 4.0",
             "licenseUrl": "https://creativecommons.org/licenses/by-nc-sa/4.0/", "url": "https://openstax.org/details/books/anatomy-and-physiology-2e",
             "repo": "https://github.com/openstax/osbooks-anatomy-physiology",
             "sections": [dict(s, quotes=len(s["quotes"]), used=sorted(s["used"])) for s in sorted(sections.values(), key=lambda s: [int(p) for p in re.findall(r"\d+", s["number"])] + [99 if s["number"].startswith("Ch.") else 0])]},
}
data["geometry"]["attribution"] = "BodyParts3D, \u00a9 The Database Center for Life Science licensed under CC Attribution 4.0 International"
data["geometry"]["licenseUpdated"] = "2025-02-27"
data["geometry"]["note"] = ("The OBJ files still carry an older CC BY-SA 2.1 Japan notice; the database's current licence page "
                            "(updated 2025-02-27) replaces it with CC BY 4.0.")
if VER:
    o = json.load(open(f"{VER}/openstax.json")); b = json.load(open(f"{VER}/bodyparts3d.json")); g = json.load(open(f"{VER}/geometry.json"))
    data["verification"] = {
        "date": "2026-10-24",
        "items": [
            f"All {o['quotes']} quotes were found word for word on the live openstax.org pages, and all {o['pages']} section links open the right page and paragraph.",
            f"All {b['matched']:,} meshes in the dataset exist in the official archive, and every name and FMA ID matches the official tables.",
            "The 3D geometry is read straight from the official archive (isa_BP3D_4.0_obj_99.zip). In every organ workstation, every vertex of the original lies within "
            f"{max(v['max_mm'] for v in g.values()):.1f} mm of what you see.",
            "The data errors listed in each organ's Notes tab (two misplaced lung arteries, two brain structures named for the wrong side) are present in the official archive itself.",
        ]}
json.dump(data, open(f"{OUT}/sources.json", "w"), indent=1)
print(len(sections), "sections,", sum(len(s["quotes"]) for s in sections.values()), "distinct quotes")
for s in data["text"]["sections"]: print(" ", s["number"], s["quotes"], s["used"])
