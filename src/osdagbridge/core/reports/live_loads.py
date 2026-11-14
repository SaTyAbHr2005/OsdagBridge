"""
Live load data for Chapter 3: one row per vehicle ticked in
Additional Inputs > Loading, and the footpath load.

Values follow IRC 6:2017. The chapter only formats what is returned here.
"""

from dataclasses import dataclass
from typing import Optional

from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
from osdagbridge.core.utils.common import (
    KEY_BL_IRC_CLASS_SV,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_ECCENTRICITY,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_SPAN,
    KEY_TS_FOOTPATH_WIDTH,
)

_G = 9.81  # kN per tonne

# IRC 6:2017 Cl. 211.2 (a): braking force from the first train of vehicles
# in a lane is 20 % of its load.
BRAKING_FRACTION = 0.20
DEFAULT_BRAKING_ECCENTRICITY_M = 1.2   # Cl. 211.3: 1.2 m above the roadway


def _wheel_total_kN(vehicle: dict) -> float:
    return sum(vehicle["wheel_loads"]) / 1000.0   # helpers return N


def _tracked_70r_kN() -> float:
    track = IRC6_2017.cl_204_1_Class70R_vehicle_track()
    length = max(track["x"]) - min(track["x"])
    return track["wheel_loads_udl"] * length * len(track["z"]) / 1000.0


# (label, input key, total load in kN, impact clause). Totals are callables
# so only the ticked vehicles' helpers run.
# Class AA, the 70R bogie and the fatigue vehicle use their nominal IRC 6:2017
# loads (Cl. 204.1: AA tracked 70 t, AA wheeled 40 t, 70R bogie 40 t;
# Cl. 204.6: fatigue truck 40 t).
_IRC_VEHICLES = [
    ("Class A", KEY_LL_IRC_CLASS_A, lambda: _wheel_total_kN(IRC6_2017.cl_204_1_ClassA_vehicle()), "A"),
    ("Class 70R (Wheeled)", KEY_LL_IRC_70R_WHEELED,
     lambda: _wheel_total_kN(IRC6_2017.cl_204_1_Class70R_vehicle_wheel()), "wheeled"),
    ("Class 70R (Tracked)", KEY_LL_IRC_70R_TRACKED, _tracked_70r_kN, "tracked"),
    ("Class 70R (Bogie)", KEY_LL_IRC_70R_BOGIE, lambda: 40 * _G, "wheeled"),
    ("Class AA (Wheeled)", KEY_LL_IRC_AA_WHEELED, lambda: 40 * _G, "wheeled"),
    ("Class AA (Tracked)", KEY_LL_IRC_AA_TRACKED, lambda: 70 * _G, "tracked"),
    ("Class SV", KEY_LL_IRC_CLASS_SV, lambda: IRC6_2017.cl_204_5_1_special_vehicle()["total_load_kN"], None),
    ("Class Fatigue", KEY_LL_IRC_CLASS_FATIGUE, lambda: 40 * _G, None),
]


@dataclass(frozen=True)
class VehicleRow:
    name: str
    total_load_kN: Optional[float]
    impact_factor: Optional[float]     # 1 + IM; None where Cl. 208 gives none
    braking_considered: bool
    braking_kN: Optional[float]
    braking_eccentricity_m: Optional[float]
    centrifugal_kN: float = 0.0        # straight deck, see chapter note


@dataclass(frozen=True)
class FootpathLoad:
    provided: str                      # "None", "Single Side" or "Both Sides"
    width_m: Optional[float]
    mode: str
    pressure_kN_m2: Optional[float]


def _is_ticked(value) -> bool:
    return value is True or str(value).strip().lower() in ("true", "yes", "1", "checked")


def _float(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _impact_factor(kind: Optional[str], span_m: Optional[float]) -> Optional[float]:
    if kind is None or span_m is None:
        return None
    if kind == "A":
        return 1.0 + IRC6_2017.cl_208_2_impact_factor(span_m)
    return 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m, tracked=(kind == "tracked"))


def vehicle_rows(input_dict: dict) -> list[VehicleRow]:
    """One row per vehicle selected in the Loading tab, custom vehicles last."""
    span_m = _float(input_dict.get(KEY_SPAN))
    eccentricity = _float(input_dict.get(KEY_LL_ECCENTRICITY))
    if eccentricity is None:
        eccentricity = DEFAULT_BRAKING_ECCENTRICITY_M

    def row(name, total, kind, braking):
        return VehicleRow(
            name=name,
            total_load_kN=total,
            impact_factor=_impact_factor(kind, span_m),
            braking_considered=braking,
            braking_kN=BRAKING_FRACTION * total if braking and total is not None else None,
            braking_eccentricity_m=eccentricity if braking else None,
        )

    rows = []
    for name, key, total, kind in _IRC_VEHICLES:
        if not _is_ticked(input_dict.get(key)):
            continue
        # Class SV braking is a separate opt-in; every other selected
        # vehicle contributes braking (matches the Loading tab).
        braking = _is_ticked(input_dict.get(KEY_BL_IRC_CLASS_SV)) if key == KEY_LL_IRC_CLASS_SV else True
        rows.append(row(name, total(), kind, braking))

    for vehicle in input_dict.get(KEY_LL_CUSTOM_VEHICLES) or []:
        if isinstance(vehicle, dict):
            loads = [_float(a) for a in vehicle.get("axle_loads") or []]
            total = sum(loads) if loads and None not in loads else None
            # Tracked custom vehicles follow Cl. 208.3; wheeled and bogie
            # ones the Class A curve of Cl. 208.2.
            kind = "tracked" if str(vehicle.get("vehicle_type", "")).lower() == "tracked" else "A"
            rows.append(row(str(vehicle.get("name") or "Custom vehicle"), total, kind, True))
        elif vehicle:
            rows.append(row(str(vehicle), None, "A", True))
    return rows


def analysis_impact_factor(input_dict: dict) -> Optional[float]:
    """Dynamic load allowance the grillage analysis applies to every vehicle case."""
    span_m = _float(input_dict.get(KEY_SPAN))
    return None if span_m is None else 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)


def footpath_load(input_dict: dict) -> FootpathLoad:
    provided = str(input_dict.get(KEY_FOOTPATH) or "None")
    mode = str(input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE) or "As per IRC 6")
    if mode.strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        pressure = IRC6_2017.cl_206_1_footway_load()
    else:
        pressure = _float(input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE))
    width = _float(input_dict.get(KEY_TS_FOOTPATH_WIDTH)) if provided != "None" else None
    return FootpathLoad(provided=provided, width_m=width, mode=mode, pressure_kN_m2=pressure)
