# Runs inside tools/gen_openapi.py in name order with its globals (rule 25 split). v0.18.179 (owner 2026-11-28: the driver's
# Bokade resor card and Bokningsdetaljer draw the real road route): DriverReservation.routePolyline, the trip's stored Google
# polyline, on every item of GET /driver/reservations (contract.json#reservationRouteLine).
_RRL = C["reservationRouteLine"]
_V179 = "v0.18.179 (contract.json#reservationRouteLine): "
_R179 = S["DriverReservation"]["properties"]
assert "routePolyline" not in _R179, "DriverReservation.routePolyline exists before v0.18.179"
_R179["routePolyline"] = s(_V179 + _RRL["reservation"] + " " + _RRL["calls"] + " " + _RRL["driver"], minLength=1)
