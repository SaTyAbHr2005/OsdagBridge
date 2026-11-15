from typing import TYPE_CHECKING
from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_TS_NO_OF_GIRDERS,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
)
from osdagbridge.core.reports.report_utils import _tex, _fig_embed
from .styles import TABLE
from .tables import longtable_begin

if TYPE_CHECKING:
    from .report_generator import ReportDataBridge

# The analysis returns load cases in completion order, which changes from run
# to run; the table lists them in a fixed order instead: primary cases,
# combinations by family and number, then the envelopes.
_PRIMARY_CASES = ("SW", "DD", "Crash barrier load", "WL Longitudinal", "WL Transverse",
                  "WL Uplift", "EQ_X", "EQ_Y", "EQ_Z")
_COMBINATION_FAMILIES = ("BASIC", "ACCIDENTAL", "SEISMIC", "SLS_RARE", "SLS_FREQUENT", "SLS_QP")


def _load_case_order(name: str) -> tuple:
    if name.lower().startswith("envelope"):
        return (3, 0 if "uls" in name.lower() else 1, 0, name)
    if ":" in name:                                     # "BASIC_6: 1.0DL + ..."
        family, _, number = name.split(":", 1)[0].strip().rpartition("_")
        if family in _COMBINATION_FAMILIES and number.isdigit():
            return (1, _COMBINATION_FAMILIES.index(family), int(number), name)
        return (2, 0, 0, name)
    if name in _PRIMARY_CASES:
        return (0, _PRIMARY_CASES.index(name), 0, name)
    return (0, len(_PRIMARY_CASES), 0, name)


def ch4_analysis(asum, fig_paths, bridge: "ReportDataBridge", span_m: float):
    lc_summary  = (asum or {}).get('load_cases', {})
    rxn_summary = (asum or {}).get('reactions',  {})

    def _is_moving(lc_name: str) -> bool:
        n = lc_name.lower()
        return "moving" in n or " pos_" in n

    lc_summary  = {k: v for k, v in lc_summary.items()  if not _is_moving(k)}
    rxn_summary = {k: v for k, v in rxn_summary.items() if not _is_moving(k)}

    def _fmt(val, nd=3):
        try:
            # + 0.0 turns a value that rounds to -0 into 0, so no "-0.000".
            return f"{round(float(val), nd) + 0.0:.{nd}f}"
        except (TypeError, ValueError):
            return r"---"

    def _merged_row(lc, bm_d, rxn_d):
        bm_d  = bm_d  or {}
        rxn_d = rxn_d or {}
        return (
            _tex(lc)                              + r" & "
            + _fmt(bm_d.get('max_bm'))           + r" & "
            + _tex(bm_d.get('bm_girder', '---')) + r" & "
            + _fmt(bm_d.get('bm_location'))      + r" & "
            + _fmt(bm_d.get('max_sf'))           + r" & "
            + _tex(bm_d.get('sf_girder', '---')) + r" & "
            + _fmt(bm_d.get('sf_location'))      + r" & "
            + _fmt(rxn_d.get('left_kN'))         + r" & "
            + _fmt(rxn_d.get('right_kN'))        + r" \\[\rowpad]"
        )

    all_lcs = sorted(set(lc_summary) | set(rxn_summary), key=_load_case_order)

    merged_body = ("\n\\hline\n").join(
        _merged_row(lc, lc_summary.get(lc), rxn_summary.get(lc))
        for lc in all_lcs
    ) if all_lcs else r"\multicolumn{9}{|c|}{\textit{No grillage results are available for this run.}} \\[\rowpad]"

    _span_m         = float(bridge.input_dict.get(KEY_SPAN, 0) or 0)
    _allow_live_mm  = _span_m * 1000.0 / 800.0
    _allow_total_mm = _span_m * 1000.0 / 600.0

    # Find governing girder — worst (max) deflection across all girders
    try:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1) or 1)
    except (TypeError, ValueError):
        n = 1

    _live_mm  = None
    _total_mm = None
    for _gi in range(1, n + 1):
        _l = bridge.output_dict.get(f"{KEY_SD_DEFL_LIVE}.G{_gi}")
        _t = bridge.output_dict.get(f"{KEY_SD_DEFL_TOTAL}.G{_gi}")
        if _l is not None:
            _live_mm  = max(_live_mm, float(_l))  if _live_mm  is not None else float(_l)
        if _t is not None:
            _total_mm = max(_total_mm, float(_t)) if _total_mm is not None else float(_t)

    _live_str        = f"{_live_mm:.3f} mm"  if _live_mm  is not None else "---"
    _total_str       = f"{_total_mm:.3f} mm" if _total_mm is not None else "---"
    _allow_live_str  = f"L/800 = {_allow_live_mm:.1f} mm"
    _allow_total_str = f"L/600 = {_allow_total_mm:.1f} mm"
    _live_status     = (r"\statuspass{PASS}" if _live_mm  <= _allow_live_mm  else r"\statusfail{FAIL}") if _live_mm  is not None else "---"
    _total_status    = (r"\statuspass{PASS}" if _total_mm <= _allow_total_mm else r"\statusfail{FAIL}") if _total_mm is not None else "---"
    return r"""
\chapter{Analysis Results}

A grillage model was used for structural analysis. The deck is idealized as a grid of elastic beam elements --- longitudinal members represent the composite steel girders with effective slab, and transverse members represent the slab or cross frames. This section summarizes the critical output from that analysis.

\vspace{\tablegap}
\begingroup
\tablesmallfont
\setlength{\tabcolsep}{\colsepdense}
\renewcommand{\arraystretch}{\densearraystretch}

""" + longtable_begin(r"""|
>{\centering\arraybackslash}p{3.1cm}|
>{\centering\arraybackslash}p{1.7cm}|
>{\centering\arraybackslash}p{1.2cm}|
>{\centering\arraybackslash}p{1.3cm}|
>{\centering\arraybackslash}p{1.7cm}|
>{\centering\arraybackslash}p{1.2cm}|
>{\centering\arraybackslash}p{1.3cm}|
>{\centering\arraybackslash}p{1.6cm}|
>{\centering\arraybackslash}p{1.6cm}|""", r"""\tableheader
& \multicolumn{3}{c|}{\textbf{Bending Moment}}
& \multicolumn{3}{c|}{\textbf{Shear Force}}
& \multicolumn{2}{c|}{\textbf{Reactions (kN)}}\\
% \cline would be painted over by the shading of the next header row;
% hhline draws the rule in its own row and keeps column 1 shaded.
\hhline{|>{\arrayrulecolor{tableHeader}}->{\arrayrulecolor{black}}|-|-|-|-|-|-|-|-|}

\tableheadernext \multirow{-2}{*}{\makecell{\textbf{Load Case /}\\\textbf{Combination}}}
& \makecell{\textbf{Max}\\\textbf{(kNm)}}
& \textbf{Girder}
& \makecell{\textbf{Loc.}\\\textbf{(m)}}
& \makecell{\textbf{Max}\\\textbf{(kN)}}
& \textbf{Girder}
& \makecell{\textbf{Loc.}\\\textbf{(m)}}
& \makecell{\textbf{Left}}
& \makecell{\textbf{Right }}\\""", caption=r"""Summary of Maximum Demands""", col_sep=TABLE.col_sep_dense) + r"""

""" + merged_body + r"""

\hline
\end{longtable}
\endgroup

\vspace{\tablegap}
""" + longtable_begin(r"""|L{7cm}|p{8.5cm}|""", r"""\tableheader \textbf{Parameter} & \textbf{Value} \\""", caption=r"""Deflection Summary (Live Load \& Total Load)""") + r"""
\textnormal{Deflection due to Live Load, $\delta_{LL}$} & """ + _live_str + r""" \\[\rowpad]
\hline
\textnormal{Allowable Live Load Deflection ($\Delta_{allow}$)} & """ + _allow_live_str + r""" \\[\rowpad]
\hline
\textnormal{Live Load Deflection Check Status} & """ + _live_status + r""" \\[\rowpad]
\hline
\textnormal{Deflection due to Total Load, $\delta_{total}$} & """ + _total_str + r""" \\[\rowpad]
\hline
\textnormal{Allowable Total Deflection ($\Delta_{allow}$)} & """ + _allow_total_str + r""" \\[\rowpad]
\hline
\textnormal{Total Load Deflection Check Status} & """ + _total_status + r""" \\[\rowpad]
\hline
\end{longtable}

\vspace{\tablegap}
\noindent
""" + _fig_embed(fig_paths.get('bm_envelope'), 'Bending Moment Envelope (Envelope ULS): Max/min BM along span. X-axis: distance from left support (m). Y-axis: Bending Moment (kN-m).') + r"""
""" + _fig_embed(fig_paths.get('sf_envelope'), 'Shear Force Envelope (Envelope ULS): Max/min SF along span. X-axis: distance from left support (m). Y-axis: Shear Force (kN).') + r"""
""" + _fig_embed(fig_paths.get('defl_ll'), 'Vertical Deflection D$_y$ (1.0 LL): Maximum deflection along span. Load Case: 1.0 LL, Combination: $D_y$. Nodes shown. Isometric view.') + r"""
"""

