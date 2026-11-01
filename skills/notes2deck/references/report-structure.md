# Report Structure

The PDF is a course note and reconstruction audit in one document. It should read naturally without hiding uncertainty.

## Required Front Matter

1. Title page with course/deck title, source files, source author when known, reconstruction date, and a representative original slide image.
2. Reconstruction notice: explain that no recording or transcript was available and define `E0-E3` briefly.
3. Table of contents.
4. Executive course map: central question, likely thesis, section sequence, and the strongest uncertainties.

## Main Sections

Organize around the deck's recoverable teaching structure, not mechanically one chapter per slide. Each major section should progress through:

1. Motivation or problem.
2. Most likely claim.
3. Mechanism, derivation, framework, or conceptual move.
4. Examples and slide evidence.
5. Implication and transition.
6. Section summary.

Retain original ordering unless the deck itself supports a better conceptual grouping. If the report changes order for teaching clarity, say so and retain original slide references.

## Figures

- Prefer original rendered slides or high-resolution crops when spatial arrangement carries meaning.
- Captions must name the source deck and slide number.
- Keep the caption and figure on the same page when practical.
- If redrawing a diagram or chart, label it "Reconstructed diagram" and cite the source slides.
- Do not improve, clean, or complete a source visual in a way that conceals missing evidence.

## Formulas and Code

For a formula, explain its purpose in plain language, show it in display math, then define every visible symbol. Do not invent omitted variables or assumptions; record them as uncertainty.

For code, explain its role before the listing and expected behavior after it. Preserve source code exactly when legible; label repaired or completed code as reconstruction.

## Page-Level Coverage

The main prose may combine related slides. Include a compact appendix titled `逐页重建索引` so every input slide remains auditable. Each entry should state:

- page title or visual identifier
- rhetorical role
- one-sentence likely point
- evidence level and confidence
- location in the main report
- uncertainty, if any

Contentless divider pages can receive a one-line entry.

## Final Section

End with `总结、边界与延伸`, containing:

- the deck's most defensible central claims
- how the major sections connect
- what the author likely wanted the audience to retain
- contradictions, missing premises, and unresolved ambiguity
- external context clearly separated from source-derived conclusions
- questions that a recording, transcript, or author could resolve

Do not add generic study tips or speculative future work unless the material supports them.

## Textbook Mode Adjustments

- Main sections follow the book's own section order and titles (e.g. 3.4.1 … 3.4.5).
- Replace `逐页重建索引` with a compact `教材页码索引`: book page → handout section.
- Include a figure of a reproduced result on the title page when one exists (it doubles as the deck's motivation figure).
- End with `总结与延伸`: core results, how they connect, typos found, and external context kept separate.
- Pitch the explanation at a newcomer: intuition before formula, define every symbol, step-by-step arithmetic for worked examples.
