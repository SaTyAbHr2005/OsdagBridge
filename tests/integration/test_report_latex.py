"""Compile a short report with the bundled TeX: preamble, a table that breaks
across pages, status cells and a chart. Skipped where no pdflatex is found."""

import shutil
import subprocess

import pytest

from osdagbridge.core.reports.charts import ur_bar_chart
from osdagbridge.core.reports.report_generator import preamble
from osdagbridge.core.reports.report_utils import _fig_embed
from osdagbridge.core.reports.tables import group_rows, longtable_begin


def _pdflatex():
    try:
        from osdag_latex_env.__main__ import OsdagLatexEnv
        exe = OsdagLatexEnv().pdflatex
        if exe:
            return str(exe)
    except Exception:
        pass
    return shutil.which("pdflatex")


def _document(chart_path):
    rows = "\n".join(group_rows(f"G{g}", [rf"Check {i} & \statuspass{{PASS}}" for i in range(4)], 3)
                     for g in range(1, 16))
    table = (longtable_begin(r"|C{2cm}|L{6cm}|C{3cm}|",
                             r"\tableheader \textbf{Girder} & \textbf{Check} & \textbf{Status} \\",
                             caption="Long Check Table", label="tab:long")
             + rows + "\n\\end{longtable}\n")
    return (r"\chapter{Design Checks}" "\n"
            r"\section{Overall Design Check Summary}\label{sec:overall-summary}" "\n"
            + table + r"Failing: \statusfail{FAIL}, see Table~\ref{tab:long}." "\n"
            + _fig_embed(chart_path.replace("\\", "/"), "Utilization Ratios --- Plate Girders") + "\n"
            r"\end{document}" "\n")


@pytest.mark.parametrize("preview", [False, True])
def test_report_compiles_without_errors(tmp_path, preview):
    exe = _pdflatex()
    if not exe:
        pytest.skip("pdflatex not available")
    chart = ur_bar_chart([("Moment", 0.8), ("Fatigue", 1.58)], str(tmp_path / "ur.png"))
    tex = preamble("Test Bridge", "J-1", "2026-01-01", preview=preview, author="Tester") + _document(chart)
    (tmp_path / "report.tex").write_text(tex, encoding="utf-8")

    for _ in range(2):                    # second pass resolves references and page totals
        subprocess.run([exe, "-interaction=nonstopmode", "report.tex"], cwd=tmp_path,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)

    log = (tmp_path / "report.log").read_text(encoding="utf-8", errors="replace")
    errors = [line for line in log.splitlines() if line.startswith("! ")]
    assert not errors, errors
    assert (tmp_path / "report.pdf").stat().st_size > 0
    assert ("draftwatermark" in log) == preview
