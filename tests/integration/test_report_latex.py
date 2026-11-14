"""Compile a short report with the bundled TeX: preamble, a table that breaks
across pages, status cells and a chart. Skipped where no pdflatex is found."""

import shutil
import subprocess

import pytest

from osdagbridge.core.reports.chap8 import design_log_chapter
from osdagbridge.core.reports.charts import ur_bar_chart
from osdagbridge.core.reports.executive_summary import executive_summary
from osdagbridge.core.reports.report_generator import ReportMetadata, preamble, title_page
from osdagbridge.core.reports.report_utils import _fig_embed, _tex
from osdagbridge.core.reports.tables import group_rows, longtable_begin
from osdagbridge.core.utils.common import KEY_TS_NO_OF_GIRDERS

# Text a user can type into the report form; every character here is special to LaTeX.
AWKWARD = "Bridge_A & B: #1 [rev] 50%"


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
                             caption="Long Check Table " + _tex(AWKWARD), label="tab:long")
             + rows + "\n\\end{longtable}\n")
    meta = ReportMetadata(project_name=AWKWARD, project_location="Mumbai", designer=AWKWARD, client="",
                          company="", additional_comments=AWKWARD, report_date="2026-01-01")
    summary = executive_summary(
        {KEY_TS_NO_OF_GIRDERS: "2"},
        {"design_results": {"per_girder": {"G1": {"checks": [
            {"name": "Int.Stiff: Leg ≤ H_limit", "dcr": 1.48, "status": "FAIL"}]}}}}, {})
    return (title_page(meta, None, None) + summary + r"\chapter{Design Checks}" "\n"
            r"\section{Plate Girder Design}\label{sec:plate-girder}" "\n"
            r"\section{Overall Design Check Summary}\label{sec:overall-summary}" "\n"
            + table + r"Failing: \statusfail{FAIL}, see Table~\ref{tab:long}." "\n"
            + _fig_embed(chart_path.replace("\\", "/"), "Utilization Ratios --- Plate Girders") + "\n"
            # Real log lines start with a [hh:mm:ss] stamp.
            + design_log_chapter(["[10:00:01]   Stage 1: input_validation complete",
                                  "[10:00:02]   WARNING : deck overhang > 1.5 m & 50% wider"]) + "\n"
            r"\end{document}" "\n")


@pytest.mark.parametrize("preview", [False, True])
def test_report_compiles_without_errors(tmp_path, preview):
    exe = _pdflatex()
    if not exe:
        pytest.skip("pdflatex not available")
    chart = ur_bar_chart([("Moment", 0.8), ("Fatigue", 1.58)], str(tmp_path / "ur.png"))
    tex = preamble(AWKWARD, "J-1", "2026-01-01", preview=preview, author=AWKWARD) + _document(chart)
    (tmp_path / "report.tex").write_text(tex, encoding="utf-8")

    for _ in range(2):                    # second pass resolves references and page totals
        subprocess.run([exe, "-interaction=nonstopmode", "report.tex"], cwd=tmp_path,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)

    log = (tmp_path / "report.log").read_text(encoding="utf-8", errors="replace")
    errors = [line for line in log.splitlines() if line.startswith("! ")]
    assert not errors, errors
    assert "Token not allowed in a PDF string" not in log      # PDF title and author are plain text
    assert "undefined references" not in log                    # Critical Checks links resolve
    # A "]" in the caption must not cut the List of Tables entry short.
    aux = (tmp_path / "report.aux").read_text(encoding="utf-8", errors="replace")
    lot_entries = [line for line in aux.splitlines() if line.startswith(r"\@writefile{lot}")]
    assert any(r"[rev] 50\%" in line for line in lot_entries), lot_entries
    assert (tmp_path / "report.pdf").stat().st_size > 0
    assert ("draftwatermark" in log) == preview
