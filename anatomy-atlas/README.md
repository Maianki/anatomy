# Anatomy Atlas (design demo)

An interactive 3D atlas for students learning organs. The whole body opens first. Organs marked
"Workstation" open a study view with the organ in its body region, labels with leader lines,
section cuts, an exploded view, an orientation cube, a guided tour, and text quoted from a textbook.

| Workstation | Body view organs that open it | Guided tour |
| --- | --- | --- |
| Heart | Heart | Blood flow (12 steps) |
| Lungs | Left lung, right lung, trachea | Air and blood (6 steps) |
| Liver, gallbladder and pancreas | Liver, gallbladder, pancreas | Blood and bile (7 steps) |
| Digestive tract | Esophagus, stomach, small intestine, large intestine | Path of food (10 steps) |
| Urinary system | Kidney, urinary bladder | Path of urine (5 steps) |
| Brain | Brain | Path of CSF (7 steps) |

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
| 3D geometry, names, FMA IDs | BodyParts3D 4.0, © The Database Center for Life Science, via Human Atlas and the npm package `@dagno/anatomy-model@0.1.2` | CC BY 4.0 |
| Quoted text | OpenStax, *Anatomy and Physiology 2e*, © Rice University (`sources/openstax`, from github.com/openstax/osbooks-anatomy-physiology): sections 13.2, 13.3, 19.1, 21.1, 22.1, 22.2, 23.3–23.6, 25.2, 25.3 | CC BY-NC-SA 4.0 |
| 3D library | three.js r128, loaded from cdnjs and jsDelivr | MIT |

The OpenStax licence is **non-commercial and share-alike**. A paid product would need different text.

Section numbers were checked against the book's collection file (`sources/openstax/coll.xml`).
Section page links follow OpenStax's URL pattern (`contentlib.slug`); the build environment could
not reach openstax.org to open them.

## Layout

```
site/anatomy-atlas.html   the page (single file; loads data/ at runtime)
site/data/                built data: <scene>.json manifests, <scene>.gz.txt geometry, content-<organ>.json
build/                    pipeline that produces site/data
sources/openstax/         the OpenStax modules the text is quoted from, plus the book's collection file
test/screenshots.mjs      headless-browser screenshots of a workstation
```

Geometry is stored as base64 text of gzipped binary (`.gz.txt`) because the artifact host does not
serve raw binary files. Each mesh is uint16-quantised positions plus uint16/uint32 indices; normals
are recomputed in the browser.

## Rebuild the data

```sh
pip install numpy fast-simplification
npm pack @dagno/anatomy-model@0.1.2 && tar xzf dagno-anatomy-model-0.1.2.tgz
build/all.sh package/model site/data
```

`all.sh` runs the steps in order:

1. `build3.py`: lungs. Finds meshes placed outside the lungs and records them as `excluded`.
2. `build5.py`: brain and head context. Records non-brain meshes and meshes whose left/right name contradicts their position.
3. `build.py`: whole body. Leaves out the meshes with data errors found in steps 1 and 2.
4. `build2.py`: heart (with great vessels cut short near the heart) and thorax context.
5. `build4.py`: liver/gallbladder/pancreas, digestive tract, urinary system, and abdomen context.
6. `content_*.py`: quoted text, the mapping from each mesh to a passage, and the guided tours.

`measure.py` prints longest-axis lengths used in the size notes below.

The output is deterministic: a rebuild matches the committed files once decompressed. Only the gzip
timestamps differ.

## Run locally

```sh
cd site && python3 -m http.server 8765
# open http://127.0.0.1:8765/anatomy-atlas.html  (or #heart, #lungs, #liver, #gut, #urinary, #brain)
```

## Data findings (please keep this list up to date)

These came up while building and are shown on the page.

**Errors in the source data, left out everywhere:**

- Lungs: two meshes named "Right anterior segmental artery" (FJ2041, FJ2044, FMA8620) sit about
  22–26 cm below the rest of their segment, at liver level.
- Brain: "Brachium of left superior colliculus" (FJ1735) lies on the right of the body and "Brachium
  of right superior colliculus" (FJ1736) on the left, while the colliculi themselves are on the
  correct sides. The names look swapped; they are left out rather than corrected.

**Gaps in the source data:**

- Lungs: no meshes for the lung surfaces, fissures or pleura. Lobes are shown through the airways and
  vessels the dataset assigns to them. Right lower lobe medial basal has no artery mesh; left lower
  lobe superior and medial basal have no vein meshes.
- Liver: no meshes for the common bile duct, the hepatopancreatic ampulla or the liver's ligaments.
  "Hepatovenous segment IX" exists but is not in the dataset's liver concept (included, with a note).
- Digestive tract: no meshes for the cecum, sigmoid colon or anal canal.
- Kidneys: single outer surfaces; no cortex, medulla or pyramids. The ureter meshes continue into
  each kidney and branch there; the dataset does not name the branches, so they are not labelled as
  the renal pelvis or calyces.
- Brain: the dataset's "brain" concept leaves out the corpus callosum, thalamus, basal nuclei,
  amygdala and more. The workstation groups brain meshes by quoted OpenStax sentences, then by each
  mesh's FMA concept; structures neither source places (geniculate bodies, optic chiasm and tracts,
  septum) are listed under "Other". 50 of 107 brain meshes have no passage of their own.

**Duplicates and grouping:**

- The dataset's "system" field has errors (brain ventricles under "cardiac", liver tissue under
  "venous", choroid plexus under "sensory"). Organs are selected by FMA concept or name instead.
- "Pancreas" and "Parenchyma of pancreas" share nearly the same surface, as do "Pancreatic duct" and
  "Pancreatic duct tree". One of each pair starts hidden.

**Sizes compared with the quoted text** (longest axis, `build/measure.py`):

| Organ | This model | OpenStax |
| --- | --- | --- |
| Kidney | 10.8 cm (left), 10.6 cm (right) | 11–14 cm |
| Spleen | 10.7 cm | about 12 cm |
| Gallbladder | 6.0 cm | 8–10 cm |

The right kidney sits about 2 cm lower than the left, as the text describes.

**Checks that pass:** 10 bronchopulmonary segments per lung; each lung mesh in exactly one lobe;
segment heights in anatomical order; every heart mesh within 3 cm of the heart walls; no left/right
mismatches in the lungs, digestive tract, urinary system or abdomen. Heart structures named "right"
lie up to 3 cm left of the midline, which matches the text ("the right side of the heart is deflected
anteriorly"). A few "left" liver vessels lie within 2 cm right of the midline.

**Naming:** some dataset names differ from OpenStax wording (papillary muscles of the left ventricle,
"pineal body" versus "pineal gland", "superior temporal gyrus" versus "superior temporal lobe").
Both are shown as they are.

## Before use with students

- An anatomy educator should review the structure names, the data findings above, the brain
  grouping, and the choice of quoted passages.
- The original BodyParts3D archive was not reachable from the build environment. The repackaged copy
  should be checked against `isa_BP3D_4.0_obj_99.zip` from dbarchive.biosciencedbc.jp.
- Tested only in headless Chromium with software rendering, at desktop and phone widths.

For learning only, not for diagnosis.
