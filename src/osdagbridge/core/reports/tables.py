"""
Opening block for the report's multi-page tables.

Every longtable in the report starts with ``longtable_begin()``. It writes the
caption and header for the first page, repeats them under a "(continued)"
caption on every following page (``\\endfirsthead`` / ``\\endhead``), closes
each broken page with a "Continued on next page" line (``\\endfoot``), and
narrows the column widths when the table would otherwise run past the text
block defined in ``styles.PAGE``.

The chapter supplies the body rows and the closing ``\\end{longtable}``.
"""

import re

from .styles import TABLE, length_cm, text_width_cm

# Column types that take an explicit width, including the L/C/R types the
# preamble defines as ragged-right, centred and ragged-left p-columns.
_WIDTH = re.compile(r"([pmbLCR])\{([\d.]+)cm\}")
# >{...}, <{...} and @{...} decorate a column without adding one.
_DECORATION = re.compile(r"[<>@]\{(?:[^{}]|\{[^{}]*\})*\}")
_COLUMN = re.compile(r"[pmbLCR]\{[^{}]*\}|[lcr]")
# A full rule right after a row end, past an optional [gap] argument.
_RULE_AFTER_ROW = re.compile(r"(?:\[[^\]]*\])?\s*(\\hline)(?![a-zA-Z])")


def count_columns(spec: str) -> int:
    """Number of columns declared by a tabular column specification."""
    return len(_COLUMN.findall(_DECORATION.sub("", spec)))


def fit_to_text_width(spec: str, col_sep: str = TABLE.col_sep) -> str:
    """Scale the cm column widths in ``spec`` down so the table fits the text block.

    The available width is the text width less the column padding
    (``col_sep`` on both sides of every column) and the vertical rules.
    Specs that already fit are returned unchanged. Only widths given in cm
    are scaled; columns sized any other way keep their natural width.
    """
    widths = [float(w) for _, w in _WIDTH.findall(spec)]
    if not widths:
        return spec
    padding = count_columns(spec) * 2 * length_cm(col_sep)
    rules = spec.count("|") * length_cm(TABLE.rule_width)
    available = text_width_cm() - padding - rules
    total = sum(widths)
    if total <= available:
        return spec
    scale = available / total
    return _WIDTH.sub(lambda m: f"{m.group(1)}{{{float(m.group(2)) * scale:.2f}cm}}", spec)


def group_rows(label: str, rows: list[str], n_cols: int) -> str:
    """Rows of one group, e.g. the members of one bracing pair, kept on one page.

    label   first-column text spanning all rows, already LaTeX-escaped
    rows    row bodies from the second column on, each starting with ``&``
            and without the closing ``\\\\``
    n_cols  number of table columns
    """
    if not rows:
        return ""
    inner_rule = " \\\\*[\\rowpad]\n\\groupcline{2-" + str(n_cols) + "}\n"
    return (r"\multirow{" + str(len(rows)) + r"}{*}{\makecell{" + label + "}} "
            + inner_rule.join(rows) + " \\\\[\\rowpad]\n\\hline")


def _row_ends(body: str) -> list[int]:
    """Positions of the row-ending ``\\\\`` in a table body, skipping any inside braces."""
    ends, depth, i = [], 0, 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            if body.startswith("\\\\", i) and depth == 0:
                ends.append(i)
            i += 2                      # also skips \{ and \}
            continue
        depth += (c == "{") - (c == "}")
        i += 1
    return ends


def keep_rows_together(tex: str) -> str:
    """Stop longtables splitting badly across pages.

    A table of up to ``TABLE.keep_whole_rows`` rows is never split: it moves
    to the next page whole. A longer table is not broken after its first row
    or before its last, so no page carries a single row of it. ``\\\\*`` is
    longtable's row end that forbids a page break after the row.
    """
    out, pos = [], 0
    for m in re.finditer(r"\\endlastfoot(.*?)\\end\{longtable\}", tex, re.S):
        start = m.start(1)
        body = m.group(1)
        ends = _row_ends(body)
        breakable = [e for e in ends if not body.startswith("\\\\*", e)]
        # The last row end stays breakable, or the table would be tied to
        # whatever follows it.
        if len(ends) <= TABLE.keep_whole_rows:
            locked = [e for e in breakable if e != ends[-1]]
        else:
            locked = [e for e in breakable if e in (ends[0], ends[-2])]
        out.append(tex[pos:start])
        last = 0
        for e in locked:
            out.append(body[last:e + 2] + "*")
            last = e + 2
            # A longtable \hline is itself a break point; use the variant without one.
            rule = _RULE_AFTER_ROW.match(body, last)
            if rule:
                out.append(body[last:rule.start(1)] + r"\hlinenobreak")
                last = rule.end()
        out.append(body[last:])
        pos = m.end(1)
    out.append(tex[pos:])
    return "".join(out)


def longtable_begin(spec: str, header: str, caption: str = "", label: str = "",
                    col_sep: str = TABLE.col_sep) -> str:
    """LaTeX from ``\\begin{longtable}`` down to ``\\endlastfoot``.

    spec     column specification without the outer braces
    header   header row(s), each ending in ``\\\\``; may span several rows
    caption  caption text, already LaTeX-escaped; set in bold
    label    optional ``\\label`` key for the table
    col_sep  column gap in force where the table is placed, used for fitting
    """
    n_cols = count_columns(spec)
    # A bare p{} column justifies its text, which leaves wide gaps in narrow
    # cells; set it ragged right like the L columns.
    spec = fit_to_text_width(re.sub(r"(?<=\|)p\{", "L{", spec), col_sep)
    head = "\\hline\n" + header.strip() + "\n\\hline\n"

    if caption:
        # The optional argument keeps the List of Tables entry in plain type.
        first_caption = r"\caption[{" + caption + r"}]{\textbf{" + caption + "}}"
        if label:
            first_caption += r"\label{" + label + "}"
        first_caption += "\\\\\n"
        repeat_caption = (r"\caption[]{\textbf{" + caption + "} "
                          + TABLE.continued_caption + "}\\\\\n")
    else:
        first_caption = ""
        repeat_caption = (r"\multicolumn{" + str(n_cols) + r"}{l}{\textit{"
                          + TABLE.continued_caption + "}}\\\\\n")

    return (
        r"\begin{longtable}{" + spec + "}\n"
        + first_caption + head + "\\endfirsthead\n"
        + repeat_caption + head + "\\endhead\n"
        + r"\multicolumn{" + str(n_cols) + r"}{r}{\tablecontinuednote}\\" + "\n"
        + "\\endfoot\n"
        + "\\endlastfoot\n"
    )
