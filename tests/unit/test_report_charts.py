"""Summary charts: files are written only when there is data to plot."""

from osdagbridge.core.reports.charts import quantity_bar_chart, ur_bar_chart

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _is_png(path):
    with open(path, "rb") as fh:
        return fh.read(8) == PNG_SIGNATURE


def test_ur_chart_is_written_with_passing_and_failing_bars(tmp_path):
    path = str(tmp_path / "ur.png")
    assert ur_bar_chart([("Moment", 0.82), ("Fatigue", 1.58), ("Stress", 0.0)], path) == path
    assert _is_png(path)


def test_ur_chart_without_data_writes_nothing(tmp_path):
    path = tmp_path / "ur.png"
    assert ur_bar_chart([], str(path)) is None
    assert not path.exists()


def test_quantity_chart_draws_side_by_side_panels(tmp_path):
    path = str(tmp_path / "qty.png")
    panels = [("Concrete volume (m$^3$)", [63.0, 18.1]), ("Reinforcement weight (MT)", [7.56, None])]
    assert quantity_bar_chart(["Deck slab", "Crash barriers"], panels, path) == path
    assert _is_png(path)


def test_quantity_chart_with_no_values_writes_nothing(tmp_path):
    path = tmp_path / "qty.png"
    assert quantity_bar_chart(["Girders"], [("Steel (MT)", [None])], str(path)) is None
    assert not path.exists()
