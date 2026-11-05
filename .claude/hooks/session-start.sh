#!/bin/bash
# Keep the HyperFrames skills installed and up to date in Claude Code cloud sessions.
set -euo pipefail

# Only run in Claude Code cloud sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Read the hook input to learn why the session started (startup|resume|clear|compact)
input="$(cat 2>/dev/null || true)"
source_kind="$(printf '%s' "$input" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p')"

skills_dir="$HOME/.claude/skills"
skills_present=true
for s in hyperframes hyperframes-cli hyperframes-registry media-use; do
  [ -d "$skills_dir/$s" ] || skills_present=false
done

# Update on every new session start; on resume/clear/compact only reinstall if missing
if [ "$source_kind" != "startup" ] && [ -n "$source_kind" ] && [ "$skills_present" = true ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# Send progress output to stderr so it does not interfere with hook stdout
if ! timeout 300 npx -y hyperframes@latest skills update >&2; then
  echo "session-start: hyperframes skills update failed" >&2
  # Fail only if the skills are not available at all
  [ "$skills_present" = true ] || exit 1
fi
