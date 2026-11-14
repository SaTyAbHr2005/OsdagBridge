"""Report style module: the LaTeX it emits and the page measurements it computes."""

from osdagbridge.core.reports import styles


def test_text_width_is_paper_width_less_margins():
    # A4 (21 cm) with 1 in margins on both sides.
    assert abs(styles.text_width_cm() - (21.0 - 2 * 2.54)) < 1e-6


def test_length_cm_converts_units():
    assert styles.length_cm("1in") == 2.54
    assert styles.length_cm("10mm") == 1.0
    assert abs(styles.length_cm("72.27pt") - 2.54) < 1e-9


def test_definitions_provide_the_macros_chapters_use():
    tex = styles.latex_definitions()
    for macro in (r"\rowpad", r"\tablegap", r"\statuspass", r"\statusfail",
                  r"\tableheader", r"\groupcline"):
        assert macro in tex, macro


def test_status_colours_come_from_the_palette():
    tex = styles.latex_definitions()
    assert styles.COLORS.status_pass in tex
    assert styles.COLORS.status_fail in tex
    # FAIL is bold as well as coloured, so it survives greyscale printing.
    assert r"\textbf{#1}" in tex


def test_geometry_sets_header_and_footer_space():
    tex = styles.geometry_package()
    assert "headheight=" + styles.PAGE.head_height in tex
    assert "footskip=" + styles.PAGE.foot_skip in tex


def test_page_styles_put_header_text_and_page_label_in_place():
    tex = styles.page_styles("Project", "2026-01-01")
    assert r"\fancyhead[L]{Project}" in tex
    assert r"\fancyhead[R]{2026-01-01}" in tex
    assert styles.HEADER_FOOTER.page_label in tex
