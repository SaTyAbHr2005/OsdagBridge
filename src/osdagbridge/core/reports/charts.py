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
    x_max = max(UR_LIMIT * 1.25, max(urs) * 1.3)
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
    ax.set_xlim(0, x_max)
    _style_axis(ax, "Utilization ratio")

    fig.savefig(path, facecolor="white")
    return path


def quantity_bar_chart(labels: Sequence[str],
                       panels: Sequence[tuple[str, Sequence[Optional[float]]]],
                       path: str) -> Optional[str]:
    """Save horizontal bar panels side by side that share the row labels.

    Each panel is (axis label, values aligned with ``labels``) and has its
    own scale, so quantities in different units are never drawn against one
    axis. A value of None draws no bar and is marked "n/a". Returns ``path``,
    or None when no panel has a value.
    """
    if not labels or not any(v is not None for _, values in panels for v in values):
        return None
    fig = Figure(
        figsize=(CHART.width_in, CHART.frame_in + CHART.bar_row_in * len(labels)),
        dpi=CHART.dpi,
        layout="constrained",
    )
    axes = fig.subplots(1, len(panels), sharey=True, squeeze=False)[0]
    rows = range(len(labels))
    text = _colour(CHART.text)
    for ax, (axis_label, values) in zip(axes, panels):
        present = [v for v in values if v is not None]
        x_max = (max(present) * 1.3) if present and max(present) > 0 else 1.0
        ax.barh([r for r, v in zip(rows, values) if v is not None], present,
                height=0.6, color=_colour(CHART.quantity_bar))
        for row, value in zip(rows, values):
            ax.text((value or 0.0) + 0.012 * x_max, row, "n/a" if value is None else f"{value:.2f}",
                    va="center", fontsize=CHART.font_size, color=text)
        ax.set_xlim(0, x_max)
        _style_axis(ax, axis_label)
    axes[0].set_yticks(list(rows), labels)

    fig.savefig(path, facecolor="white")
    return path


def _style_axis(ax, xlabel: str) -> None:
    """Recessive grid and spines, rows read top to bottom."""
    text = _colour(CHART.text)
    if not ax.yaxis_inverted():
        ax.invert_yaxis()
    ax.set_xlabel(xlabel, fontsize=CHART.font_size, color=text)
    ax.tick_params(labelsize=CHART.font_size, colors=text, length=0)
    ax.xaxis.grid(True, color=_colour(CHART.grid), linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_colour(CHART.grid))
