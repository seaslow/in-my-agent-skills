# in-my-agent-skills

Reusable [Agent Skills](https://agentskills.io) shared across Cursor, Claude, Codex, and other agents that follow the Agent Skills layout.

## Layout

```text
skills/
  <skill-name>/
    SKILL.md          # required; YAML frontmatter name must match folder
    scripts/          # optional helpers
    references/       # optional docs the skill reads
    assets/           # optional templates / static files
```

Each skill is a self-contained folder. Add new skills as siblings under `skills/`.

## Install

**Personal (all projects):**

```bash
git clone https://github.com/seaslow/in-my-agent-skills.git
# Agent Skills discovery path (create if missing):
mkdir -p ~/.agents/skills
cp -R in-my-agent-skills/skills/* ~/.agents/skills/
# or symlink individual skills:
# ln -s "$(pwd)/in-my-agent-skills/skills/notes2deck" ~/.agents/skills/notes2deck
```

**Project-local:**

```bash
mkdir -p .agents/skills
cp -R path/to/in-my-agent-skills/skills/<skill-name> .agents/skills/
```

Exact discovery paths may vary by host (Cursor, Claude Code, Codex, etc.). Prefer the host’s documented skills directory; copying or symlinking the skill folder is enough.

## Skills in this repo

| Skill | Description |
|-------|-------------|
| [`notes2deck`](skills/notes2deck/) | Turn study material (a textbook chapter or section, PPTX/PDF slides, or lecture PDFs) into a polished, figure-rich, evidence-labelled course handout PDF; and, only when the user explicitly asks for a PPT/deck, also a presentation .pptx built from that handout. |
| [`bilibili-render-pdf`](skills/bilibili-render-pdf/) | Generate a professional, detailed, figure-rich LaTeX course note and final PDF from a Bilibili lecture, tutorial, or technical talk. |

## License

MIT — see [LICENSE](LICENSE).
