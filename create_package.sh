#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

OUT="kind2anki.ankiaddon"

rm -f "$OUT"

zip -r "$OUT" manifest.json __init__.py kind2anki -x "**/__pycache__/*"
