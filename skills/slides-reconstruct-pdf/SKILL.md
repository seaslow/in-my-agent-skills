---
name: slides-reconstruct-pdf
description: >-
  Reconstruct the most likely lecture, argument, and teaching intent behind one
  or more PPTX or slide-exported PDF files, using slide-grounded evidence,
  explicit uncertainty labels, visual inspection, and cross-slide reasoning;
  deliver a polished, figure-rich course-note PDF. Use when slides exist but the
  recording, transcript, or reliable speaker notes are missing. Do not use for
  ordinary deck summarization, slide creation, or transcription of an available
  recording.
---
# Slides Reconstruct PDF

Helper files (scripts/, references/, assets/) live in this skill's folder.

Reconstruct a defensible *likely lecture*, not a fictional transcript. The final PDF should help a reader understand what the author was trying to establish, how the deck develops that argument, what each important visual contributes, and where the evidence stops.

## Non-Negotiable Boundary

Never present generated prose as words the speaker actually said. Separate direct slide evidence, cross-slide inference, plausible reconstruction, and external enrichment according to references/evidence-protocol.md. Preserve competing interpretations when the deck does not resolve them.

## Input Decision

Prefer the original `.pptx`. Accept slide PDFs when PPTX is unavailable. When both exist, use PPTX as the structural source and PDF as a rendering cross-check. Read references/input-handling.md for multiple decks, links, media, old `.ppt`, Keynote, and PDF-only limitations.

## Deliverable

One compiled PDF. Keep the `.tex`, manifests, rendered slides, extracted assets, and QA images in the working directory; surface them only on request. Use `assets/report-template.tex` and follow references/report-structure.md. Default to Chinese unless the user requests another language.

## Workflow

### 1. Establish the source set
Record input files, order, language, and course context. Ask only for information that materially changes interpretation. Create `<deck-stem>-reconstruction/` with `<course-title>.pdf` and `work/` (source-manifests/, rendered-slides/, extracted-assets/, evidence-ledger.md, reconstruction.tex, qa/).

### 2. Extract structure and render every page
```bash
python scripts/inspect_deck.py INPUT --output work/source-manifests/NAME.json
python scripts/render_deck.py INPUT --output-dir work/rendered-slides/NAME
python scripts/extract_assets.py INPUT --output-dir work/extracted-assets/NAME
```
Extraction applies to PPTX. If a tool is missing, use an equivalent renderer and document the limitation. For PDF, extracted text is only an index, never a substitute for visual inspection.

### 3. Build the evidence inventory
Inspect every rendered slide directly; skip none. Record visible text and hierarchy; figures, diagrams, charts, tables, equations, code, screenshots, citations, captions; spatial relations, arrows, grouping, emphasis, progressive states; notes, links, media, hidden status; unreadable or ambiguous elements. Do not infer illegible values; crop or enlarge first.

### 4. Reconstruct globally before writing locally
1. Page pass: each page's explicit content and rhetorical role.
2. Deck pass: segments, central question, thesis, dependencies, evidence chain, turning points, conclusion.
3. Return pass: revisit every page against the global structure.
For multiple decks, reconstruct each first, then the shared arc; don't force one narrative.

### 5. Maintain an evidence ledger
Create `work/evidence-ledger.md` per the evidence protocol. Every substantive claim resolves to a page anchor or is labeled external context. Test adversarially: what supports it, does another reading fit, did domain knowledge slip in, do adjacent slides contradict it, would it be writable without the deck?

### 6. Write the report
Start from `assets/report-template.tex`. Write as a patient teacher, keeping the author's terminology and order. For each major section cover the problem, likely claim, mechanism or derivation, slide evidence with page refs and figures, implication and transition, and uncertainties. Boxes: `sourcebox` (E0 direct evidence), `claimbox` (E1 cross-slide conclusion), `reconstructbox` (E2 plausible explanation), `uncertaintybox` (ambiguity). Use rendered slides or crops when layout matters; label redraws as interpretation.

### 7. Compile and verify
```bash
python scripts/compile_report.py work/reconstruction.tex --output '<course-title>.pdf'
```
Render the PDF to images and inspect every page for clipped text, broken links, missing glyphs, unreadable figures, orphan headings, bad breaks, split boxes, and unanchored claims. Recompile until sound.

## Acceptance Criteria
- The final PDF opens and every page renders.
- Every input slide is accounted for.
- Important figures are readable and tied to slide numbers.
- Evidence and reconstruction are distinguishable.
- Includes a deck-level argument map, section teaching notes, page-level coverage, alternative readings, and a final synthesis.
- No uncertain content is attributed to the speaker as fact.
