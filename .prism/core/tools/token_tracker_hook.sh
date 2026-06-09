#!/bin/bash
# Auto-called by Claude Code Stop hook.
# Silently syncs token usage after each Claude Code session ends.
# Installed by: python .prism/core/tools/token_tracker.py install-hook

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

python3 "$SCRIPT_DIR/token_tracker.py" sync \
  --project-root "$PROJECT_ROOT" \
  --quiet 2>/dev/null

exit 0
