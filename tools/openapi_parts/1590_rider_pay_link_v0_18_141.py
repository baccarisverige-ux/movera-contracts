# Runs inside tools/gen_openapi.py in name order with its globals (rule 25 split). v0.18.141 (DRAFT; owner 2026-11-20
# "add a payment link when the rider wants to cancel, but she has to pay a cancellation fee"): the rider's fee payment
# link (contract.json#riderPayLink). Setting on the country standard (off), the rider's read route; confirmation stays
# the admin's Mark as paid on the owed fee.
_RPL = C["riderPayLink"]
_V141 = "v0.18.141 (riderPayLink): "
_cr141 = S["CountryRules"]["properties"]
assert "riderPayLink" not in _cr141, "CountryRules.riderPayLink exists before v0.18.141"
S["RiderPayLinkSetting"] = obj({
    "enabled": dflt(b("Off by default in every country: no Pay now button until the admin switches it on."), False),
    "payLink": dflt(s("The payment link the rider's Pay now button opens (https, printable ASCII, no backslash, no user:password@; '' = none). Required when enabled.", maxLength=500, pattern="^(https://[\\x21-\\x5B\\x5D-\\x7E]+)?$"), "")},
    ["enabled"], _V141 + _RPL["setting"], addl=False)
_cr141["riderPayLink"] = ref("RiderPayLinkSetting")
S["RiderPayMovera"] = obj({
    "owed": {"allOf": [ref("Money")], "description": "Her debt now in that currency (debtModel.riderWallet); 0 when nothing."},
    "reference": s("'<riderId>-<tripId>' while owed is above 0, else '<riderId>': the text she writes on the payment.", maxLength=80),
    "tripId": s("The trip of her oldest owed fee in that currency; only while owed is above 0."),
    "payLink": s("Only while owed is above 0 and her country's riderPayLink is on: opened as it is (no amount added).", maxLength=500)},
    ["owed", "reference"], _V141 + _RPL["read"], addl=False)
op("get", "/rider/pay-movera", "getRiderPayMovera", "What the rider owes Movera and where to pay (fee payment link)", ["rider"], "Rider · Payments",
   params=[pref("WalletCurrency")], ok=(200, "RiderPayMovera"), read_only=True, desc=_V141 + _RPL["read"] + " " + _RPL["cancel"] + " " + _RPL["debtLine"] + " " + _RPL["confirm"])
PATHS["/admin/riders/{riderId}/fees/{tripId}/mark-paid"]["post"]["description"] += " " + _V141 + _RPL["confirm"]
PATHS["/admin/config/{doc}"]["put"]["description"] += " " + _V141 + _RPL["setting"]
PATHS["/admin/config/{doc}/restore"]["post"]["description"] += " " + _V141 + "Restore keeps riderPayLink (pricingHistory.restoreKeeps)."
_rk141 = S["ConfigDraftUpdate"]["properties"]["removeKeys"]
assert "riderPayLink" in C["configDocs"]["keptKeys"]["country_rules"], "riderPayLink is a kept key"
_rk141["items"]["enum"] = sorted(set(_rk141["items"]["enum"]) | {"riderPayLink"})
_rk141["maxItems"] = len(_rk141["items"]["enum"])
