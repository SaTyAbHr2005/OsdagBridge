from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS
)
from pylatex import Command, Figure, NoEscape
from pylatex.figure import StandAloneGraphic

from .styles import FIGURE
from .tables import dumps


def _tex(value):
    """Escape a Python value for safe LaTeX embedding."""
    s = str(value) if value is not None else ''
    if not s:
        return r''
    # Normalise non-ASCII glyphs from section designations (e.g. "∠ 100 ⅹ 100ⅹ 10")
    # that pdflatex cannot render.
    for uni, ascii_ in [('∠', 'L'), ('ⅹ', 'x'), ('×', 'x')]:
        s = s.replace(uni, ascii_)
    s = s.replace('\\', r'\textbackslash{}')
    for ch, esc in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
                    ('{', r'\{'), ('}', r'\}'),          
                    ('_', r'\_\allowbreak{}'),            
                    ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        s = s.replace(ch, esc)
    # Check names from the design modules use these signs; pdflatex stops
    # with an error on them as text, so they go in as math.
    s = s.replace('≤', r'$\le$').replace('≥', r'$\ge$')
    s = s.replace(':', r':\allowbreak{}')
    return s


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    if isinstance(val, float):
        # Computed widths such as 15.649999999999999 print as 15.65; values
        # without that floating-point noise are unchanged.
        val = round(val, 6)
    return _tex(val) + unit


def get_girder_entries(input_dict):
    """
    Retrieve all girder labels and member IDs from backend keys.

    Usage Example:
    --------------------------
    girder_entries = get_girder_entries(bridge.input_dict)
    
    # 1. Fallback handling (if backend hasn't populated keys yet)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1))
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
        
    # 2. Get total number of girders safely
    n_girders = len(girder_entries)
    
    # 3. Iterate over the girders to build table rows
    for lbl, mid in girder_entries:
        # lbl will be e.g., "G1", mid will be e.g., "G1M1"
        # Access girder specific keys dynamically:
        # val = input_dict.get(f"{KEY_MP_GIRDER_DEPTH}.{lbl}.{mid}")
        pass

    Returns:
        List[Tuple[str, str]]
    """
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))

    entries = []

    for i in range(1, n + 1):
        entries.append(
            (
                input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", ""),
                input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", ""),
            )
        )

    return entries


def _placeholder(caption):
    """Framed box standing in for a figure whose image is missing."""
    return NoEscape(r'\fbox{\parbox{' + FIGURE.placeholder_width + '}{' + '\n'
                    r'\textit{[ PLACEHOLDER: ' + caption + r' ]}' + '\n' r'}}')


def _image(path, options):
    """\\includegraphics for an image already copied into the build folder."""
    return StandAloneGraphic(filename=NoEscape(path.replace('\\', '/')), image_options=NoEscape(options))


def _fig_or_placeholder(path, caption, width=FIGURE.summary_width):
    """PyLaTeX Figure of an image with an unnumbered caption, or a placeholder box.
    path is the path as pdflatex will see it (e.g. 'assets/plan.png').
    """
    fig = Figure(position='H')
    fig.append(NoEscape(r'\centering'))
    fig.append(_image(path, 'width=' + width) if path else _placeholder(caption))
    fig.append(Command('caption*', NoEscape(caption)))
    return dumps(fig)


def _fig_embed(path, caption, width=FIGURE.plot_width, height=None):
    """PyLaTeX Figure of a plot or chart with a numbered caption; a placeholder box when path is empty."""
    if not path:
        return r'\noindent' + _placeholder(caption)
    opts = 'width=' + width
    if height:
        opts += ',height=' + height + ',keepaspectratio'
    gap_outer = Command('vspace', NoEscape(FIGURE.plot_gap_outer))
    fig = Figure(position='H')
    fig.append(gap_outer)
    fig.append(NoEscape(r'\centering'))
    fig.append(_image(path, opts))
    fig.append(Command('vspace', NoEscape(FIGURE.plot_gap_caption)))
    # Numbered so the plot is listed in the List of Figures; the list takes
    # the title up to the first colon.
    fig.append(Command('caption', NoEscape(FIGURE.plot_caption_size + ' ' + caption),
                       options=NoEscape('{' + caption.split(':')[0] + '}')))
    fig.append(gap_outer)
    return dumps(fig)


