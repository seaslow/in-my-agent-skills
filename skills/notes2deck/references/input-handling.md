# Input Handling

## Preferred Formats

| Input | Use | Limitations |
|---|---|---|
| `.pptx` | Preferred structural source | Rendering can vary by fonts, PowerPoint version, and unsupported effects |
| slide-exported `.pdf` | Supported visual source and rendering cross-check | Usually loses notes, object identity, animation, hidden slides, embedded files, and some link semantics |
| `.ppt` | Convert to `.pptx` first | Binary format is not directly inspected by the bundled script |
| Keynote | Export both `.pptx` and `.pdf` when possible | PPTX preserves structure; PDF preserves the author's final appearance |

When the user can provide only one format, request PPTX. When confidentiality or macro risk matters, note that `.pptx` is a ZIP-based XML format and does not carry VBA macros; macro-enabled `.pptm` requires separate handling and should not be executed.

## Multiple Decks

Infer relationships conservatively from filenames, title pages, numbering, recurring section labels, prerequisites, and explicit references.

- Preserve each deck's own slide numbers.
- Assign stable labels such as `Deck A`, `Deck B`.
- Do not reorder files solely to produce a smoother story.
- If more than one plausible course order exists, report the alternatives.

## Hyperlinks

Inventory every link and its anchor text. Follow a link only when it materially affects interpretation and access is within the user's request.

- Record fetched content as `E3 External`.
- Promote a specific linked claim to `E0` only when the slide visibly quotes, reproduces, or explicitly endorses it.
- Report dead, private, or inaccessible links.
- Do not recursively crawl unrelated pages.

## Embedded Media

Inventory audio, video, OLE objects, and embedded files without executing them.

- A poster frame proves only what the frame shows.
- A filename or relationship target does not prove media content.
- If the media can be safely extracted and inspected, treat its actual contents according to their provenance.
- If it cannot be inspected, identify the missing evidence and keep any reconstruction at `E2` or lower confidence.

## Notes, Hidden Slides, and Animations

- Existing speaker notes are strong `E0` evidence of intended narration, but may be stale or incomplete; compare them with the visible slide.
- Hidden slides are evidence about the deck's development or optional material. Do not insert them into the main lecture sequence unless other evidence supports that use.
- Object order can hint at progressive reveal, but does not reliably recover animation timing. Treat inferred reveal order as `E2` unless animation XML or multiple exported states make it explicit.

## PDF-Only Mode

State the limitation near the beginning of the report: the reconstruction is based on final rendered pages and cannot reliably recover notes, builds, hidden material, or embedded-object semantics.

Use text extraction only for indexing. Inspect each page image directly for layout, figures, equations, and hierarchy.

## Textbook Mode

Input is a textbook chapter or section, usually a scanned PDF. The user may delete a large book after one use; keep page renders in `work/rendered-pages/` so later edits do not need the book again.

- Anchor every claim to **book page numbers** (state the offset if PDF page ≠ printed page).
- Keep the book's numbering for sections, definitions, theorems, algorithms, examples, figures and equations, e.g. 定理 3.20, 算法 3.9, (3.84).
- E0 = 教材原文 (what the book prints), E1 = 要点归纳, E2 = 讲解建议 (your explanation or analogy), E3 = 外部补充 with link.
- Recompute every worked example (exact fractions where possible). If the book has a typo, keep the book's text visible and flag it in a 注意 box with the page number; never silently correct.
- Reproduced plots or numbers (e.g. iteration paths, iteration counts) are labelled 本文复现 and state the settings used (line search, stopping rule).
- The slides-mode "reconstruction notice" becomes a short 说明 of scope: book, section, pages, evidence labels, and what was verified.
