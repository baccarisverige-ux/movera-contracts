# Runs inside tools/gen_openapi.py in name order with its globals (rule 25 split). v0.18.163 (live traffic for trip
# times; owner 2026-11-25 "Google trafic réel"): Quote.tripSeconds / tripMeters / routeSource and
# DispatchDocument.liveTraffic { on } (contract.json#liveTraffic).
_LT = C["liveTraffic"]
_V163 = "v0.18.163 (contract.json#liveTraffic): "
_Q = S["Quote"]["properties"]
for _k in ("tripSeconds", "tripMeters", "routeSource"):
    assert _k not in _Q, "Quote." + _k + " exists before v0.18.163"
_Q["tripSeconds"] = i(_V163 + "the drive time this price used, in seconds (live traffic when routeSource is google). " + _LT["rider"] + " Absent from an older server.", minimum=0)
_Q["tripMeters"] = i(_V163 + "the road distance this price used, in metres. Absent from an older server.", minimum=0)
_Q["routeSource"] = s(_V163 + _LT["routeSourceRule"] + " Absent from an older server.", enum=list(_LT["routeSources"]))
_D = S["DispatchDocument"]["properties"]
assert "liveTraffic" not in _D, "DispatchDocument.liveTraffic exists before v0.18.163"
_D["liveTraffic"] = obj({"on": b(_V163 + "true: trip times with live traffic (Google), else roads without traffic (OSRM).")}, ["on"],
                        _V163 + _LT["setting"] + " " + _LT["fallback"], addl=False)
