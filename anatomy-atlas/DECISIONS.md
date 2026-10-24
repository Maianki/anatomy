# Anatomy Atlas: decisions, gaps and review checklist

The single reference for what we are building, what has been decided and why, what the data is
missing, and what still needs checking. Update it whenever a decision changes or a check is done.

Last updated: 2026-10-24 (female body from the Human Reference Atlas; male reproductive workstation; bones; verified against the official BodyParts3D archive, the HRA files and the live OpenStax site).

## 1. What we are building

- **Goal:** an interactive 3D app for students, especially medical students, to learn human organs
  and their parts.
- **Version 1 (now):** organs and their parts, and the bones of the skeleton (normal anatomy).
- **Version 2 (later):** diseases. Disease passages in the textbook are deliberately left out of version 1.
- **Flow:** a whole human body opens first, male or female (switch). Tapping an organ selects it. Organs with enough detail
  open an organ workstation: the organ alone in 3D, with its parts named, quoted text and a guided tour.
- **Top priority:** accuracy. Nothing is assumed or invented. Where something is unclear or missing,
  the app says so.

## 2. Decisions

| # | Decision | Why |
| --- | --- | --- |
| D1 | Build a **web app**, not a native app. It can be wrapped for app stores later (for example with Capacitor). | One codebase for phones, tablets and laptops, opened from a link, with no app-store review. |
| D2 | **No hand-made geometry.** All 3D models come from a scan-based anatomy dataset. | The first hand-built heart demo was rejected; hand modelling can't be accurate enough for teaching. |
| D3 | 3D source: **BodyParts3D 4.0** (Database Center for Life Science, CC BY 4.0). **Geometry is read straight from the official archive** `isa_BP3D_4.0_obj_99.zip`; names, FMA IDs and concept groups come from the npm package `@dagno/anatomy-model@0.1.2`, checked identical to the official tables. | Built from MRI scans, separate named meshes, FMA IDs, free with credit. At first only the npm copy was reachable; once the official site was allowed, the copy's own simplification was found to move parts of long vessels by up to about 7 mm, so geometry was switched to the official files. |
| D4 | Text source: **OpenStax Anatomy and Physiology 2e**, quoted **word for word**, each quote linked to its section. Taken from OpenStax's official GitHub repository. | Peer-reviewed textbook for students. Quoting unchanged avoids errors in paraphrase. |
| D5 | **WebMD is not used for text.** It may be used only as a reference to cross-check facts. | WebMD's text is copyrighted. |
| D6 | OpenStax is **CC BY-NC-SA 4.0** (non-commercial, share-alike), not CC BY as first stated. | Corrected after reading the licence file. A paid product would need different text. |
| D7 | The build **fails** if a quote is not found word for word in the source, or if it points at a figure the page doesn't show ("()", "(see b)", "( and )", "(see and )", "(; see also )", "As shown in ,"). | Guarantees every quote is exact and complete on the page. |
| D8 | Every structure **name and FMA ID comes from the dataset**. When dataset and textbook wording differ, both are shown as they are. | No renaming by us. |
| D9 | Organs are selected by **FMA concept or exact dataset name**, not by the dataset's "system" field. | The system field has errors (brain ventricles under "cardiac", liver tissue under "venous", choroid plexus under "sensory"). |
| D10 | Meshes with **errors in the source data are left out** (not corrected) and listed on the page with the reason. | Correcting the source ourselves would be an assumption. |
| D11 | **Gaps are shown, not filled**: "Not in this model" and "About this model" boxes on each page. | Students must know what the model does not show. |
| D12 | **Two whole bodies, male and female** (switch on the body page), made to look alike: the female body is the male reference body with only the pelvic region replaced (D36). | The user asked for both bodies to be the same except for the parts that differ between the sexes. |
| D13 | Workstation layout **inspired by the reference video** (an angiogram trainer): context view, main 3D view, exact controls, orientation cube, leader-line labels. **None of its angiogram content is copied.** | The user asked to use it as a layout reference only. |
| D14 | Workstation features: organ-in-region context view that turns with the main view; labels; section cuts (transverse, coronal, sagittal) through the real geometry; explode; see-through; standard anatomical views with angle readouts; orientation cube (A/P/L/R/S/I); guided tour; part list with FMA IDs. | Agreed after the heart workstation was shown. |
| D15 | **Lungs are shown without lung surfaces.** Lobes are shown through the airways and vessels the dataset assigns to them. | The dataset has no lung surface, fissure or pleura meshes; drawing an outline would be invented. |
| D16 | **Brain grouping**: by quoted OpenStax sentences first, then each mesh's FMA concept; anything neither places goes under "Other". | The dataset's own brain concept is incomplete. |
| D17 | Organs that are **single meshes** (spleen, diaphragm) get quoted text in the body view but **no workstation**. | Nothing to study inside a single surface. |
| D18 | **Great vessels are cut short** near the heart; near-duplicate surfaces (pancreas/parenchyma, duct/duct tree) start with one hidden. | Clear framing; avoids two surfaces flickering through each other. Nothing is deleted. |
| D19 | **Size comparisons** between model and textbook are shown as plain notes, without conclusions. | One reference body; measured from simplified scan data. |
| D20 | Geometry is stored as base64 gzip text (`.gz.txt`). | The artifact host does not serve raw binary files. |
| D21 | Work is saved to GitHub `Maianki/anatomy`, branch `claude/new-session-oqwx8r`, folder `anatomy-atlas/`. | The cloud container is temporary. |
| D22 | A **Sources page** lists the 3D dataset (publisher, licence, paper, download, how the data reaches the app), the textbook (publisher, licence, source files), every OpenStax section quoted with its quote count and where it is used, FMA IDs, software, and the review status. It is built from what the app actually uses (`build/content_sources.py`). OpenStax authors are not typed in; the page links to OpenStax's contributor list. | Shows students and reviewers where everything comes from. Avoids writing citation details from memory. |
| D23 | **Redesign**: Poppins for the interface, Source Serif 4 only for quoted textbook passages; light and dark themes; 3D views always on a dark stage; organ pages use tabs (Learn, Parts, Tour, Notes) with the region view as a picture-in-picture; organ cards with search on the body page. | The first UI was hard to use. Serif quotes make it obvious which words are from the textbook. |
| D24 | Organ workstation meshes are simplified **only as far as keeps every original vertex within 1 mm** of the displayed surface (`common.py`, `MAX_DEV`). The whole-body view and the small region views are simplified further, as overviews. | Accuracy of what students study, with files small enough for phones. |
| D25 | **Verification is part of the build record**: `verify_openstax.py` (every quote and link against the live site), `verify_bp3d.py` (names, FMA IDs and positions against the official archive), `verify_output.py` (the files the app loads against the official meshes). Results are kept in `sources/verification/` and shown on the Sources page with the date. | Anyone can see what was checked and when. |
| D26 | Quotes from a section's "Chapter Review" paragraph link to the chapter's review page on openstax.org. | On the live site those paragraphs are not on the section page, so the link would not land on the quote. |
| D27 | The app shows BodyParts3D's **required credit line** word for word: "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International". | Required by the licence page (updated 2025-02-27). |
| D28 | **Every organ workstation has the heart's tools**: see-through (the organ's outer parts turn faint) and a vessel button (named for what it shows: "Great vessels", "Vessels" or "Arteries"). The tour's Play button flies the camera to each step's parts and labels them. | The user found these only on the heart. Play did advance on every organ, but the highlighted parts could be off screen. |
| D29 | **Digestive tract vessels and brain arteries** were added from the dataset. Gut vessels are chosen by dataset name (mesenteric, gastric, colic and so on, split into arteries and veins). Brain arteries are the dataset's branches of the internal carotid and vertebral arteries, with the trunks cut short below the brain. | Gives the gut and brain a vessel view like the heart's. The vessels come from dataset names and concepts only. |
| D30 | **Bones**: the body page has an **Organs / Bones switch**, so the two are never clickable at the same time. Bones mode turns organs and muscles off. There are six bone workstations, each built from the dataset's own FMA concept: skull, vertebral column, rib cage (thoracic cage), left and right upper limb, bony pelvis, left and right lower limb. "Skeleton" means the dataset's bone organs plus costal cartilages, intervertebral disks and the three parts of the sternum. Inside a region, bones are grouped under the OpenStax heading that names them (sections 7.2–7.4, 8.1–8.4); the build fails if a bone matches no heading or two. The hip bones are in the pelvis workstation, as in OpenStax 8.3. The sacrum appears in both the vertebral column and the pelvis. | Requested by the user. Choosing organs or bones first avoids clutter. The regions and groups follow the dataset and the textbook rather than our own choices. |
| D31 | In the body view, meshes in the FMA concept "muscle organ" that the dataset files under the skeletal system are shown in the Muscles layer. | The "system" field files some muscles as skeletal (D9). |
| D32 | **Identical duplicate meshes are shown once.** Five pairs in the official archive have the same FMA ID and byte-identical geometry. The build keeps the lower mesh ID, records the other in the scene file, and shows it in the Notes tab. | Two identical surfaces in the same place flicker and are counted twice. Nothing differs between them, so nothing is lost. |
| D33 | **WebMD is used only to cross-check facts**, as D5 requires. No WebMD text, image or model is copied. For each check, `sources/crosscheck/webmd.json` records our quote, the WebMD page (title, reviewer, date), whether the two agree, and a summary in our own words. It is shown on the Sources page with a thank-you. **NIH 3D is not used**, so it is not credited. | The user asked for a shout-out to sources used. Crediting a source we did not use would be inaccurate. |
| D34 | Every selected part shows the BodyParts3D credit with a link to the licence, beside its FMA ID and mesh ID. | "Citations everywhere": each 3D part carries its source, as each quote does. |
| D35 | **Male reproductive workstation** from BodyParts3D: the 12 meshes the dataset files as reproductive, plus the urethra, the dorsal vessels of the penis, the testicular arteries and veins, and the bladder for context. Text from OpenStax 27.1 (titled "Anatomy and Physiology of the Testicular Reproductive System" in the current edition) and 25.2. Passages on disorders (prostate enlargement, prostate cancer, vasectomy) are left for version 2. The body view now shows these organs and the urethra; before this they were missing from it. | Requested by the user. Every mesh is from the dataset; the build fails if a candidate mesh matches no group or two. |
| D36 | **Female body = the BodyParts3D reference body + the Visible Human Female pelvic region.** Same skeleton, muscles, vessels, nerves and organs as the male body. The pelvic region comes from the Human Reference Atlas (HRA) 3D Reference Object Library (HuBMAP; github.com/hubmapconsortium/ccf-releases, v1.2 models with their metadata, commit b036a91, files pinned by SHA-256; CC BY 4.0 with a DOI per model): hip bones, sacrum, coccyx, bladder, uterus, uterine tubes, ovaries and uterine arteries and veins, all from the Visible Human Female (NLM; a 59-year-old woman). They are placed as one block by a single rigid fit (rotation and translation, **no resizing**) of her pelvis onto the male pelvis (ICP, `build8.py`), so they keep their real sizes and arrangement. Removed from the male body: hip bones, sacrum, bladder, urethra, all reproductive organs, and the penile and testicular vessels. The male skin is kept with the external genital region cut away (12,244 triangles in a box around the penis and testes); the female skin was not used because it is 5 cm shorter with the arms raised, so male bones would pass through it. | The user asked for the female body to match the male except the parts that differ, and, after seeing the measured options, to use the female parts for the pelvic region rather than male ones. Using her pelvis together with her organs keeps them in true relation to each other. |
| D37 | The body page's bone search also matches the names of the bones inside each region ("femur" finds Lower limbs), and a selected region lists its bone groups. | The user could not find the femur: it was in the Lower limbs workstation, but nothing on the body page named it. |
| D38 | **Measured limits of the fit, shown in the app** (body page note and Sources page, from `female-fit.json`): rotation 6.5°, median pelvis surface gap 8.2 mm; the female hip joints sit 15.3 mm (left) and 21.5 mm (right) from the male femoral heads, because her hips are 3.1 cm wider; the male ureters end 16.5–23.7 mm short of her bladder; about half of the ovaries' and uterine tubes' surface points lie inside the male "descending colon" mesh (which reaches into the left pelvis), and 10.7% of the ovaries inside the right psoas major. These are not hidden or corrected. | Accuracy: mixing two people's anatomy cannot fit exactly, so the app says where it does not. Options considered and rejected: keeping the male bladder (28% of the uterus inside it), shifting the organs 2.9 cm (they then collide with the colon and ileum, and the position would be our choice). |
| D39 | **Female-only workstations**: female reproductive system (uterus, cervix, uterine tubes, ovaries, uterine vessels, her own bladder for context; text from OpenStax 27.2) and female pelvis (ilium, ischium, pubis, sacrum, coccyx; OpenStax 8.3 including its female/male comparison, and 7.3). These show the Visible Human Female parts in their own, unfitted positions. All other organs and bone regions open the same workstations as the male body. | The workstations show the real female arrangement; the body view shows how it sits in the shared reference body. |

## 3. What is built

| Workstation | Opened from body view | Tour | Text (OpenStax sections) |
| --- | --- | --- | --- |
| Heart | Heart | Blood flow, 12 steps | 19.1 |
| Lungs | Left lung, right lung, trachea | Air and blood, 6 steps | 22.1, 22.2 |
| Liver, gallbladder and pancreas | Liver, gallbladder, pancreas | Blood and bile, 7 steps | 23.5, 23.6 |
| Digestive tract | Esophagus, stomach, small and large intestine | Path of food, 10 steps | 23.3, 23.4, 23.5 |
| Urinary system | Kidney, urinary bladder | Path of urine, 5 steps | 25.2, 25.3 |
| Brain | Brain | Path of CSF, 7 steps | 13.2, 13.3 |
| (body view only) | Spleen, diaphragm | none | 21.1, 22.2 |
| Skull (bones mode) | Skull | Bone by bone, 3 steps | 7.2 |
| Vertebral column | Vertebral column | Bone by bone, 5 steps | 7.3 |
| Thoracic cage | Thoracic cage | Bone by bone, 3 steps | 7.4 |
| Upper limbs | Upper limbs | Bone by bone, 8 steps | 8.1, 8.2 |
| Pelvis | Pelvis | Bone by bone, 2 steps | 8.3, 7.3 |
| Lower limbs | Lower limbs | Bone by bone, 8 steps | 8.4 |
| Male reproductive system | Testis, epididymis, deferent duct, seminal vesicle, prostate, penis | Path of sperm, 7 steps | 27.1, 25.2 |
| Female reproductive system (female body) | Uterus, uterine tube, ovary | Path of the oocyte, 6 steps | 27.2, 25.2 |
| Pelvis (female) | Pelvis in the female body, bones mode | Bone by bone, 6 steps | 8.3, 7.3 |

Quoted sections also include the Chapter 19 Chapter Review page (one heart quote).

Live demo: https://claude.ai/artifact/Scn9ufkjgswd4MQXWQj1HK (private until shared).

## 4. Data findings

### Errors in the source data (left out everywhere)

| Mesh | Problem |
| --- | --- |
| Right anterior segmental artery (FJ2041, FJ2044, FMA8620) | Sits 22–26 cm below the rest of its lung segment, at liver level. **Confirmed in the official archive.** |
| Brachium of left superior colliculus (FJ1735, FMA73462) | Lies on the right side of the body. |
| Brachium of right superior colliculus (FJ1736, FMA73461) | Lies on the left side. The colliculi themselves are on the correct sides, so the two names look swapped. **Confirmed in the official archive.** |

### Duplicates in the source data (each shown once, D32)

| Kept | Left out | Name (FMA ID) |
| --- | --- | --- |
| FJ2772 | FJ3201 | Hyoid bone (FMA52749) |
| FJ2440 | FJ2769 | Cricoid cartilage |
| FJ1846 | FJ2013 | Celiac artery |
| FJ1916 | FJ2386 | Hepatic artery piece |
| FJ1924 | FJ2394 | Hepatic artery piece |

The geometry and the FMA ID are identical in each pair (checked on the official meshes).

### Left out of a workstation for other reasons (still in the body view)

- Interpeduncular fossa (a space) and tentorium cerebelli (dura mater): not brain tissue.

### Gaps (not in the dataset)

- **Lungs:** surfaces, fissures, pleura. No artery for right lower lobe medial basal; no veins for
  left lower lobe superior and medial basal.
- **Liver:** common bile duct, hepatopancreatic ampulla, ligaments. "Hepatovenous segment IX" exists
  but is not in the dataset's liver concept (included, with a note).
- **Digestive tract:** cecum, sigmoid colon, anal canal.
- **Kidneys:** single outer surfaces (no cortex, medulla, pyramids). The ureter meshes branch inside
  each kidney; the branches are not named, so they are not labelled as renal pelvis or calyces.
- **Brain:** meninges and spinal cord (apart from its central canal) are not in the workstation. Of the
  blood vessels, only the internal carotid and vertebral artery branches are shown. The dataset's brain
  concept omits the corpus callosum, thalamus, basal nuclei, amygdala and others.
- **Bones:** no coccyx mesh and no auditory ossicles (malleus, incus, stapes); costal cartilage meshes for ribs 1
  to 7 only. The teeth are in the body view, not the skull workstation. Against the usual adult count of 206
  bones, the dataset has 199: every other bone is present, each as its own mesh (the sternum as three parts).
- **Male reproductive:** no scrotum, spermatic cord, ejaculatory ducts, bulbourethral glands or prepuce. The
  urethra is one mesh (its four regions are not separate).
- **Female body:** no vagina, vulva, breasts or female urethra; no ovarian arteries or veins; no female skin shape
  (male skin with the genital region removed). The pelvic region is fitted, with the limits in D38.
- **HRA metadata error:** the uterus model's metadata says it was made from the Visible Human Male, in every release
  (v1.1 to v2.0). A uterus cannot come from a male body, and the model sits in the female body's frame with the other
  female organs, so this looks like a metadata error. It is shown with a note. Consider reporting it to HRA.

### Gaps in the text (OpenStax)

- Does not describe individual bronchopulmonary segments by name.
- Describes the liver by lobes, not the numbered segments the model uses.
- Does not name 50 of 107 brain meshes (mostly individual gyri and tracts).
- Some small heart vessels have no passage of their own; the group's passage is shown with a note.
- The dataset's "triquetral" is the textbook's "triquetrum"; both names are shown.
- The textbook describes sesamoid bones in general (in its section on the patella), not the sesamoid
  bones of the foot by name. A note says so.

### Sizes compared with the text (longest axis, `build/measure.py`)

| Organ | Model | OpenStax |
| --- | --- | --- |
| Kidney | 10.8 cm (left), 10.6 cm (right) | 11–14 cm |
| Spleen | 10.7 cm | about 12 cm |
| Gallbladder | 6.0 cm | 8–10 cm |
| Testis | 2.9 cm (each) | about 4–5 cm |
| Uterus with cervix (female body) | 6.3 × 5.2 cm | about 7 × 5 cm |
| Ovary (female body) | 2.5 cm (left), 2.6 cm (right) | 2–3 cm |

The right kidney sits about 2 cm lower than the left, as the text says.

### Verification against the original sources (2026-10-24)

- **OpenStax:** all 418 quotes found word for word on the live openstax.org pages; all 22 links open the right page
  and land on the quoted paragraph (`sources/verification/openstax.json`). This check caught one quote with an empty
  figure reference, "(; see also )", which the build's guard then learned to reject (D7).
- **BodyParts3D names:** all 2,234 meshes exist in the official archive; every name and FMA ID matches the official
  tables (`sources/verification/bodyparts3d.json`).
- **BodyParts3D positions:** with one fixed conversion (mm to m, Z-up to Y-up, feet at origin), every mesh centre in
  the npm copy matches the official archive to 0.00 mm.
- **Female geometry:** in the female reproductive and pelvis workstations every original HRA vertex lies within
  1.0 mm of the displayed surface (`build/verify_hra.py`, `sources/verification/geometry-hra.json`).
- **Geometry shown:** in every organ and bone workstation, every original vertex lies within 1.0 mm of the displayed surface
  (`sources/verification/geometry.json`).
- **Licence:** the current licence page says CC BY 4.0 (updated 2025-02-27). The OBJ files still carry an older
  CC BY-SA 2.1 Japan notice, which the licence page replaces.
- **Brain grouping:** for the 59 brain meshes the official BodyParts3D part-of tree covers, it agrees with the groups
  used (cortex in the telencephalon, brain stem parts in the midbrain, pons or medulla, and so on). This evidence is
  now shown in the brain notes.

### Checks that pass

- Every quote found word for word; no quote points at a missing figure.
- 10 bronchopulmonary segments per lung; each lung mesh in exactly one lobe; segment heights in
  anatomical order.
- Every heart mesh within 3 cm of the heart walls.
- No left/right mismatches in lungs, digestive tract, urinary system, abdomen. Heart "right"
  structures lie up to 3 cm left of the midline, matching the text ("the right side of the heart is
  deflected anteriorly"). A few "left" liver vessels lie within 2 cm right of the midline.
- A clean rebuild reproduces every data file exactly.

### Cross-check with WebMD (2026-10-24, D33)

| Fact (our source) | Result |
| --- | --- |
| Heart has four chambers (OpenStax 19.1) | Agrees |
| Heart about the size of a fist (OpenStax 19.1) | Agrees; WebMD gives no measurements |
| Right lung three lobes, left lung two (OpenStax 22.2) | Agrees |
| Small intestine about 3.05 m in a living person, about twice that in a cadaver (OpenStax 23.5) | **Differs**: WebMD says more than 20 feet spread out. The app keeps the OpenStax sentence, which states both figures. |
| Gallbladder on the underside of the liver (OpenStax 23.6) | Agrees |
| Midbrain, pons, medulla from top to bottom (OpenStax 13.2) | Agrees |
| Skull: 8 brain-case and 14 facial bone meshes in the dataset | Agrees with WebMD's 22 bones and its list of 14 facial bones |

WebMD's kidney and liver "picture" pages now open disease articles, so there was nothing to compare there.

### Corrections made during the project

- OpenStax licence corrected from CC BY to CC BY-NC-SA (D6).
- The liver was first missing its main tissue because vessel meshes were excluded; fixed by selecting
  organs by FMA concept (D9).
- "Renal pelvis not modelled" was wrong; replaced with the accurate description of the ureter meshes.
- A sentence splitter bug joined two heart sentences in one quote; fixed and all text rebuilt.
- "Brachium of … colliculus" was briefly grouped with the brain stem by a loose name rule; it now
  follows its FMA white-matter concept.
- The npm copy's simplification moved parts of long vessels (aorta, inferior vena cava, oesophagus) by up to about
  7 mm; geometry now comes from the official archive (D3, D24).
- The heart's chapter-review quote linked to a page that doesn't contain it on the live site; it now links to the
  chapter review page (D26).
- The body view's brain used the dataset's incomplete brain concept (59 meshes); it now uses the same 106 brain
  meshes as the brain workstation.
- An edit to this file on 2026-10-24 accidentally dropped sections 3 to 6; they were restored from the previous commit.

## 5. Needs checking (open items)

- [ ] **Educator review** of structure names, the brain grouping, the quoted passages, and every item in section 4.
- [x] **Check the repackaged data against the original** BodyParts3D archive. Done 2026-10-24; geometry now comes from the official archive.
- [x] **Confirm the brachium name swap** and the misplaced lung arteries against the original archive. Both are in the official data. Consider reporting them to DBCLS.
- [x] **Open every OpenStax section link.** Done 2026-10-24: all 22 pages and all 418 quotes verified on the live site.
- [x] **Female body (D36):** built from the HRA Visible Human Female models (GitHub copy; humanatlas.io itself is blocked here).
- [ ] **Decide on commercial use.** If the app will be paid, replace the OpenStax text (D6).
- [ ] **Educator review of the female body**, especially the uterus metadata note (D36) and the shared-workstation approach (D38).
- [ ] **Decide whether lungs need surfaces** from a second source, which would need its own checks (D15).
- [ ] **Test on real phones, tablets and laptops** with a GPU. So far tested only in headless Chromium with software rendering.
- [ ] **Review naming differences** between dataset and textbook (papillary muscles, "pineal body" vs "pineal gland", "superior temporal gyrus" vs "superior temporal lobe", older segment names).
- [x] **Network access:** `dbarchive.biosciencedbc.jp`, `openstax.org`, `3d.nih.gov` and `www.webmd.com` are reachable (2026-10-24).
- [x] **WebMD** is used for cross-checks only (D33). **NIH 3D** is not used; any model taken from it would need its own licence check and the same accuracy checks as BodyParts3D.
- [ ] **Educator review of the bone grouping** (D30), especially the sacrum shown in two regions and the hyoid listed with the skull.
- [x] **Body-view brain now matches the brain workstation** (106 brain meshes; the pituitary context mesh is not counted).

## 6. Next steps

- Version 1: educator review, real-device testing, then any further organs the data supports.
- Version 2: diseases, using the disease passages already identified in the same OpenStax sections.
