# Evidence Protocol

Use this protocol to prevent a fluent reconstruction from being mistaken for recovered fact.

## Evidence Levels

| Level | Meaning | Allowed wording |
|---|---|---|
| `E0 Direct` | Explicitly visible or structurally present in the source: slide text, labels, values, notes, link targets, media metadata, or an unambiguous visual relation. | "Slide 8 states..." / "The chart reports..." |
| `E1 Relational` | Strong inference supported by multiple source elements, adjacent pages, repetition, ordering, or a clear question-answer relationship. | "Taken together, slides 8-10 argue..." |
| `E2 Reconstructed` | A plausible explanation, example, transition, emphasis, or spoken elaboration that makes the deck coherent but is not recoverable as fact. | "The speaker may have explained this as..." |
| `E3 External` | Background from a linked page, cited paper, documentation, or general domain knowledge. | "External context helps explain..." |

`E3` never proves speaker intent by itself. A source linked by the author still remains external unless the slide explicitly adopts its claim, figure, quotation, or conclusion.

## Confidence

Assign `high`, `medium`, or `low` confidence independently of evidence level.

- `high`: only one reasonable reading fits clear evidence.
- `medium`: the reading is well supported, but some connective content is missing.
- `low`: multiple interpretations remain or a critical element is unreadable.

Do not convert confidence into fake numerical precision.

## Ledger Schema

Keep one row per substantive claim:

```markdown
| ID | Claim | Level | Confidence | Source anchors | Counterevidence or alternative | Report location |
|---|---|---|---|---|---|---|
| C-01 | ... | E1 | high | Deck A, slides 4-6 | None found | Section 2.1 |
```

Source anchors must identify the deck and original slide/page number. Use a stable local figure filename when the claim depends on a crop.

## Page Dossier

Maintain compact coverage for every slide:

```markdown
### Deck A, slide 12 - title
- Role: evidence / transition / definition / mechanism / example / result / conclusion / other
- E0 inventory: ...
- Likely point (E1): ...
- Possible spoken elaboration (E2): ...
- Connection: slide 11 -> slide 12 -> slide 13
- Uncertainty: ...
- Coverage: main text section or appendix location
```

## Attribution Rules

- Use "the slide states" for `E0` text, not "the speaker believes".
- Use "the deck appears to argue" for `E1`.
- Use conditional language for `E2`.
- Name and link external sources for `E3`.
- If original speaker notes exist, treat them as `E0`, but distinguish notes from visible slide content.
- Never invent an exact quotation, anecdote, emotional state, audience reaction, gesture, or timing.
- A likely gesture may be described only as a presentation affordance, such as "the presenter could point to the curve's inflection," and remains `E2`.

## Conflict Resolution

When sources disagree, preserve the conflict instead of silently harmonizing it.

1. Rendered slide appearance governs what the audience could see.
2. Structured PPTX data helps interpret objects but does not override visible output without a note.
3. Existing speaker notes govern intended narration only for that slide; they do not automatically fix contradictions elsewhere.
4. A PDF exported by the author can be used to audit PPTX rendering differences.
5. External references explain context but cannot erase internal inconsistency.
