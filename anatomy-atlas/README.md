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

## Decisions, data findings and open checks

All project decisions, data errors and gaps, size comparisons, passing checks and the review
checklist are kept in one place: [DECISIONS.md](DECISIONS.md).

For learning only, not for diagnosis.
