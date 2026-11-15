"""Multi-page table helper: repeated headers, continuation notes and width fitting."""

import re

from osdagbridge.core.reports.styles import TABLE, length_cm, text_width_cm
from osdagbridge.core.reports.tables import (count_columns, fit_to_text_width, group_rows,
                                             keep_rows_together, longtable_begin)

HEADER = r"\tableheader \textbf{A} & \textbf{B} \\"


def test_count_columns_ignores_decorations():
    assert count_columns(r"|C{2cm}|>{\centering\arraybackslash}p{3cm}|l|") == 3
    assert count_columns(r"|L{5.5cm}|p{10.0cm}|") == 2


def test_header_and_caption_repeat_on_every_page():
    tex = longtable_begin(r"|L{5cm}|L{5cm}|", HEADER, caption="Loads", label="tab:loads")
    first, rest = tex.split(r"\endfirsthead")
    assert r"\caption[{Loads}]{\textbf{Loads}}\label{tab:loads}" in first
    # The repeated caption is left out of the List of Tables and marked as continued.
    assert r"\caption[]{\textbf{Loads} " + TABLE.continued_caption + "}" in rest
    cells = r"\textbf{A} & \textbf{B} \\"
    assert first.count(cells) == 1 and rest.count(cells) == 1
    assert r"\endhead" in rest and r"\endfoot" in rest and r"\endlastfoot" in rest


def _table(n_rows):
    rows = "".join(f"\\makecell{{a\\\\b}} & {i} \\\\\n\\hline\n" for i in range(n_rows))
    return longtable_begin(r"|L{5cm}|L{5cm}|", HEADER) + rows + r"\end{longtable}"


def test_short_table_is_kept_on_one_page():
    tex = keep_rows_together(_table(4))
    body = tex.split(r"\endlastfoot")[1]
    # Every row but the last forbids a break, and so does the rule under it.
    assert body.count("\\\\*\n\\hlinenobreak") == 3
    # The last row stays breakable so the table is not tied to what follows.
    assert body.rstrip().endswith("3 \\\\\n\\hline\n\\end{longtable}")
    # The line break inside \makecell is not a row end.
    assert body.count(r"\makecell{a\\b}") == 4


def test_long_table_keeps_two_rows_on_each_side_of_a_break():
    body = keep_rows_together(_table(10)).split(r"\endlastfoot")[1]
    assert body.count(r"\hlinenobreak") == 2
    assert "0 \\\\*" in body and "8 \\\\*" in body and "4 \\\\*" not in body


def test_bare_p_columns_are_set_ragged_right():
    tex = longtable_begin(r"|L{2cm}|p{5cm}|>{\centering\arraybackslash}p{3cm}|", HEADER)
    spec = tex.splitlines()[0]
    assert "|L{5cm}|" in spec and r">{\centering\arraybackslash}p{3cm}" in spec


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
