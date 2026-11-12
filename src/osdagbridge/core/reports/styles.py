"""
Layout and theme settings for the OsdagBridge design report.

Page geometry, the header and footer, table spacing and status colours are
defined here and nowhere else. ``latex_definitions()`` turns them into named
LaTeX lengths, colours and macros (``\\rowpad``, ``\\tablegap``,
``\\statusfail{...}`` ...), and the chapter templates use those names rather
than literal values. One-off spacing inside a single form layout stays with
its template.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PageStyle:
    paper: str = "a4paper"
    font_size: str = "12pt"
    margin_top: str = "1in"
    margin_bottom: str = "1in"
    margin_left: str = "1in"
    margin_right: str = "1in"
    line_stretch: float = 1.15


@dataclass(frozen=True)
class Palette:
    # HTML hex values without the leading '#', as expected by xcolor.
    brand: str = "91B014"
    # 15% tint of the brand green: marks header rows without competing
    # with the PASS/FAIL colours in the table body.
    table_header: str = "EEF3DC"
    status_pass: str = "000000"
    status_fail: str = "FF0000"
    log_warning: str = "0000FF"
    log_error: str = "FF0000"


@dataclass(frozen=True)
class TableStyle:
    # Column gaps, widest first. Most tables use the default; the BOM and
    # standards tables use tight and the nine-column analysis summary dense.
    col_sep: str = "4pt"
    col_sep_tight: str = "3.5pt"
    col_sep_dense: str = "3pt"
    array_stretch: float = 1.12
    array_stretch_dense: float = 1.25
    row_pad: str = "6pt"
    row_pad_wide: str = "8pt"
    rule_width: str = "0.5pt"
    extra_row_height: str = "0.6pt"
    # Space above and below every longtable; the caption already separates
    # a table from the paragraph before it.
    longtable_pre: str = "0pt"
    longtable_post: str = "6pt"
    # A table starting with fewer lines than this left on the page moves to
    # the next page instead of leaving its caption or first row stranded.
    # A longtable needs room for caption, header, "Continued" foot and at
    # least one row; with less, longtable sets only the foot on that page
    # and the first header lands under the repeated one on the next page.
    min_lines_before_table: int = 5
    min_lines_before_longtable: int = 10
    # Labels on tables that break across pages.
    continued_caption: str = "(continued)"
    continued_note: str = r"\small\itshape Continued on next page"


@dataclass(frozen=True)
class SpacingScale:
    # Vertical gaps between blocks of content, smallest first.
    small: str = "0.4em"    # a heading or note directly attached to a table
    block: str = "1em"      # paragraph or table followed by another table
    section: str = "2em"    # start of a new group within a section


@dataclass(frozen=True)
class FigureStyle:
    plot_width: str = r"0.75\textwidth"        # analysis plots (Chapter 4)
    summary_width: str = r"0.9\textwidth"      # executive summary views
    drawing_width: str = r"0.85\textwidth"     # single drawings (Chapter 6)
    grid_cell_width: str = r"0.31\textwidth"   # three drawings side by side
    placeholder_width: str = r"0.97\textwidth"
    gap_before_drawing: str = "4pt"
    # Plots carry their own whitespace margin, so the gaps around them are
    # pulled in slightly to keep plot and caption visually together.
    plot_gap_outer: str = "-0.5em"
    plot_gap_caption: str = "0.5em"
    plot_caption_size: str = r"\small"


@dataclass(frozen=True)
class Typography:
    chapter_title: str = r"\Large\bfseries"
    # The report class leaves a large gap above chapter titles; pulling
    # them up keeps the title close to the running header.
    chapter_title_before: str = "-30pt"
    chapter_title_after: str = "10pt"
    toc_title: str = r"\Large\bfseries"
    toc_depth: int = 2
    caption_label_font: str = "bf"
    caption_justification: str = "raggedright"
    caption_skip: str = "2pt"
    # Dense tables and long formulas inside table cells.
    table_small_font: str = r"\footnotesize"


@dataclass(frozen=True)
class TitlePageStyle:
    top_gap: str = "1.5cm"
    name_size: str = r"\Huge"
    name_gap: str = "0.3cm"
    tagline_size: str = r"\large"
    document_type_size: str = r"\Large"
    block_gap: str = "1.5cm"
    logo_gap: str = "1cm"
    osdag_logo_width: str = r"0.6\textwidth"
    org_logo_width: str = r"0.35\textwidth"
    org_logo_height: str = "2.2cm"
    label_width: str = "4cm"
    value_width: str = "10cm"


@dataclass(frozen=True)
class HeaderFooterStyle:
    footer_left: str = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
    page_label: str = r"Page \thepage\ of \pageref{LastPage}"
    rule_thickness: str = "1pt"
    default_value_note: str = r"* Software default value"


PAGE = PageStyle()
COLORS = Palette()
TABLE = TableStyle()
SPACING = SpacingScale()
FIGURE = FigureStyle()
TYPOGRAPHY = Typography()
TITLE_PAGE = TitlePageStyle()
HEADER_FOOTER = HeaderFooterStyle()


_PAPER_WIDTH_CM = {"a4paper": 21.0}
_UNIT_CM = {"cm": 1.0, "mm": 0.1, "in": 2.54, "pt": 2.54 / 72.27}


def length_cm(value: str) -> float:
    """Convert a LaTeX length such as ``1in``, ``4pt`` or ``2.5cm`` to centimetres."""
    for unit, factor in _UNIT_CM.items():
        if value.endswith(unit):
            return float(value[: -len(unit)]) * factor
    raise ValueError(f"Unsupported length: {value!r}")


def text_width_cm() -> float:
    """Width of the text block, i.e. the widest a table may be."""
    return (_PAPER_WIDTH_CM[PAGE.paper]
            - length_cm(PAGE.margin_left) - length_cm(PAGE.margin_right))


def document_class() -> str:
    """``\\documentclass`` line with the base font size and paper."""
    return rf"\documentclass[{PAGE.font_size},{PAGE.paper}]{{report}}"


def geometry_package() -> str:
    """``geometry`` package line with the page margins."""
    return (
        rf"\usepackage[{PAGE.paper}, top={PAGE.margin_top}, bottom={PAGE.margin_bottom}, "
        rf"left={PAGE.margin_left}, right={PAGE.margin_right}]{{geometry}}"
    )


def latex_definitions() -> str:
    """Colours, lengths and macros used by the chapter templates."""
    t, c = TABLE, COLORS
    return rf"""
\definecolor{{osdagGreen}}{{HTML}}{{{c.brand}}}
\definecolor{{statusPass}}{{HTML}}{{{c.status_pass}}}
\definecolor{{statusFail}}{{HTML}}{{{c.status_fail}}}
\definecolor{{logWarning}}{{HTML}}{{{c.log_warning}}}
\definecolor{{logError}}{{HTML}}{{{c.log_error}}}
\definecolor{{tableHeader}}{{HTML}}{{{c.table_header}}}
\newcommand{{\tableheader}}{{\rowcolor{{tableHeader}}}}
\newcommand{{\statuspass}}[1]{{\textcolor{{statusPass}}{{#1}}}}
\newcommand{{\statusfail}}[1]{{\textcolor{{statusFail}}{{#1}}}}

\setlength{{\tabcolsep}}{{{t.col_sep}}}
\renewcommand{{\arraystretch}}{{{t.array_stretch}}}
\setlength{{\LTleft}}{{\fill}}
\setlength{{\LTright}}{{\fill}}
\setlength{{\LTpre}}{{{t.longtable_pre}}}
\setlength{{\LTpost}}{{{t.longtable_post}}}
\setlength{{\arrayrulewidth}}{{{t.rule_width}}}
\setlength{{\extrarowheight}}{{{t.extra_row_height}}}

\newlength{{\rowpad}}\setlength{{\rowpad}}{{{t.row_pad}}}
\newlength{{\rowpadwide}}\setlength{{\rowpadwide}}{{{t.row_pad_wide}}}
\newlength{{\gapsmall}}\setlength{{\gapsmall}}{{{SPACING.small}}}
\newlength{{\tablegap}}\setlength{{\tablegap}}{{{SPACING.block}}}
\newlength{{\sectiongap}}\setlength{{\sectiongap}}{{{SPACING.section}}}
\newlength{{\colseptight}}\setlength{{\colseptight}}{{{t.col_sep_tight}}}
\newlength{{\colsepdense}}\setlength{{\colsepdense}}{{{t.col_sep_dense}}}
\newcommand{{\densearraystretch}}{{{t.array_stretch_dense}}}
\newcommand{{\tablecontinuednote}}{{{t.continued_note}}}

\BeforeBeginEnvironment{{table}}{{\needspace{{{t.min_lines_before_table}\baselineskip}}}}
\BeforeBeginEnvironment{{longtable}}{{\needspace{{{t.min_lines_before_longtable}\baselineskip}}}}
"""


def caption_setup() -> str:
    """Caption formatting shared by tables and figures."""
    ty = TYPOGRAPHY
    return rf"""\captionsetup{{
    labelfont={ty.caption_label_font},
    justification={ty.caption_justification},
    singlelinecheck=false,
    format=plain,
    aboveskip={ty.caption_skip},
    belowskip={ty.caption_skip}
}}
\newcommand{{\tablesmallfont}}{{{ty.table_small_font}}}"""


def heading_formats() -> str:
    """Chapter heading and table of contents layout."""
    ty = TYPOGRAPHY
    # Each TOC level is indented by the previous level's indent plus its
    # number width, so section and subsection numbers line up in columns.
    return rf"""\titleformat{{\chapter}}[block]
  {{\normalfont{ty.chapter_title}\centering}}{{\thechapter}}{{1em}}{{}}
\titlespacing*{{\chapter}}{{0pt}}{{{ty.chapter_title_before}}}{{{ty.chapter_title_after}}}
\setcounter{{tocdepth}}{{{ty.toc_depth}}}

\titlecontents{{chapter}}[1.5em]
  {{\normalfont\vspace{{2pt}}}}
  {{\contentslabel{{1.5em}}}}
  {{\hspace*{{-1.5em}}}}
  {{\hfill\contentspage}}

\titlecontents{{section}}[3.8em]
  {{\normalfont}}
  {{\contentslabel{{2.3em}}}}
  {{\hspace*{{-2.3em}}}}
  {{\hfill\contentspage}}

\titlecontents{{subsection}}[7.0em]
  {{\normalfont}}
  {{\contentslabel{{3.2em}}}}
  {{\hspace*{{-3.2em}}}}
  {{\hfill\contentspage}}

\renewcommand{{\contentsname}}{{\centering{ty.toc_title} Table of Contents}}"""


def _rule() -> str:
    return rf"\color{{osdagGreen}}\hrule width \headwidth height {HEADER_FOOTER.rule_thickness}"


def page_styles(header_left: str, header_right: str) -> str:
    """fancyhdr styles for body pages (``main``, ``plain``) and the title page.

    ``header_left`` and ``header_right`` must already be LaTeX-escaped.
    """
    hf = HEADER_FOOTER
    footer = rf"""  \fancyfoot[L]{{{hf.footer_left}}}
  \fancyfoot[R]{{{hf.page_label}}}"""
    # On pages that print a software default value (flagged by \markSD in the
    # preamble), the explanatory note is set just above the footer rule.
    body = rf"""  \fancyhf{{}}
  \fancyhead[L]{{{header_left}}}
  \fancyhead[R]{{{header_right}}}
{footer}
  \renewcommand{{\headrule}}{{{_rule()} \vspace{{2pt}}}}
  \renewcommand{{\footrule}}{{%
    \ifbool{{hasSDonPage}}{{%
      \vspace{{-20pt}}%
      \hbox to \headwidth{{\textcolor{{black}}{{\footnotesize\textit{{{hf.default_value_note}}}}}\hfil}}%
      \vspace{{4pt}}%
    }}{{%
      \vspace{{-8pt}}%
    }}%
    {_rule()} \vspace{{6pt}}%
  }}"""
    return rf"""\fancypagestyle{{main}}{{
{body}
}}
\fancypagestyle{{plain}}{{
{body}
}}
\fancypagestyle{{firstpage}}{{
  \fancyhf{{}}
  \renewcommand{{\headrulewidth}}{{0pt}}
{footer}
  \renewcommand{{\footrule}}{{\vspace{{-8pt}}{_rule()} \vspace{{6pt}}}}
}}
\pagestyle{{main}}
\setstretch{{{PAGE.line_stretch}}}"""
