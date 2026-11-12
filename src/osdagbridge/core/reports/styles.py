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
    min_lines_before_break: int = 5


@dataclass(frozen=True)
class SpacingScale:
    # Vertical gaps between blocks of content, smallest first.
    small: str = "0.4em"    # a heading or note directly attached to a table
    block: str = "1em"      # paragraph or table followed by another table
    section: str = "2em"    # start of a new group within a section


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
HEADER_FOOTER = HeaderFooterStyle()


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

\BeforeBeginEnvironment{{table}}{{\needspace{{{t.min_lines_before_break}\baselineskip}}}}
\BeforeBeginEnvironment{{longtable}}{{\needspace{{{t.min_lines_before_break}\baselineskip}}}}
"""


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
