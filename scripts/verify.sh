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
# v0.18.48 §70: owner French wording (fr only).
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
assert c['statusWords']['families']['tripStatus']['no_show']['fr'] == 'Absence du passager', 'no_show fr'
assert c['pickupWaiting']['terms']['texts']['pickupMove']['fr'] == 'Vous pouvez déplacer le lieu de prise en charge de {meters} m au plus après la réservation', 'terms.pickupMove fr'
assert c['arrivedWaiting']['pin']['texts']['driverWrong']['fr'] == 'Code incorrect. Il vous reste {left} tentatives.', 'pin.driverWrong fr'
assert c['statusWords']['families']['tripStatus']['approaching_dropoff']['fr'] == 'Approche de la destination', 'approaching_dropoff fr'
assert c['finish']['driverMoney']['texts']['pickup_pay']['fr'] == 'Rémunération d’approche', 'pickup_pay fr'
assert c['auth']['signedOut']['texts']['expired']['fr'] == c['auth']['signedOut']['texts']['revoked']['fr'] == 'Vous avez été déconnecté de votre compte. Reconnectez-vous.', 'signedOut fr'
def frs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'fr' and isinstance(v, str): yield v
            else: yield from frs(v)
    elif isinstance(o, list):
        for v in o: yield from frs(v)
old = ['Marquer comme client absent ? Vous recevez {amount}', 'Frais de client absent {amount}', 'Trop d’essais. Réessayez dans {min} min', 'Ouvrir les réglages', 'Annuler le client absent', 'Mise en ligne', 'Approche de la dépose', 'Le point de départ a été déplacé', 'Vous avez été déconnecté – reconnectez-vous']
left = [v for v in frs(c) if v in old]
assert not left, f'old French texts still in the contract: {left}'
for _p in (('legal', 'defaults', 'SE', 'terms', 'text'), ('legal', 'defaults', 'FR', 'terms', 'text'), ('pickupWaiting', 'servedConfig', 'cancelAfterArrivedIsNoShow', 'adminText'), ('arrivedWaiting', 'termsTexts', 'lines', 'category'), ('arrivedWaiting', 'termsTexts', 'lines', 'rule')):
    _t = c
    for _k in _p: _t = _t[_k]
    assert 'client absent' not in _t['fr'].lower() and 'absence du passager' in _t['fr'], f'{_p} fr still says client absent'
assert c['arrivedWaiting']['reverseNoShow']['texts']['done']['fr'] == 'Absence du passager annulée', 'reverseNoShow.done fr'
assert 'frais de non-présentation du passager' in c['pickupWaiting']['servedConfig']['cancelAfterArrivedIsNoShow']['adminText']['fr'], 'adminText fee wording'
assert not [x for x in frs(c) if 'frais d’absence' in x], 'owner fee wording is « frais de non-présentation du passager »'
import re
assert not [x for x in frs(c) if re.search('(?i)client absent', x)], 'a contract French text still says « client absent » (owner: « absence du passager »)'
PY
# v0.18.47 §69: admin stream replay limit (no cursor = from now; > replayMax unseen = one resync).
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
a = c['adminLiveEvents']
assert a['replayMax'] == 500, 'adminLiveEvents.replayMax'
assert 'FROM NOW' in a['replay'] and 'replayMax' in a['replay'], 'adminLiveEvents.replay names the no-cursor and replayMax rules'
assert 'replayMax' in a['types']['resync']['when'], 'resync.when names replayMax'
assert a['rule33'], 'adminLiveEvents.rule33'
PY
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
