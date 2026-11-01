# Presentation Deck

Build only when the user explicitly asks for a PPT / deck / slides. The handout is for the user's own study; the deck is for standing up and presenting. Distill the handout; do not copy its teaching voice.

## Content rules

- **Structure follows the source.** Slide titles are the source's own section names and numbers (e.g. `3.4.1 拟 Newton 方程`, `例 3.9`, `定理 3.25–3.27`). Typical arc: cover, 引言, one or more slides per section in book order, worked examples where the book has them, 小结, 参考文献.
- **No meta pages:** no 汇报总览 / outline, 动机 page framed as "why you should care", time plan, likely questions / Q&A, errata page.
- **No presenter voice on slides:** no "讲什么 / 怎么讲 / 怎么做" titles, no tips for the presenter, no questions or rhetorical questions (scan for `？` and `?`). State results declaratively.
- **No evidence labels on slides** (no E0/E1/E2). Cite book pages lightly in box titles, e.g. `定理 3.20（Sherman–Morrison 公式，p.96）`.
- **Concise:** keywords, formulas, figures, short lines. Remove filler and repetition. Worked examples keep the essential numbers per step; full arithmetic lives in the handout.
- **Typos** from the handout go in a small footnote line on the relevant slide (`注：教材 p.101 “…” 应为 …`).
- **No obvious context labels:** no course name, textbook title or author, degree year, "课堂报告" style subtitles. The cover is the topic plus a short subtitle.
- **Reuse the handout's figures** (reproductions, cropped book figures). If a cropped book image is cut off or wrong, typeset the content instead.
- E2 explanations, analogies and the spoken walk-through go into **speaker notes**, in plain sentences.

## Timing

- Ask for or use the user's target duration. Each slide's notes start with `（约 N 分钟）`; the total must land inside the target.
- Report the per-slide minutes and total to the user.

## Visual style (copy the handout)

- White background. Ink `25313D`, muted `66727E`, title rule `B8C0C8`. No decorative shapes, icons, device mockups, or template art.
- Header: short section tag (e.g. `§3.4 拟 Newton 法`) muted 12 pt top-left with a thin rule; page number centered at the bottom.
- Title: bold ~28 pt ink with a thin rule beneath.
- Body: normal text, display formulas, figures, and **three-line (booktabs) tables**: thick top and bottom rules, thin mid rule, no cell borders.
- **Colored boxes are small and rare:** only for a theorem statement, a conclusion, or a short summary, the way the handout uses them. A box never fills most of the slide; main content is plain body text.
- Box palette (background / frame): 结论 or 算例 `FFF8EC/C26B1A`; 注 or 要点 `EEF3F8/527A9E`; 定理 `EDF5F1/6B9B82`; 注意 `FAEEEE/A65B5B`. Title bar in the frame color with white bold text. Avoid saturated green/emerald themes.
- 16:9 (13.333 × 7.5 in).

## Fonts

- Latin text and numbers: **Times New Roman**. Chinese: **等线**. Set on every run (`latin`, `cs` = Times New Roman, `ea` = 等线) and in the theme major/minor fonts; remove supplemental per-script theme fonts and stray faces (Arial, Calibri, 等线 Light, 游ゴシック, Noto, …); fix `docProps/app.xml` font list.
- Run `python scripts/pptx_fonts.py DECK.pptx` after every build, then `python scripts/pptx_check.py DECK.pptx`.
- The box may lack these fonts and render with substitutes (Tinos, Noto Sans CJK); that is a rendering artefact, the file still names the right fonts. Say so if the user asks.

## File integrity

- Every notes master must have its own theme relationship, otherwise PowerPoint asks to repair the file. `pptx_check.py` checks this; `pptx_fonts.py --fix-notes-theme` adds a copy of the slide theme.
- Validate the package (open with python-pptx; LibreOffice render of every slide) and inspect each render for overflow, overlaps, wrapped table cells pushing rules, clipped formulas.

## Edits after delivery

- Work on the user's current file (e.g. a PowerPoint-repaired copy), in a new working folder; keep the previous version until the user confirms.
- When inserting or deleting slides, renumber page numbers and update timing notes.
- Deliver to the user's computer under a clear filename; do not leave stray copies.

## Checklist before delivery

1. Titles = source section names; no meta pages; no `？`/`?` on slides; no presenter tips; no E-labels; no banned context labels.
2. Boxes small and only for conclusions/theorems/summaries.
3. Fonts script + check pass (only Times New Roman and 等线).
4. Notes on every slide with `（约 N 分钟）`; total within target.
5. Notes masters have a theme; file opens without repair.
6. Every slide rendered and inspected.
