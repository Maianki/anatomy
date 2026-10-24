# Anatomy Atlas (design demo)

An interactive 3D atlas for students learning organs. The whole body opens first. Organs marked
"Workstation" open a study view with the organ in the chest, labels with leader lines, section
cuts, an exploded view, an orientation cube, a guided tour, and text quoted from a textbook.

Workstations so far: **heart** and **lungs**.

Accuracy rules this project follows:

- Geometry comes only from BodyParts3D. Nothing is modelled by hand.
- Every structure name and FMA ID comes from the dataset.
- Every sentence of text is quoted unchanged from OpenStax, with a link to its section. The build
  fails if a quote is not found word for word in the source, or if it refers to a figure the page
  does not show.
- Where the data or the text has a gap, the page says so instead of filling it.

## Sources and licences

| What | Source | Licence |
| --- | --- | --- |
| 3D geometry, names, FMA IDs | BodyParts3D 4.0, © The Database Center for Life Science, via Human Atlas and the npm package `@dagno/anatomy-model@0.1.2` | CC BY 4.0 |
| Quoted text | OpenStax, *Anatomy and Physiology 2e*, © Rice University (`sources/openstax`, from github.com/openstax/osbooks-anatomy-physiology) | CC BY-NC-SA 4.0 |
| 3D library | three.js r128, loaded from cdnjs and jsDelivr | MIT |

The OpenStax licence is **non-commercial and share-alike**. A paid product would need different text.

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

1. `build3.py`: lungs scene. Also finds meshes placed outside the lungs and writes them to `lungs.json` as `excluded`.
2. `build.py`: whole-body scene. Leaves out the meshes `build3.py` excluded.
3. `build2.py`: heart scene (heart plus great vessels cut short near the heart) and the thorax context scene.
4. `content_heart.py`, `content_lungs.py`: quoted text, mapping each mesh to a passage, and the guided tours.

The output is deterministic: a rebuild matches the committed files once decompressed. Only the gzip
timestamps differ.

## Run locally

```sh
cd site && python3 -m http.server 8765
# open http://127.0.0.1:8765/anatomy-atlas.html  (or #heart, #lungs)
```

## Data findings (please keep this list up to date)

These came up while building and are reflected on the page:

- **Organ grouping:** the dataset's own "system" grouping has errors, for example brain ventricles under
  "cardiac" and the liver's main tissue ("Hepatovenous segment II–VIII") under "venous". Organs are
  selected by FMA concept instead.
- **Liver:** "Hepatovenous segment IX" is not in the dataset's liver concept.
- **Lungs:** there are no meshes for the lung surfaces, fissures or pleura. Lobes are shown through the
  airways and vessels the dataset assigns to them.
- **Lungs:** two meshes named "Right anterior segmental artery" (FJ2041, FJ2044, FMA8620) sit about
  22–26 cm below the rest of their segment, at liver level. They are left out everywhere and listed on the page.
- **Lungs, missing vessels:** right lower lobe medial basal has no artery mesh. Left lower lobe superior
  and medial basal have no vein meshes.
- **Checks that pass:** 10 segments per lung, each lung mesh in exactly one lobe, no left/right
  mismatches, segment heights in anatomical order, every heart mesh within 3 cm of the heart walls.
- **Naming:** some dataset names differ from OpenStax wording, for example papillary muscles of the
  left ventricle. Both are shown as they are.

## Before use with students

- An anatomy educator should review the structure names, the data findings above, and the choice of
  quoted passages.
- The original BodyParts3D archive was not reachable from the build environment. The repackaged copy
  should be checked against `isa_BP3D_4.0_obj_99.zip` from dbarchive.biosciencedbc.jp.
- Tested only in headless Chromium with software rendering, at desktop and phone widths.

For learning only, not for diagnosis.
