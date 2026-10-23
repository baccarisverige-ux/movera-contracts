#!/usr/bin/env sh
# Rewrites CHECKSUMS: sha256 of every contract file, in C-locale order, the
# format the three apps' contract-copy tests read ("<sha256>  <path>").
set -eu
cd "$(dirname "$0")/.."
find CONTRACT.md contract.json openapi.yaml reference_check.py fixtures tools \
  -type f ! -name '*.pyc' ! -path '*/__pycache__/*' \
  | LC_ALL=C sort | xargs sha256sum > CHECKSUMS
echo "CHECKSUMS: $(wc -l < CHECKSUMS) files"
