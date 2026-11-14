"""Multi-page table helper: repeated headers, continuation notes and width fitting."""

import re

from osdagbridge.core.reports.styles import TABLE, length_cm, text_width_cm
from osdagbridge.core.reports.tables import count_columns, fit_to_text_width, group_rows, longtable_begin

HEADER = r"\tableheader \textbf{A} & \textbf{B} \\"


def test_count_columns_ignores_decorations():
    assert count_columns(r"|C{2cm}|>{\centering\arraybackslash}p{3cm}|l|") == 3
    assert count_columns(r"|L{5.5cm}|p{10.0cm}|") == 2


def test_header_and_caption_repeat_on_every_page():
    tex = longtable_begin(r"|L{5cm}|L{5cm}|", HEADER, caption="Loads", label="tab:loads")
    first, rest = tex.split(r"\endfirsthead")
    assert r"\caption[Loads]{\textbf{Loads}}\label{tab:loads}" in first
    # The repeated caption is left out of the List of Tables and marked as continued.
    assert r"\caption[]{\textbf{Loads} " + TABLE.continued_caption + "}" in rest
    assert first.count(HEADER) == 1 and rest.count(HEADER) == 1
    assert r"\endhead" in rest and r"\endfoot" in rest and r"\endlastfoot" in rest


def test_every_broken_page_ends_with_a_continued_note():
    tex = longtable_begin(r"|L{5cm}|L{5cm}|", HEADER)
    foot = tex[tex.index(r"\endhead"):tex.index(r"\endfoot")]
    assert r"\multicolumn{2}{r}{\tablecontinuednote}" in foot


def test_wide_table_is_narrowed_to_the_text_block():
    spec = fit_to_text_width(r"|C{8cm}|C{8cm}|C{8cm}|")
    widths = [float(w) for w in re.findall(r"\{([\d.]+)cm\}", spec)]
    padding = 3 * 2 * length_cm(TABLE.col_sep) + 4 * length_cm(TABLE.rule_width)
    assert sum(widths) + padding <= text_width_cm() + 0.02
    assert widths[0] == widths[1] == widths[2]          # scaled in proportion


def test_table_that_fits_is_left_alone():
    spec = r"|L{5.5cm}|L{6.0cm}|"
    assert fit_to_text_width(spec) == spec


def test_group_rows_keep_a_group_on_one_page():
    tex = group_rows("G1", ["a & 1", "b & 2", "c & 3"], 3)
    assert tex.startswith(r"\multirow{3}{*}{\makecell{G1}}")
    # Rows inside the group forbid a page break; the group ends with a full rule.
    assert tex.count(r"\\*[\rowpad]") == 2
    assert tex.count(r"\groupcline{2-3}") == 2
    assert tex.rstrip().endswith(r"\hline")
    assert group_rows("G1", [], 3) == ""
