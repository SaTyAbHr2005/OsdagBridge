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
    # Tall enough for the running header and its rule; fancyhdr warns and
    # shifts the header on every page when it is smaller.
    head_height: str = "18pt"
    # Distance from the last text line to the footer baseline. It leaves room
    # for the software-default note above the footer rule (see page_styles)
    # while keeping both clear of a table ending at the bottom of the page.
    foot_skip: str = "42pt"
    line_stretch: float = 1.15


@dataclass(frozen=True)
class Palette:
    # HTML hex values without the leading '#', as expected by xcolor.
    brand: str = "91B014"
    # 15% tint of the brand green: marks header rows without competing
    # with the PASS/FAIL colours in the table body.
    table_header: str = "EEF3DC"
    # Both at least 4.5:1 against white for small table text; FAIL is also
    # set bold so it still stands out in black-and-white print.
    status_pass: str = "1E7B34"
    status_fail: str = "D0312D"
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
    # Cell padding: extra_row_height is added above the text of every row,
    # row_pad below a row that ends in \\[\rowpad]. array measures that gap
    # from the first line, so it only shows on single-line rows; the two are
    # balanced so single-line text sits near the middle of its row.
    row_pad: str = "4.5pt"
    row_pad_wide: str = "6.5pt"
    # One width for every table rule. 0.75pt is one screen pixel at 100% zoom;
    # thinner rules are drawn as full, faint or missing pixels depending on
    # where they fall, so equal rules look unequal when zoomed out.
    rule_width: str = "0.75pt"
    extra_row_height: str = "2pt"
    # Gap \tallcell keeps between a formula taller than a text line and the
    # rule above it.
    min_row_clearance: str = "3pt"
    # Space above and below every longtable; the caption already separates
    # a table from the paragraph before it.
    longtable_pre: str = "0pt"
    longtable_post: str = "6pt"
    # A float table starting with fewer lines than this left on the page
    # moves to the next page instead of leaving its caption stranded.
    # Longtables handle their own start-of-table page break; a \needspace
    # before them adds a break point that can separate the table from its
    # first page and strand the "Continued" foot.
    min_lines_before_table: int = 5
    # A table with this many rows or fewer moves to the next page whole
    # instead of splitting.
    keep_whole_rows: int = 6
    # Labels on tables that break across pages.
    continued_caption: str = "(continued)"
    continued_note: str = r"\small\itshape Continued on next page"


@dataclass(frozen=True)
class SpacingScale:
    # Vertical gaps between blocks of content, smallest first.
    line: str = "3pt"       # between lines inside one boxed block
    small: str = "0.4em"    # a heading or note directly attached to a table
    block: str = "1em"      # paragraph or table followed by another table
    section: str = "2em"    # start of a new group within a section


@dataclass(frozen=True)
class FigureStyle:
    plot_width: str = r"0.75\textwidth"        # analysis plots (Chapter 4)
    summary_width: str = r"0.9\textwidth"      # executive summary views
    drawing_width: str = r"0.85\textwidth"     # single drawings (Chapter 6)
    grid_cell_width: str = r"0.31\textwidth"   # three drawings side by side
    grid_image_height: str = "3.5cm"           # tallest a side-by-side drawing may be
    placeholder_width: str = r"0.97\textwidth"
    gap_before_drawing: str = "4pt"
    # Plots carry their own whitespace margin, so the gaps around them are
    # pulled in slightly to keep plot and caption visually together.
    plot_gap_outer: str = "-0.5em"
    plot_gap_caption: str = "0.5em"
    plot_caption_size: str = r"\small"
    chart_width: str = r"0.95\textwidth"       # summary bar charts


@dataclass(frozen=True)
class ChartStyle:
    # Bar charts drawn with matplotlib for the summary sections. The pass
    # and fail colours stay distinguishable under red-green colour
    # blindness; failing bars are also hatched and labelled FAIL so the
    # charts still read in greyscale print.
    pass_bar: str = "2F6DB5"
    fail_bar: str = "D0312D"
    limit_line: str = "D0312D"
    quantity_bar: str = "2F6DB5"   # material quantities (no pass/fail meaning)
    text: str = "333333"
    grid: str = "D9D9D9"
    # Close to FigureStyle.chart_width on the page, so the font prints at
    # about font_size.
    width_in: float = 6.0
    bar_row_in: float = 0.34    # height added per bar (horizontal bar charts)
    frame_in: float = 0.75      # axis labels and margins
    column_height_in: float = 3.0   # utilization charts: UR on the vertical axis
    label_wrap_chars: int = 10      # element names under a column wrap at this width
    font_size: float = 10.0
    dpi: int = 200


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
    page_label: str = r"Page \thepage\osdagpagetotal"
    rule_thickness: str = "1pt"
    default_value_note: str = r"* Software default value"


PAGE = PageStyle()
COLORS = Palette()
TABLE = TableStyle()
SPACING = SpacingScale()
FIGURE = FigureStyle()
CHART = ChartStyle()
TYPOGRAPHY = Typography()
TITLE_PAGE = TitlePageStyle()
HEADER_FOOTER = HeaderFooterStyle()


_PAPER_WIDTH_CM = {"a4paper": 21.0, "a3paper": 29.7, "letterpaper": 21.59, "legalpaper": 21.59}
_UNIT_CM = {"cm": 1.0, "mm": 0.1, "in": 2.54, "pt": 2.54 / 72.27}


def length_cm(value: str) -> float:
    """Convert a LaTeX length such as ``1in``, ``4pt`` or ``2.5cm`` to centimetres."""
    for unit, factor in _UNIT_CM.items():
        if value.endswith(unit):
            return float(value[: -len(unit)]) * factor
    raise ValueError(f"Unsupported length: {value!r}")


def text_width_cm() -> float:
    """Width of the text block, i.e. the widest a table may be."""
    if PAGE.paper not in _PAPER_WIDTH_CM:
        raise ValueError(f"No paper width defined for {PAGE.paper!r}; add it to _PAPER_WIDTH_CM")
    return (_PAPER_WIDTH_CM[PAGE.paper]
            - length_cm(PAGE.margin_left) - length_cm(PAGE.margin_right))


def document_class() -> str:
    """``\\documentclass`` line with the base font size and paper."""
    return rf"\documentclass[{PAGE.font_size},{PAGE.paper}]{{report}}"


def geometry_package() -> str:
    """``geometry`` package line with the page margins."""
    return (
        rf"\usepackage[{PAGE.paper}, top={PAGE.margin_top}, bottom={PAGE.margin_bottom}, "
        rf"left={PAGE.margin_left}, right={PAGE.margin_right}, "
        rf"headheight={PAGE.head_height}, footskip={PAGE.foot_skip}]{{geometry}}"
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
% Header row shading. colortbl paints a cell's fill after the rules above and
% to the left of it, and PDF viewers round fills out to whole screen pixels,
% so a fill that touches a rule paints over part of it and the rule looks
% thinner than the others at screen zoom. The fill therefore stops one rule
% width short of the vertical rules and, in the first header row, of the rule
% above. Every rule is drawn once and nothing is painted over it.
% \tableheadernext shades a second header row; it fills to the top so a cell
% that spans both rows (\multirow) stays one colour.
\colorlet{{tableHeaderTop}}{{tableHeader}}
\makeatletter
% colortbl stores the row colour as \CT@color{{name}} followed by the
% overhang widths; #2 is the colour name.
\def\osdag@toprowheight#1#2#3\@nil{{%
  \ifnum\pdfstrcmp{{#2}}{{tableHeaderTop}}=\z@\@height\dimexpr\ht\@arstrutbox-\arrayrulewidth\relax\fi}}
\patchcmd{{\CT@@do@color}}{{\leaders\vrule}}
  {{\leaders\vrule\ifx\CT@row@color\relax\else\expandafter\osdag@toprowheight\CT@row@color\@nil\fi}}
  {{}}{{\PackageWarning{{osdagbridge}}{{Header fill could not be patched}}}}
\makeatother
\newcommand{{\tableheader}}{{\rowcolor{{tableHeaderTop}}[\dimexpr\tabcolsep-\arrayrulewidth\relax][\dimexpr\tabcolsep-\arrayrulewidth\relax]}}
\newcommand{{\tableheadernext}}{{\rowcolor{{tableHeader}}[\dimexpr\tabcolsep-\arrayrulewidth\relax][\dimexpr\tabcolsep-\arrayrulewidth\relax]}}
% longtable draws every \hline twice, one copy on each side of a page-break
% point. The overlapping copies render darker than the vertical rules and
% \cline at screen zoom. Draw the rule once with the break point after it;
% \hlinenobreak, used after a row ending in \\*, leaves the break point out.
\makeatletter
\def\osdag@LTbreak@default{{\penalty-\@lowpenalty}}
\let\osdag@LTbreak\osdag@LTbreak@default
\def\osdag@LTnobreak{{\penalty\@M}}
\newcommand{{\hlinenobreak}}{{\noalign{{\global\let\osdag@LTbreak\osdag@LTnobreak}}\hline}}
\AtBeginDocument{{\def\LT@@hline{{\ifnum0=`{{\fi}}%
  \multispan\LT@cols{{\CT@arc@\leaders\hrule\@height\arrayrulewidth\hfill}}\cr
  \noalign{{\osdag@LTbreak\global\let\osdag@LTbreak\osdag@LTbreak@default}}}}}}
\makeatother
% A heading must stay with the longtable under it. LaTeX marks the spot
% right after a heading (\if@nobreak), but the first paragraph inside a
% table cell clears that flag before longtable decides on its first page
% break, so the flag is recorded when the table begins. After a heading the
% table start adds no break point, and when the first rows do not fit,
% the needed height is added as glue that takes itself back, so TeX breaks
% before the heading instead of under it.
\makeatletter
\newif\ifosdag@afterhead
\AtBeginEnvironment{{longtable}}{{\if@nobreak\global\osdag@afterheadtrue\else\global\osdag@afterheadfalse\fi}}
\AtBeginDocument{{\apptocmd{{\label}}{{\ifvmode\if@nobreak\nobreak\fi\fi}}{{}}
  {{\PackageWarning{{osdagbridge}}{{\string\label\space could not be patched}}}}}}
\ExplSyntaxOn
\patchcmd{{\LT@start}}{{\endgraf\penalty\z@}}
  {{\endgraf\ifosdag@afterhead\nobreak\else\penalty\z@\fi}}{{}}
  {{\PackageWarning{{osdagbridge}}{{longtable~start~break~could~not~be~patched}}}}
\patchcmd{{\LT@start}}{{\vfil\break}}
  {{\ifosdag@afterhead
     \advance\dimen@\pagegoal\advance\dimen@-\pagetotal
     \nobreak\vskip\dimen@\penalty9999\vskip-\dimen@
   \else\vfil\break\fi}}{{}}
  {{\PackageWarning{{osdagbridge}}{{longtable~page~check~could~not~be~patched}}}}
\patchcmd{{\LT@start}}{{\ifvoid\LT@firsthead\copy\LT@head}}
  {{\ifosdag@afterhead\nobreak\fi\ifvoid\LT@firsthead\copy\LT@head}}{{}}
  {{\PackageWarning{{osdagbridge}}{{longtable~head~could~not~be~patched}}}}
\ExplSyntaxOff
\makeatother
\newcommand{{\statuspass}}[1]{{\textcolor{{statusPass}}{{#1}}}}
\newcommand{{\statusfail}}[1]{{\textcolor{{statusFail}}{{\textbf{{#1}}}}}}

\setlength{{\tabcolsep}}{{{t.col_sep}}}
\renewcommand{{\arraystretch}}{{{t.array_stretch}}}
\setlength{{\LTleft}}{{\fill}}
\setlength{{\LTright}}{{\fill}}
\setlength{{\LTpre}}{{{t.longtable_pre}}}
\setlength{{\LTpost}}{{{t.longtable_post}}}
\setlength{{\arrayrulewidth}}{{{t.rule_width}}}
\setlength{{\extrarowheight}}{{{t.extra_row_height}}}
% A cell taller than a text line (a square root, a stacked fraction) sits
% against the rule above it; \tallcell keeps a gap between them.
\newsavebox{{\tallcellbox}}
\newcommand{{\tallcell}}[1]{{\sbox{{\tallcellbox}}{{#1}}%
  \rule{{0pt}}{{\dimexpr\ht\tallcellbox+{t.min_row_clearance}\relax}}\usebox{{\tallcellbox}}}}

\newlength{{\rowpad}}\setlength{{\rowpad}}{{{t.row_pad}}}
\newlength{{\rowpadwide}}\setlength{{\rowpadwide}}{{{t.row_pad_wide}}}
\newlength{{\gapline}}\setlength{{\gapline}}{{{SPACING.line}}}
\newlength{{\gapsmall}}\setlength{{\gapsmall}}{{{SPACING.small}}}
\newlength{{\tablegap}}\setlength{{\tablegap}}{{{SPACING.block}}}
\newlength{{\sectiongap}}\setlength{{\sectiongap}}{{{SPACING.section}}}
\newlength{{\colseptight}}\setlength{{\colseptight}}{{{t.col_sep_tight}}}
\newlength{{\colsepdense}}\setlength{{\colsepdense}}{{{t.col_sep_dense}}}
\newcommand{{\densearraystretch}}{{{t.array_stretch_dense}}}
\newcommand{{\tablecontinuednote}}{{{t.continued_note}}}

% Partial rule between the rows of one group (one girder, one bracing pair).
% \cline allows a page break right after it; this copy does not, so a group
% whose rows end in \\* stays on one page.
\makeatletter
\let\osdag@groupcline\@cline
\patchcmd{{\osdag@groupcline}}{{\vskip-\arrayrulewidth}}{{\nobreak\vskip-\arrayrulewidth}}{{}}
  {{\PackageWarning{{osdagbridge}}{{\string\groupcline\space could not be patched}}}}
\newcommand{{\groupcline}}[1]{{\osdag@groupcline#1\@nil}}
\makeatother

\BeforeBeginEnvironment{{table}}{{\needspace{{{t.min_lines_before_table}\baselineskip}}}}
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


def front_matter() -> str:
    """Roman page numbers without a total for the contents and lists."""
    return r"\pagenumbering{roman}\renewcommand{\osdagpagetotal}{}"


def main_matter() -> str:
    """Arabic page numbers from 1, with "of N" counting these pages only."""
    return r"\pagenumbering{arabic}\renewcommand{\osdagpagetotal}{\ of \pageref{LastPage}}"


def _rule() -> str:
    return rf"\color{{osdagGreen}}\hrule width \headwidth height {HEADER_FOOTER.rule_thickness}"


def page_styles(header_left: str, header_right: str) -> str:
    """fancyhdr styles for body pages (``main``, ``plain``) and the title page.

    ``header_left`` and ``header_right`` must already be LaTeX-escaped.
    """
    hf = HEADER_FOOTER
    # On pages that print a software default value (flagged by \markSD in the
    # preamble) the explanatory note sits just above the footer rule, right
    # aligned; foot_skip leaves room for it below the text block.
    rule = rf"""\renewcommand{{\footrule}}{{\vspace{{-8pt}}\ifbool{{hasSDonPage}}{{\hbox to\headwidth{{\hfill
    \footnotesize\itshape\color{{gray}}{hf.default_value_note}}}\vspace{{2pt}}}}{{}}{_rule()}}}"""
    footer = rf"""  \fancyfoot[L]{{{hf.footer_left}}}
  \fancyfoot[R]{{{hf.page_label}}}
  {rule}"""
    # The title page carries no page number.
    title_footer = rf"""  \fancyfoot[L]{{{hf.footer_left}}}
  {rule}"""
    body = rf"""  \fancyhf{{}}
  \fancyhead[L]{{{header_left}}}
  \fancyhead[R]{{{header_right}}}
{footer}
  \renewcommand{{\headrule}}{{{_rule()} \vspace{{2pt}}}}"""
    # Front matter pages show "Page iii"; main_matter() adds "of N" from the
    # Executive Summary on, where N is the last arabic page.
    return rf"""\newcommand{{\osdagpagetotal}}{{\ of \pageref{{LastPage}}}}
\fancypagestyle{{main}}{{
{body}
}}
\fancypagestyle{{plain}}{{
{body}
}}
\fancypagestyle{{firstpage}}{{
  \fancyhf{{}}
  \renewcommand{{\headrulewidth}}{{0pt}}
{title_footer}
}}
\pagestyle{{main}}
\setstretch{{{PAGE.line_stretch}}}"""
