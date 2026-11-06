#!/usr/bin/env sh
# The contract's own checks: files match CHECKSUMS, the reference engine
# agrees with the fixtures, openapi.yaml parses, and (on a tag) the tag is
# the contract's version.
set -eu
cd "$(dirname "$0")/.."
sha256sum -c --quiet CHECKSUMS
listed=$(awk '{print $2}' CHECKSUMS | LC_ALL=C sort)
present=$(find CONTRACT.md contract.json openapi.yaml reference_check.py fixtures tools -type f ! -path '*/__pycache__/*' | LC_ALL=C sort)
[ "$listed" = "$present" ] || { echo "CHECKSUMS lists different files than the tree"; exit 1; }
python3 reference_check.py
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['openapi'].startswith('3.'), 'openapi.yaml is not OpenAPI 3'
# v0.9.0: no operation lists the same parameter twice (name + in).
params = spec['components']['parameters']
for path, item in spec['paths'].items():
    for method, op in item.items():
        seen = set()
        for p in op.get('parameters', []):
            p = params[p['$ref'].split('/')[-1]] if '$ref' in p else p
            key = (p['name'], p['in'])
            assert key not in seen, f'{method} {path} lists {key} twice'
            seen.add(key)
print(f"contract.json version {c['version']}, openapi {spec['info'].get('version')}, {len(spec['paths'])} paths")
PY
# openapi.yaml must be exactly what the generator makes (no hand edits).
tmp=$(mktemp)
python3 tools/gen_openapi.py . "$tmp" >/dev/null
cmp -s "$tmp" openapi.yaml || { rm -f "$tmp"; echo "openapi.yaml is not what tools/gen_openapi.py generates; run it and commit the result"; exit 1; }
rm -f "$tmp"
# v0.18.45 §68: the driver config stream lists driver_reservations_changed; §67 note says "renumbered from 0.18.42".
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
assert c['driverReservationsLive']['kind'] == 'driver_reservations_changed', 'driverReservationsLive.kind'
assert c['driverReservationsLive']['stream'] == 'GET /driver/config/stream', 'driverReservationsLive.stream'
assert 'driver_reservations_changed' in spec['paths']['/driver/config/stream']['get'].get('description', ''), 'driver stream kinds miss driver_reservations_changed'
assert spec['components']['schemas']['DriverReservationsChangedEvent']['properties']['kind']['const'] == 'driver_reservations_changed'
assert 'renumbered from 0.18.42' in c['sameAddress']['note'] and 'renumbered from 0.18.44' not in c['sameAddress']['note'], 'sameAddress.note typo (C10)'
PY
# CONTRACT.md's title names the same version as contract.json.
v=$(python3 -c "import json;print(json.load(open('contract.json'))['version'])")
head -1 CONTRACT.md | grep -q "v$v\b" || { echo "CONTRACT.md title does not name v$v"; exit 1; }
tag="${GITHUB_REF_NAME:-}"
case "$tag" in
  v*) v=$(python3 -c "import json;print(json.load(open('contract.json'))['version'])")
      [ "$tag" = "v$v" ] || { echo "tag $tag does not match contract.json version $v"; exit 1; } ;;
esac
echo "contract ok"
