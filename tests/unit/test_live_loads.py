"""Chapter 3 live load rows follow the vehicles ticked in Additional Inputs > Loading."""

import pytest

from osdagbridge.core.reports.live_loads import (
    BRAKING_FRACTION, DEFAULT_BRAKING_ECCENTRICITY_M, footpath_load, vehicle_rows,
)
from osdagbridge.core.utils.common import (
    KEY_BL_IRC_CLASS_SV, KEY_FOOTPATH, KEY_LL_CUSTOM_VEHICLES, KEY_LL_ECCENTRICITY,
    KEY_LL_FOOTPATH_PRESSURE_MODE, KEY_LL_FOOTPATH_PRESSURE_VALUE, KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_CLASS_A, KEY_LL_IRC_CLASS_SV, KEY_SPAN, KEY_TS_FOOTPATH_WIDTH,
)


def test_only_ticked_vehicles_are_listed():
    rows = vehicle_rows({KEY_SPAN: "30", KEY_LL_IRC_CLASS_A: True, KEY_LL_IRC_70R_TRACKED: "No"})
    assert [r.name for r in rows] == ["Class A"]


def test_class_a_row_values():
    (row,) = vehicle_rows({KEY_SPAN: "30", KEY_LL_IRC_CLASS_A: "Yes"})
    assert row.total_load_kN == pytest.approx(543.47, abs=0.01)
    # IRC 6 Cl. 208.2: 9 / (13.5 + L) for a 30 m span; the code helper rounds to 3 places.
    assert row.impact_factor == pytest.approx(1 + 9 / 43.5, abs=5e-4)
    assert row.braking_kN == pytest.approx(BRAKING_FRACTION * row.total_load_kN)
    assert row.braking_eccentricity_m == DEFAULT_BRAKING_ECCENTRICITY_M


def test_class_sv_braking_follows_its_own_tick():
    inputs = {KEY_SPAN: "30", KEY_LL_IRC_CLASS_SV: True, KEY_BL_IRC_CLASS_SV: False}
    (row,) = vehicle_rows(inputs)
    assert row.braking_considered is False and row.braking_kN is None
    assert row.impact_factor is None            # Cl. 208 gives no factor for SV


def test_custom_vehicle_and_eccentricity():
    inputs = {KEY_SPAN: "30", KEY_LL_ECCENTRICITY: "1.5",
              KEY_LL_CUSTOM_VEHICLES: [{"name": "Crane", "axle_loads": [100, 250], "vehicle_type": "Wheeled"}]}
    (row,) = vehicle_rows(inputs)
    assert (row.name, row.total_load_kN, row.braking_eccentricity_m) == ("Crane", 350.0, 1.5)


def test_footpath_load_modes():
    none = footpath_load({KEY_FOOTPATH: "None"})
    assert none.provided == "None" and none.width_m is None
    user = footpath_load({KEY_FOOTPATH: "Single Side", KEY_TS_FOOTPATH_WIDTH: "1.5",
                          KEY_LL_FOOTPATH_PRESSURE_MODE: "User Defined", KEY_LL_FOOTPATH_PRESSURE_VALUE: "5"})
    assert (user.width_m, user.pressure_kN_m2) == (1.5, 5.0)
