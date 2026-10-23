#!/usr/bin/env sh
# Copies this contract into an app repository: scripts/sync.sh <app-dir>
# Only the files CHECKSUMS lists, plus CHECKSUMS itself, land in
# <app-dir>/contracts; anything else there is removed, so the app's
# contract-copy test sees exactly the canonical set.
set -eu
[ $# -eq 1 ] || { echo "usage: scripts/sync.sh <app-dir>"; exit 2; }
src="$(cd "$(dirname "$0")/.." && pwd)"
dst="$1/contracts"
rm -rf "$dst"
mkdir -p "$dst"
awk '{print $2}' "$src/CHECKSUMS" | while read -r f; do
  mkdir -p "$dst/$(dirname "$f")"
  cp "$src/$f" "$dst/$f"
done
cp "$src/CHECKSUMS" "$dst/CHECKSUMS"
(cd "$dst" && sha256sum -c --quiet CHECKSUMS)
echo "synced $(wc -l < "$src/CHECKSUMS") files into $dst (contract $(python3 -c "import json;print(json.load(open('$src/contract.json'))['version'])"))"
