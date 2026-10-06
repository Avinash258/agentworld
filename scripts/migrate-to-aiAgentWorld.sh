#!/usr/bin/env bash
# Run in WSL — writes directly to your Windows folder
set -euo pipefail
DEST="/mnt/c/Project/aiAgentWorld"
mkdir -p /mnt/c/Project
if [[ -d "$DEST/.git" ]]; then
  cd "$DEST" && git pull || true
else
  rm -rf "$DEST"
  # Install origin if needed
  if ! command -v origin >/dev/null 2>&1; then
    curl -fsSL https://downloads.cursor.com/origin/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  fi
  origin auth login
  origin repo clone avinash-sharma-dev/locus-ai "$DEST"
fi
echo "Project ready at C:\\Project\\aiAgentWorld ($DEST)"
