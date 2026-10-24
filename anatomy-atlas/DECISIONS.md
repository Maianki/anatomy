# Anatomy Atlas: decisions, gaps and review checklist

The single reference for what we are building, what has been decided and why, what the data is
missing, and what still needs checking. Update it whenever a decision changes or a check is done.

Last updated: 2026-10-24 (sources page and redesign added).

## 1. What we are building

- **Goal:** an interactive 3D app for students, especially medical students, to learn human organs
  and their parts.
- **Version 1 (now):** organs and their parts (normal anatomy).
- **Version 2 (later):** diseases. Disease passages in the textbook are deliberately left out of version 1.
- **Flow:** a whole human body opens first. Tapping an organ selects it. Organs with enough detail
  open an organ workstation: the organ alone in 3D, with its parts named, quoted text and a guided tour.
- **Top priority:** accuracy. Nothing is assumed or invented. Where something is unclear or missing,
  the app says so.

## 2. Decisions

| # | Decision | Why |
| --- | --- | --- |
| D1 | Build a **web app**, not a native app. It can be wrapped for app stores later (for example with Capacitor). | One codebase for phones, tablets and laptops, opened from a link, with no app-store review. |
| D2 | **No hand-made geometry.** All 3D models come from a scan-based anatomy dataset. | The first hand-built heart demo was rejected; hand modelling can't be accurate enough for teaching. |
| D3 | 3D source: **BodyParts3D 4.0** (Database Center for Life Science, CC BY 4.0), via the npm package `@dagno/anatomy-model@0.1.2`. | Built from MRI scans, separate named meshes, FMA IDs, free with credit. The original site and NIH 3D were blocked by this environment's network settings; the npm copy was reachable and credits the original. |
| D4 | Text source: **OpenStax Anatomy and Physiology 2e**, quoted **word for word**, each quote linked to its section. Taken from OpenStax's official GitHub repository. | Peer-reviewed textbook for students. Quoting unchanged avoids errors in paraphrase. |
| D5 | **WebMD is not used for text.** It may be used only as a reference to cross-check facts. | WebMD's text is copyrighted. |
| D6 | OpenStax is **CC BY-NC-SA 4.0** (non-commercial, share-alike), not CC BY as first stated. | Corrected after reading the licence file. A paid product would need different text. |
| D7 | The build **fails** if a quote is not found word for word in the source, or if it points at a figure the page doesn't show ("()", "(see b)", "As shown in ,"). | Guarantees every quote is exact and complete on the page. |
| D8 | Every structure **name and FMA ID comes from the dataset**. When dataset and textbook wording differ, both are shown as they are. | No renaming by us. |
| D9 | Organs are selected by **FMA concept or exact dataset name**, not by the dataset's "system" field. | The system field has errors (brain ventricles under "cardiac", liver tissue under "venous", choroid plexus under "sensory"). |
| D10 | Meshes with **errors in the source data are left out** (not corrected) and listed on the page with the reason. | Correcting the source ourselves would be an assumption. |
| D11 | **Gaps are shown, not filled**: "Not in this model" and "About this model" boxes on each page. | Students must know what the model does not show. |
| D12 | **Adult male body only** for now. A female body is added only when a verified source exists. | No verified free female full-body model with separate organs was found. |
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
