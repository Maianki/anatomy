# Anatomy Atlas (design demo)

An interactive 3D atlas for students learning organs and bones (one adult male body; no female body yet, see DECISIONS D36). The whole body opens first, with a
switch between **Organs** and **Bones** so only one kind is clickable at a time. Organs and bone
regions marked "Workstation" open a study view with the structure in its body region, labels with
leader lines, section cuts, an exploded view, see-through and vessel views (organs), an orientation
cube, a guided tour with Play, and text quoted from a textbook.

| Workstation | Body view organs that open it | Guided tour |
| --- | --- | --- |
| Heart | Heart | Blood flow (12 steps) |
| Lungs | Left lung, right lung, trachea | Air and blood (6 steps) |
| Liver, gallbladder and pancreas | Liver, gallbladder, pancreas | Blood and bile (7 steps) |
| Digestive tract | Esophagus, stomach, small intestine, large intestine | Path of food (10 steps) |
| Urinary system | Kidney, urinary bladder | Path of urine (5 steps) |
| Brain | Brain | Path of CSF (7 steps) |
| Skull | Skull (bones mode) | Bone by bone (3 steps) |
| Vertebral column | Vertebral column | Bone by bone (5 steps) |
| Thoracic cage | Thoracic cage | Bone by bone (3 steps) |
| Upper limbs | Upper limbs | Bone by bone (8 steps) |
| Pelvis | Pelvis | Bone by bone (2 steps) |
| Lower limbs | Lower limbs | Bone by bone (8 steps) |
| Male reproductive system | Testis, epididymis, deferent duct, seminal vesicle, prostate, penis | Path of sperm (7 steps) |

The spleen and diaphragm are single meshes with no named parts, so they have no workstation. The
body view shows quoted text for them.

Accuracy rules this project follows:

- Geometry comes only from BodyParts3D. Nothing is modelled by hand.
- Every structure name and FMA ID comes from the dataset.
- Every sentence of text is quoted unchanged from OpenStax, with a link to its section. The build
  fails if a quote is not found word for word in the source, or if it refers to a figure the page
  does not show.
- Every mesh in a workstation belongs to exactly one group, chosen by its dataset name or FMA concept
  (the abdominal build fails on a mesh that matches no group or two), and every mesh gets a passage
  or an explicit note (the content build fails otherwise).
- Where the data or the text has a gap, the page says so instead of filling it.

## Sources and licences

| What | Source | Licence |
| --- | --- | --- |
| 3D geometry | BodyParts3D 4.0, official archive `isa_BP3D_4.0_obj_99.zip`. Credit: "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International" | CC BY 4.0 |
| Names, FMA IDs, concept groups | `@dagno/anatomy-model@0.1.2` (BodyParts3D tables prepared by Human Atlas), checked identical to the official tables | CC BY 4.0 |
| Quoted text | OpenStax, *Anatomy and Physiology 2e*, © Rice University (`sources/openstax`, from github.com/openstax/osbooks-anatomy-physiology): sections 7.2–7.4, 8.1–8.4, 13.2, 13.3, 19.1, 21.1, 22.1, 22.2, 23.3–23.6, 25.2, 25.3, 27.1 | CC BY-NC-SA 4.0 |
| Fact cross-check (no content copied) | WebMD pages listed in `sources/crosscheck/webmd.json`, summarised in our own words | n/a |
| 3D library | three.js r128, loaded from cdnjs and jsDelivr | MIT |

The OpenStax licence is **non-commercial and share-alike**. A paid product would need different text.

Section numbers were checked against the book's collection file (`sources/openstax/coll.xml`).
Every section link and quote was checked against the live openstax.org pages (see below).

## Layout

```
site/anatomy-atlas.html   the page (single file; loads data/ at runtime)
site/data/                built data: <scene>.json manifests, <scene>.gz.txt geometry, content-<organ>.json
build/                    pipeline that produces site/data
sources/openstax/         the OpenStax modules the text is quoted from, plus the book's collection file
sources/bodyparts3d/      official BodyParts3D name and part-of tables, and the licence page
sources/verification/     results of the checks against the original sources
sources/crosscheck/       facts cross-checked with WebMD (links, reviewer, date, result)
test/                     headless-browser checks: ui.mjs (screens), play.mjs (tour Play), tools.mjs (see-through, vessels), bones.mjs (bone search), screenshots.mjs
```

Geometry is stored as base64 text of gzipped binary (`.gz.txt`) because the artifact host does not
serve raw binary files. Each mesh is uint16-quantised positions plus uint16/uint32 indices; normals
are recomputed in the browser.

## Rebuild the data

```sh
pip install numpy scipy fast-simplification
npm pack @dagno/anatomy-model@0.1.2 && tar xzf dagno-anatomy-model-0.1.2.tgz
curl -LO https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip
build/all.sh package isa_BP3D_4.0_obj_99.zip site/data
```

Geometry is read from the official BodyParts3D archive (`official.py`). Names, FMA IDs and concept groups come
from the npm package, which was checked to match the official tables exactly. `all.sh` runs the steps in order:

1. `build3.py`: lungs. Finds meshes placed outside the lungs and records them as `excluded`.
2. `build5.py`: brain and head context. Records non-brain meshes and meshes whose left/right name contradicts their position.
3. `build6.py`: six bone workstations and the skeleton context, from the dataset's FMA concepts for each region.
4. `build.py`: whole body. Leaves out the meshes with data errors found in steps 1 and 2.
5. `build2.py`: heart (with great vessels cut short near the heart) and thorax context.
6. `build4.py`: liver/gallbladder/pancreas, digestive tract, urinary system, and abdomen context.
7. `build7.py`: male reproductive organs and the pelvis context.
8. `content_*.py`: quoted text, the mapping from each mesh to a passage, the guided tours, and the Sources page data.

Organ and bone workstation meshes are simplified only as far as keeps every original vertex within 1 mm (`common.py`).
Where the archive has two meshes with the same FMA ID and identical geometry, only the first is used and the other is
listed in the scene file (`duplicates`).
`measure.py` prints the longest-axis lengths used in the size notes.

The output is deterministic: a rebuild matches the committed files once decompressed. Only the gzip
timestamps differ.

## Verify against the original sources

These need network access to openstax.org and the official archive. Results are kept in `sources/verification/`
and shown on the Sources page.

```sh
VERIFY_OUT=sources/verification/openstax.json python3 build/verify_openstax.py site/data /tmp/openstax-pages
python3 build/verify_bp3d.py isa_BP3D_4.0_obj_99.zip package/model sources/verification/bodyparts3d.json sources/bodyparts3d/isa_element_parts.txt
VERIFY_OUT=sources/verification/geometry.json python3 build/verify_output.py site/data isa_BP3D_4.0_obj_99.zip
```

`verify_geometry.py` and `verify_coverage.py` compare the npm copy's own geometry with the original; they found the
deviations that led to reading geometry from the official archive instead.

## Run locally

```sh
cd site && python3 -m http.server 8765
# open http://127.0.0.1:8765/anatomy-atlas.html  (or #heart, #lungs, #liver, #gut, #urinary, #brain,
#   #repro-male, #bones-skull, #bones-spine, #bones-thorax, #bones-upper, #bones-pelvis, #bones-lower, #sources)
```

## Decisions, data findings and open checks

All project decisions, data errors and gaps, size comparisons, passing checks and the review
checklist are kept in one place: [DECISIONS.md](DECISIONS.md).

For learning only, not for diagnosis.
