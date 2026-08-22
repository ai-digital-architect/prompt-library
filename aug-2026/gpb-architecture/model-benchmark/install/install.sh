#!/usr/bin/env bash
# Install the model-benchmark skill into a repository's harness directories.
#
#   ./install/install.sh [--claude] [--copilot] [--copy] [target-repo]
#
# Symlinks by default so edits take effect immediately; --copy pins a version.
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${*: -1}"
[[ "$TARGET" == --* || -z "$TARGET" ]] && TARGET="$(pwd)"

DO_CLAUDE=0; DO_COPILOT=0; MODE="symlink"
for arg in "$@"; do
  case "$arg" in
    --claude)  DO_CLAUDE=1 ;;
    --copilot) DO_COPILOT=1 ;;
    --copy)    MODE="copy" ;;
  esac
done
if [[ $DO_CLAUDE -eq 0 && $DO_COPILOT -eq 0 ]]; then DO_CLAUDE=1; DO_COPILOT=1; fi

install_to() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  if [[ -e "$dest" || -L "$dest" ]]; then
    echo "  exists, skipping: $dest"
    return
  fi
  if [[ "$MODE" == "copy" ]]; then
    cp -R "$SKILL_ROOT" "$dest"; echo "  copied  -> $dest"
  else
    ln -s "$SKILL_ROOT" "$dest"; echo "  linked  -> $dest"
  fi
}

echo "model-benchmark installer"
echo "  source: $SKILL_ROOT"
echo "  target: $TARGET"
[[ $DO_CLAUDE  -eq 1 ]] && install_to "$TARGET/.claude/skills/model-benchmark"
[[ $DO_COPILOT -eq 1 ]] && install_to "$TARGET/.github/skills/model-benchmark"

echo
echo "Verifying…"
python3 "$SKILL_ROOT/scripts/mb.py" doctor || {
  echo "doctor reported problems — see above"; exit 1; }
echo
echo "Next: python3 $SKILL_ROOT/scripts/mb.py test"
