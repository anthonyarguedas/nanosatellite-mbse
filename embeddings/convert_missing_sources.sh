#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_SCRIPT="$HOME/agent-tools/processing/skills/pdf-to-markdown/scripts/pdf_to_markdown.py"
OUTPUT_DIR="$SCRIPT_DIR/data/generated-sources"
FORCE="${1:-}"

mkdir -p "$OUTPUT_DIR" "$SCRIPT_DIR/logs"
case "$(cd "$OUTPUT_DIR" && pwd)" in
  "$SCRIPT_DIR"/*) ;;
  *) echo "Refusing unexpected output directory: $OUTPUT_DIR" >&2; exit 1 ;;
esac

convert_3814() {
  UV_CACHE_DIR="$SCRIPT_DIR/.cache/uv" uv run "$SKILL_SCRIPT" \
    --input "$REPO_ROOT/SLR/SLR1/pdfs/citation-chasing-candidates/citation-candidate-3814.pdf" \
    --output-path "$OUTPUT_DIR/citation-candidate-3814.md" \
    --verbose 2>&1 | tee "$SCRIPT_DIR/logs/pdf-conversion-3814.log"
}

if [[ "$FORCE" == "--force" || ! -f "$OUTPUT_DIR/citation-candidate-3814.md" ]]; then
  convert_3814
else
  echo "Keeping existing $OUTPUT_DIR/citation-candidate-3814.md"
fi

if [[ ! -f "$OUTPUT_DIR/citation-candidate-4690.md" ]]; then
  echo "Missing retained source: $OUTPUT_DIR/citation-candidate-4690.md" >&2
  exit 1
fi
echo "Keeping existing $OUTPUT_DIR/citation-candidate-4690.md"
