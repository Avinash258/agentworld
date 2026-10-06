#!/usr/bin/env bash
# Publish this project to GitHub as Avinash258/agentworld (public) + Release with SKILL.md
set -euo pipefail

OWNER="${GITHUB_OWNER:-Avinash258}"
REPO_NAME="${GITHUB_REPO:-agentworld}"
TAG="${RELEASE_TAG:-v0.1.0}"
TITLE="${RELEASE_TITLE:-AgentWorld Skill v0.1.0}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI first: https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  if [[ -n "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ]]; then
    export GH_TOKEN="${GH_TOKEN:-$GITHUB_TOKEN}"
  else
    echo "Not logged into GitHub. Run: gh auth login" >&2
    echo "Or export GH_TOKEN=<classic/fine-grained PAT with repo scope>" >&2
    exit 1
  fi
fi

# Build downloadable skill artifacts
mkdir -p dist/release
cp -f skills/local-agentic-ai-platform/SKILL.md dist/SKILL.md
cp -f skills/local-agentic-ai-platform/SKILL.md dist/release/SKILL.md
rm -rf dist/release/references
cp -R skills/local-agentic-ai-platform/references dist/release/references
rm -f dist/agentworld-skill.zip
(cd dist/release && zip -r ../agentworld-skill.zip SKILL.md references >/dev/null)

FULL="$OWNER/$REPO_NAME"

if gh repo view "$FULL" >/dev/null 2>&1; then
  echo "Repo $FULL already exists"
else
  echo "Creating public repo $FULL"
  gh repo create "$FULL" --public --description "AgentWorld — Local Agentic AI Platform + portable Agent Skill (SKILL.md)" --source=. --remote=github --push
fi

# Ensure remote and push
if git remote get-url github >/dev/null 2>&1; then
  git remote set-url github "https://github.com/$FULL.git"
else
  git remote add github "https://github.com/$FULL.git"
fi

git push -u github HEAD:main

NOTES="$(cat <<EOF
## AgentWorld ${TAG}

Portable Agent Skill for the Local Agentic AI Platform.

### Download the skill

| Asset | Use |
| --- | --- |
| **SKILL.md** | Single-file skill — drop into \`.cursor/skills/local-agentic-ai-platform/\` |
| **agentworld-skill.zip** | Full package including \`references/\` |

### Install (Cursor)

\`\`\`bash
mkdir -p ~/.cursor/skills/local-agentic-ai-platform
# after downloading SKILL.md from this release:
mv ~/Downloads/SKILL.md ~/.cursor/skills/local-agentic-ai-platform/
\`\`\`

Or unzip \`agentworld-skill.zip\` into \`~/.cursor/skills/local-agentic-ai-platform/\`.

Repo: https://github.com/${FULL}
EOF
)"

if gh release view "$TAG" --repo "$FULL" >/dev/null 2>&1; then
  echo "Updating release $TAG"
  gh release upload "$TAG" dist/SKILL.md dist/agentworld-skill.zip --repo "$FULL" --clobber
else
  echo "Creating release $TAG"
  gh release create "$TAG" dist/SKILL.md dist/agentworld-skill.zip \
    --repo "$FULL" \
    --title "$TITLE" \
    --notes "$NOTES" \
    --latest
fi

echo
echo "Public repo:  https://github.com/$FULL"
echo "Releases:     https://github.com/$FULL/releases/tag/$TAG"
echo "SKILL.md:     https://github.com/$FULL/releases/download/$TAG/SKILL.md"
