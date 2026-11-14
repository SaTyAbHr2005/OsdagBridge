"""
Bar charts for the report's summary sections, saved as PNG files for
``_fig_embed``. The bundled TeX distribution has no pgfplots, so the
charts are drawn with matplotlib's object API (no pyplot), which is safe
to call from the report thread while the Qt GUI is running.
"""

from typing import Optional, Sequence

from matplotlib.figure import Figure

from .styles import CHART

UR_LIMIT = 1.0


def _colour(hex_value: str) -> str:
    return "#" + hex_value


def ur_bar_chart(items: Sequence[tuple[str, float]], path: str) -> Optional[str]:
    """Save a horizontal bar chart of (label, utilization ratio) pairs.

    Bars run top to bottom in the order given. Bars above UR = 1.0 are drawn
    in the fail colour, hatched and labelled FAIL; a dashed line marks the
    limit. Returns ``path``, or None when there is nothing to plot.
    """
    if not items:
        return None
    labels = [label for label, _ in items]
    urs = [float(ur) for _, ur in items]
    failing = [ur > UR_LIMIT for ur in urs]

    fig = Figure(
        figsize=(CHART.width_in, CHART.frame_in + CHART.bar_row_in * len(urs)),
        dpi=CHART.dpi,
        layout="constrained",
    )
    ax = fig.add_subplot()
    rows = range(len(urs))
    bars = ax.barh(
        rows, urs, height=0.6,
        color=[_colour(CHART.fail_bar if fail else CHART.pass_bar) for fail in failing],
    )
    for bar, fail in zip(bars, failing):
        if fail:
            # Hatch lines take the edge colour.
            bar.set_hatch("////")
            bar.set_edgecolor("white")
            bar.set_linewidth(0)

    # Room on the right for the value labels.
    x_max = max(UR_LIMIT * 1.25, max(urs) * 1.2)
    text = _colour(CHART.text)
    for row, ur, fail in zip(rows, urs, failing):
        # White backing keeps a label readable where it crosses the limit line.
        ax.text(ur + 0.012 * x_max, row, f"{ur:.2f}" + ("  FAIL" if fail else ""),
                va="center", fontsize=CHART.font_size, color=text,
                fontweight="bold" if fail else "normal", zorder=4,
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.0})

    ax.axvline(UR_LIMIT, color=_colour(CHART.limit_line), linestyle="--", linewidth=1.2)
    ax.annotate(f"UR = {UR_LIMIT:.1f}", xy=(UR_LIMIT, 1.0), xycoords=("data", "axes fraction"),
                xytext=(3, 2), textcoords="offset points", va="bottom",
                fontsize=CHART.font_size, color=_colour(CHART.limit_line))

    ax.set_yticks(list(rows), labels)
    ax.invert_yaxis()
    ax.set_xlim(0, x_max)
    ax.set_xlabel("Utilization ratio", fontsize=CHART.font_size, color=text)
    ax.tick_params(labelsize=CHART.font_size, colors=text, length=0)
    ax.xaxis.grid(True, color=_colour(CHART.grid), linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_colour(CHART.grid))

    fig.savefig(path, facecolor="white")
    return path
