# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_DENSITY,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from .live_loads import analysis_impact_factor, footpath_load, vehicle_rows
from .styles import TABLE
from .tables import longtable_begin


def _num(value, digits):
    return "---" if value is None else f"{value:.{digits}f}"


def _wearing_course_load(input_dict) -> str:
    """Material, thickness and density of the wearing course and the surface load they give."""
    material = _tex(input_dict.get(KEY_WC_MATERIAL) or "---")
    try:
        thickness_mm = float(input_dict.get(KEY_WC_THICKNESS))
        density = float(input_dict.get(KEY_WC_DENSITY))
    except (TypeError, ValueError):
        return material
    return (f"{material}, {thickness_mm:g} mm thick at {density:g} kN/m\\textsuperscript{{3}} "
            f"= {thickness_mm / 1000.0 * density:.2f} kN/m\\textsuperscript{{2}}")


def _vehicle_live_load_table(input_dict) -> str:
    """Vehicles ticked in Additional Inputs > Loading, one row each."""
    rows = vehicle_rows(input_dict)
    body = [
        _tex(v.name)
        + " & " + _num(v.total_load_kN, 1)
        + " & " + _num(v.impact_factor, 3)
        + " & " + ("Yes" if v.braking_considered else "No")
        + " & " + _num(v.braking_kN, 1)
        + " & " + _num(v.braking_eccentricity_m, 2)
        + " & " + _num(v.centrifugal_kN, 1)
        + r" \\[\rowpad]" + "\n\\hline"
        for v in rows
    ] or [r"\multicolumn{7}{|l|}{No vehicle is selected in Additional Inputs $>$ Loading.} \\[\rowpad]" + "\n\\hline"]

    dla = analysis_impact_factor(input_dict)
    dla_note = (f" The grillage analysis currently applies the Cl. 208.3 tracked-vehicle factor, "
                f"{dla:.3f}, to every vehicle load case." if dla is not None else "")
    # The two header rows share the Vehicle, load, impact and centrifugal
    # cells; only the braking group is split, so the hhline rule is drawn
    # under columns 4-6 and in the header colour elsewhere.
    header = r"""\tableheader & & & \multicolumn{3}{c|}{\textbf{Braking Load (IRC 6 Cl. 211)}} & \\
\hhline{|>{\arrayrulecolor{tableHeader}}->{\arrayrulecolor{black}}|>{\arrayrulecolor{tableHeader}}->{\arrayrulecolor{black}}|>{\arrayrulecolor{tableHeader}}->{\arrayrulecolor{black}}|-|-|-|>{\arrayrulecolor{tableHeader}}->{\arrayrulecolor{black}}|}
\tableheader \multirow{-2}{*}{\textbf{Vehicle}}
& \multirow{-2}{*}{\makecell{\textbf{Total Load}\\\textbf{(kN)}}}
& \multirow{-2}{*}{\makecell{\textbf{Impact}\\\textbf{Factor}}}
& \textbf{Considered?}
& \makecell{\textbf{Value}\\\textbf{(kN)}}
& \makecell{\textbf{Eccentricity}\\\textbf{(m)}}
& \multirow{-2}{*}{\makecell{\textbf{Centrifugal}\\\textbf{Force (kN)}}} \\"""
    return (
        "\\begingroup\n\\tablesmallfont\n\\setlength{\\tabcolsep}{\\colsepdense}\n"
        + longtable_begin("|L{2.6cm}|C{2.1cm}|C{1.5cm}|C{2.15cm}|C{1.5cm}|C{2.2cm}|C{2.15cm}|",
                          header, caption="Vehicular Live Load (LL)", label="tab:vehicle-live-load",
                          col_sep=TABLE.col_sep_dense)
        + "\n".join(body) + "\n\\end{longtable}\n\\endgroup\n"
        + r"\noindent\textit{Note: Vehicles are those selected in Additional Inputs $>$ Loading. "
        r"Impact factor = 1 + IM for the span, IRC 6 Cl. 208.2 for Class A and wheeled custom "
        r"vehicles, Cl. 208.3 for Class AA, 70R and tracked custom vehicles; Cl. 208 gives none "
        r"for Class SV or the fatigue vehicle."
        + dla_note
        + r" Braking load is 20\% of one vehicle train (Cl. 211.2), acting at the stated height "
        r"above the deck; succeeding trains add 10\% and each lane beyond two adds 5\%. "
        r"Centrifugal force (Cl. 212) arises only on a horizontally curved deck; no horizontal "
        r"curve is specified for this bridge, so it is taken as nil.}"
    )


def _footpath_live_load_table(input_dict) -> str:
    fp = footpath_load(input_dict)
    has_footpath = fp.provided != "None"
    rows = [
        ("Footpath", _tex(fp.provided), "---"),
        ("Footpath width", _num(fp.width_m, 2), "m" if has_footpath else "---"),
        ("Pressure basis", _tex(fp.mode), "---"),
        ("Footpath live load",
         _num(fp.pressure_kN_m2, 3) if has_footpath else "Not applied",
         r"kN/m\textsuperscript{2}" if has_footpath else "---"),
    ]
    body = "\n".join(f"{p} & {v} & {u}" + r" \\[\rowpad]" + "\n\\hline" for p, v, u in rows)
    if not has_footpath:
        note = "No footpath is provided, so no footpath live load is applied."
    elif fp.mode.strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        note = ("Footpath pressure acts on the footway area only; the value is the IRC 6 "
                "Cl. 206.1 load for the default footway type.")
    else:
        note = "Footpath pressure acts on the footway area only; the value is user-defined."
    return (
        longtable_begin("|L{5.5cm}|L{6.5cm}|C{2.5cm}|",
                        r"\tableheader \textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\",
                        caption="Footpath Live Load", label="tab:footpath-live-load")
        + body + "\n\\end{longtable}\n"
        + r"\noindent\textit{Note: " + note + "}"
    )


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m\\textsuperscript{{2}}" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table."""
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):  # permanent load with adding/relieving
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue  # skip N/A factors
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[\rowpad]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[\rowpad]" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\vspace{\tablegap}
""" + longtable_begin(r"""|L{5.5cm}|p{10.0cm}|""", r"""\tableheader \textbf{Parameter} & \textbf{Value} \\""", caption=r"""Dead Load -- Self Weight""") + r"""
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[\rowpad]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[\rowpad]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[\rowpad]
\hline
\end{longtable}

\vspace{\tablegap}
""" + longtable_begin(r"""|L{5.5cm}|p{10.0cm}|""", r"""\tableheader \textbf{Parameter} & \textbf{Value} \\""", caption=r"""Dead Load for Surfacing (DW)""") + r"""
\textnormal{Wearing Course Load} & """ + _wearing_course_load(input_dict) + r""" \\[\rowpad]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[\rowpad]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[\rowpad]
\hline
\end{longtable}

\vspace{\tablegap}
""" + _vehicle_live_load_table(input_dict) + r"""

\vspace{\tablegap}
""" + _footpath_live_load_table(input_dict) + r"""

\vspace{\tablegap}
""" + longtable_begin(r"""|L{5.5cm}|p{10.0cm}|""", r"""\tableheader \textbf{Parameter} & \textbf{Value} \\""", caption=r"""Wind Load (WL) --- per IRC 6""") + r"""
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[\rowpad]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[\rowpad]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[\rowpad]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + vz_str + r""" \\[\rowpad]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + pz_str + r""" \\[\rowpad]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[\rowpad]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[\rowpad]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[\rowpad]
\hline
\end{longtable}

\vspace{\tablegap}
""" + longtable_begin(r"""|L{5.5cm}|p{10.0cm}|""", r"""\tableheader \textbf{Parameter} & \textbf{Value} \\""", caption=r"""Earthquake Load (EL) --- per IRC 6""") + r"""
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[\rowpad]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[\rowpad]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[\rowpad]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[\rowpad]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[\rowpad]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[\rowpad]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[\rowpad]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + '' + r""" kN \\[\rowpad]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + '' + r""" kN \\[\rowpad]
\hline
\end{longtable}

\vspace{\tablegap}
""" + longtable_begin(r"""|L{5.5cm}|p{10.0cm}|""", r"""\tableheader \textbf{Parameter} & \textbf{Value} \\""", caption=r"""Temperature Load (TL) --- per IRC 6""") + r"""
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[\rowpad]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[\rowpad]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[\rowpad]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[\rowpad]
\hline
\end{longtable}

\vspace{\tablegap}
""" + longtable_begin(r"""|C{4.0cm}|p{11.5cm}|""", r"""\tableheader \textbf{Combination ID} & \textbf{Load Cases} \\[\rowpad]""", caption=r"""Load Combinations""") + r"""
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""


