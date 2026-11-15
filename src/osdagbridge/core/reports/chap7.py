import logging
import os

from .charts import quantity_bar_chart
from osdagbridge.core.utils.common import KEY_DECK_CONCRETE_GRADE_BASIC, KEY_DS_REINF_MATERIAL

from .report_utils import _fig_embed, _tex
from .styles import FIGURE, TABLE
from .tables import longtable_begin

logger = logging.getLogger(__name__)


def _qty(input_dict, *keys):
    """Sum of BOM values (strings such as "12.34" or "N.A."); None when none is a number."""
    total, found = 0.0, False
    for key in keys:
        try:
            total += float(input_dict.get(key))
            found = True
        except (TypeError, ValueError):
            pass
    return total if found else None


def _quantity_charts(input_dict, fig_dir):
    """Steel tonnage by component, and concrete volume next to reinforcement weight."""
    ed_rows = input_dict.get("end_diaphragm_rows") or []
    steel = [
        _qty(input_dict, "steel_girders_wt_total"),
        _qty(input_dict, "bracing_top_wt_total", "bracing_bot_wt_total", "bracing_diag_wt_total"),
        sum(row["weight_t"] for row in ed_rows) if ed_rows else None,
    ]
    charts = [
        (["Plate girders", "Cross bracing", "End diaphragms"],
         [("Structural steel (MT)", steel)],
         "qty_steel.png", "Structural Steel Tonnage by Component"),
        (["Deck slab", "Crash barriers"],
         [("Concrete volume (m$^3$)", [_qty(input_dict, "concrete_deck_vol_total"),
                                       _qty(input_dict, "crash_barrier_vol_total")]),
          ("Reinforcement weight (MT)", [_qty(input_dict, "rebar_deck_wt_total"), None])],
         "qty_concrete.png", "Concrete Volume and Reinforcement Weight"),
    ]
    figures = []
    for labels, panels, name, caption in charts:
        try:
            path = quantity_bar_chart(labels, panels, os.path.join(fig_dir, name))
        except Exception:
            # The charts restate the table; losing one must not stop the report.
            logger.exception("Quantity chart %s could not be drawn", name)
            path = None
        if path:
            figures.append(_fig_embed(path.replace("\\", "/"), caption, width=FIGURE.chart_width))
    if not figures:
        return ""
    parts = [name for name, value in zip(("girders", "cross bracing", "end diaphragms"), steel)
             if value is not None]
    total = sum(value for value in steel if value is not None)
    steel_text = (f"Structural steel for the {', '.join(parts[:-1])}{' and ' if len(parts) > 1 else ''}"
                  f"{parts[-1]} totals {total:.2f} MT. ") if parts else ""
    return ("\n" r"\vspace{\tablegap}" "\n"
            r"\noindent The charts below summarise the bill of materials. " + steel_text +
            r"Concrete and reinforcement are drawn on separate scales; "
            r"n/a marks a quantity the take-off does not compute (crash barrier reinforcement)."
            "\n\n" + "\n".join(figures) + "\n")


def _grade(input_dict, key) -> str:
    """' (grade)' for a material picked in the inputs, or '' when none is set."""
    grade = str(input_dict.get(key) or "").strip()
    return f" ({_tex(grade)})" if grade else ""


def _end_diaphragm_rows(rows: list) -> str:
    """Item 7 of the bill of materials: one sub-item per end diaphragm member kind."""
    if not rows:
        return r"7 & End Diaphragms & N.A. & N.A. & N.A. & N.A. & N.A. \\" + "\n\\hline\n"
    out = ""
    for letter, row in zip("abcdefgh", rows):
        number = f"7({letter})" if len(rows) > 1 else "7"
        cells = (number, row["label"], row["vol_formula"], row["qty"], row["vol_total"],
                 row["wt_single"], row["wt_total"])
        out += " & ".join(cells) + r" \\" + "\n\\hline\n"
    return out


def ch7_quantities(input_dict, fig_dir=None):
    """Chapter 7: bill of materials, then the quantity charts when ``fig_dir`` is given."""
    charts = _quantity_charts(input_dict, fig_dir) if fig_dir else ""
    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

\begingroup
\setlength{\tabcolsep}{\colseptight}
""" + longtable_begin(
        r"""|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|""",
        r"""\tableheader \textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)} \\""",
        caption=r"""Bill of Materials (Steel, Concrete, and Reinforcement Quantities)""",
        label="tab:bill-of-materials",
        col_sep=TABLE.col_sep_tight,
    ) + r"""1 &Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
3 & Concrete""" + _grade(input_dict, KEY_DECK_CONCRETE_GRADE_BASIC) + r""" for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
4 & Reinforcement Steel""" + _grade(input_dict, KEY_DS_REINF_MATERIAL) + r""" & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\hline
""" + _end_diaphragm_rows(input_dict.get("end_diaphragm_rows") or []) + r"""\end{longtable}
\endgroup
""" + charts


