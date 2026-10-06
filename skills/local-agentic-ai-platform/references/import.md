# Import this skill into Cursor, VS Code, Claude, Codex, and others

This folder is a portable [Agent Skills](https://agentskills.io) package:

```text
local-agentic-ai-platform/
├── SKILL.md
└── references/
    ├── import.md
    ├── team-packs.md
    └── api.md
```

`name` in frontmatter must match the folder name: `local-agentic-ai-platform`.

## Cursor (project)

Already wired in this repo at:

- `.cursor/skills/local-agentic-ai-platform/`
- `.agents/skills/local-agentic-ai-platform/`

Open the project in Cursor → Agent chat → type `/` → search **local-agentic-ai-platform**.

Or ask naturally; Agent may auto-attach when the description matches.

## Cursor (personal / global)

Copy the folder:

```bash
cp -R skills/local-agentic-ai-platform ~/.cursor/skills/
```

Optional: Settings → Agents → enable **Sync Skills for Cloud Agents** so Cloud Agents see `~/.cursor/skills/`.

## Cursor (team marketplace / GitHub import)

This repo includes a minimal marketplace entry under `.cursor-plugin/`. In Cursor:

1. Customize → import marketplace **From GitHub Repository** (after you publish/create the GitHub repo)
2. Or copy `plugins/laap-skills/` into your team marketplace repo

## Claude Code

```bash
cp -R skills/local-agentic-ai-platform .claude/skills/
# or globally:
cp -R skills/local-agentic-ai-platform ~/.claude/skills/
```

## OpenAI Codex

```bash
cp -R skills/local-agentic-ai-platform .codex/skills/
# or:
cp -R skills/local-agentic-ai-platform ~/.codex/skills/
```

## VS Code + GitHub Copilot

Copilot does not load Agent Skills natively the same way. Practical options:

1. **Cursor** — preferred for this skill format
2. **Copilot custom instructions** — paste a short summary from `SKILL.md` into `.github/copilot-instructions.md`
3. **Continue / Cline / Aider / other agents** that support Agent Skills — point them at `skills/local-agentic-ai-platform/`

A ready-to-paste Copilot stub lives at [copilot-instructions.snippet.md](copilot-instructions.snippet.md).

## Any Agent Skills–compatible tool

Copy or submodule:

```bash
git submodule add <this-repo-url> third_party/laap
# then link:
ln -s "$(pwd)/third_party/laap/skills/local-agentic-ai-platform" \
  .agents/skills/local-agentic-ai-platform
```

## Verify

In Cursor Agent chat:

```text
What skills are available?
```

You should see `local-agentic-ai-platform`. Then:

```text
/local-agentic-ai-platform
Add a Team Pack for Security vulnerability triage
```
