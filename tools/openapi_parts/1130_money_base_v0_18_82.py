# Runs inside tools/gen_openapi.py in name order with its globals (rule 25 split). v0.18.82 (S5 J3 money fixes, owner Sitting 3
# 2026-11-12: 106, 107, Q-M7, Q-S5-6, Q-S5-7; contract.json#moneyBase): expectedVersion on the two admin money buttons, one
# commission, KPI money, admin fare = driver side only, Tunisia defaults.
_MB = C["moneyBase"]
_EV = i("v0.18.82 (owner 106): required. ", minimum=1)
for _name, _what in (("WalletCreditCommand", "The Rider.version the admin last saw"), ("DriverPayCommand", "The TripProjection.version the admin last saw")):
    _sc = S[_name]
    assert "expectedVersion" not in _sc["properties"], _name + " has expectedVersion before v0.18.82"
    _sc["properties"] = OrderedDict([("expectedVersion", {**_EV, "description": _EV["description"] + _what + "; stale → 409 version_mismatch with the fresh projection."})] + list(_sc["properties"].items()))
    _sc["required"] = ["expectedVersion"] + list(_sc["required"])
for _p, _proj in (("/admin/riders/{riderId}/wallet-credit", "the fresh admin Rider view"), ("/admin/trips/{tripId}/driver-pay", "the fresh admin TripProjection")):
    _op = PATHS[_p]["post"]
    assert _op["responses"]["409"] == rref("Conflict"), _p + " 409 changed before v0.18.82"
    _op["responses"]["409"] = err("v0.18.82 (owner 106): expectedVersion is stale → version_mismatch with " + _proj + " (nothing written; a second click is refused), "
                                  "or conflict / invalid_transition as before. " + _MB["versionGuard"], "ConflictError")
S["CountryRules"]["properties"]["driverPayChangeMax"]["description"] += " v0.18.82 (owner Q-S5-6): TN 150 DT (150000 TND minor units)."
for _name in ("AdminAdjustCommand", "AdminCompleteCommand"):
    # Q-S5-8 "Admin types driver pay": a NEW field driverPay; the old fare (a rider price in older admins) is refused, never read as pay.
    _pr = S[_name]["properties"]
    assert "driverPay" not in _pr and "fare" in _pr, _name + " changed before v0.18.82"
    _pr["fare"] = {"allOf": [ref("Money")], "deprecated": True, "description": "v0.18.82 (owner Q-M7 / Q-S5-8): refused — 400 invalid_request, reason fare_is_driver_pay; the rider's price cannot be changed. Send driverPay."}
    _pr["driverPay"] = {"allOf": [ref("Money")], "description": "v0.18.82 (owner Q-S5-8 'Admin types driver pay'): driver side only — the driver's new pay for this trip, typed directly (≥ 0); the rider's price never changes. " + _MB["adminFare"]}
S["TripProjection"]["properties"]["commission"] = {"allOf": [ref("Money")], "description": "v0.18.82: " + _MB["commission"]}
