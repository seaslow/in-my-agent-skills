---
name: notes2deck
description: >-
  Turn study material (a textbook chapter or section, PPTX/PDF slides, or
  lecture PDFs) into a polished, figure-rich, evidence-labelled course handout
  PDF; and, only when the user explicitly asks for a PPT/deck, also a
  presentation .pptx built from that handout. Use for 讲义, course notes,
  reconstructing a lecture from slides, or a 汇报 PPT for a textbook section. Not
  for plain deck summaries or transcribing an available recording.
---
# notes2deck

Helper files (scripts/, references/, assets/) live in this skill's folder.

Two outputs, one pipeline:
1. **Handout (default, always):** a compiled course-note PDF that explains the material for self-study, with evidence labels and page anchors.
2. **Presentation deck (only on explicit request):** a `.pptx` for presenting, distilled from the finished handout. Never build one unless the user asks for a PPT, deck, or slides to present.

## Non-Negotiable Boundary

Never present generated prose as words the source actually says. Separate direct source evidence, cross-page inference, plausible explanation, and external enrichment per references/evidence-protocol.md. Preserve competing interpretations when the source does not resolve them. For slide inputs, never present reconstruction as what the speaker said; for textbook inputs, never attribute to the book what it does not print, and cite book page numbers.

## Input Decision

Read references/input-handling.md.
- **Slides mode:** PPTX or slide-exported PDF without a recording. Prefer `.pptx`; PDF as a rendering cross-check.
- **Textbook mode:** a book chapter or section (often a scanned PDF). Use the book's own section numbers, theorem, algorithm, example and equation numbers. Verify every worked example numerically (exact fractions where possible) and flag typos as notes, not silent fixes.

## Handout Workflow

### 1. Establish the source set
Record input files, order, language, and course context. Ask only for what materially changes interpretation. Create `<stem>-handout/` with the final PDF and `work/` (source-manifests/, rendered-pages/, extracted-assets/, fig/, evidence-ledger.md, handout.tex, qa/).

### 2. Extract structure and render every page
```bash
python scripts/inspect_deck.py INPUT --output work/source-manifests/NAME.json   # PPTX
python scripts/render_deck.py INPUT --output-dir work/rendered-pages/NAME
python scripts/extract_assets.py INPUT --output-dir work/extracted-assets/NAME    # PPTX
```
For PDFs (slides or textbook), render pages with `pdftoppm`; extracted text is only an index, never a substitute for looking at the page. Crop figures, algorithms and tables you will reuse into `work/fig/`.

### 3. Build the evidence inventory
Inspect every rendered page directly; skip none. Record text and hierarchy, figures, tables, equations, algorithms, examples, captions, emphasis, and unreadable or ambiguous elements. Crop or enlarge before reading small values.

### 4. Reconstruct globally before writing locally
Page pass (content and role of each page), whole-source pass (sections, central question, dependencies, conclusion), then a return pass against that structure.

### 5. Evidence ledger
Keep `work/evidence-ledger.md` per the protocol. Every substantive claim resolves to a page anchor or is labelled external.

### 6. Write the handout
Start from `assets/report-template.tex`, follow references/report-structure.md. Default to Chinese unless asked otherwise. Write as a patient teacher for a reader new to the topic: plain explanations first, derivations only as deep as needed, every symbol defined. Keep the source's terminology and order. Boxes: `sourcebox` (E0), `claimbox` (E1), `reconstructbox` (E2), `uncertaintybox` (ambiguity). Where it helps, reproduce key numerical results yourself (e.g. Python plots of iteration paths) and label them as reproductions.

### 7. Compile and verify
```bash
python scripts/compile_report.py work/handout.tex --output '<title>.pdf'
```
Render the PDF and inspect every page for clipped text, missing glyphs, unreadable figures, orphan headings, split boxes, and unanchored claims. Recompile until sound.

## Presentation Deck (only when asked)

Read references/presentation-deck.md in full and follow it. In short: the deck is for presenting, not studying. Follow the source's section structure with its section names as titles; concise; no meta pages, questions, or presenter tips on slides; the handout's visual style; small colored boxes only for conclusions; Times New Roman + 等线; timed speaker notes; run `scripts/pptx_fonts.py` and `scripts/pptx_check.py` before delivery.

If a platform deck workflow exists (e.g. a `slides` skill), use it for the build mechanics, and pass every rule in references/presentation-deck.md into its brief.

## Acceptance Criteria
- Handout PDF opens and every page renders; every source page is accounted for.
- Important figures readable and tied to page numbers; evidence and reconstruction distinguishable.
- Worked examples verified; typos flagged with page numbers.
- Slides mode also includes an argument map, page-level coverage index, alternative readings, and final synthesis.
- If a deck was requested: it passes every check in references/presentation-deck.md and opens in PowerPoint without a repair prompt.
