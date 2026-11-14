"""Executive summary verdict, load case order and readable labels."""

import random

from osdagbridge.core.reports.chap3 import _wearing_course_load
from osdagbridge.core.reports.chap8 import design_log_chapter
from osdagbridge.core.reports.chap4 import _load_case_order
from osdagbridge.core.reports.executive_summary import _deck_check_name, _readable_check, executive_summary
from osdagbridge.core.utils.common import (
    KEY_TS_NO_OF_GIRDERS, KEY_WC_DENSITY, KEY_WC_MATERIAL, KEY_WC_THICKNESS,
)


def _check(name, dcr, status):
    return {"name": name, "dcr": dcr, "status": status}


def _summary(per_girder, n_girders="4"):
    return executive_summary({KEY_TS_NO_OF_GIRDERS: n_girders},
                             {"design_results": {"per_girder": per_girder}}, {})


def test_every_failing_girder_is_listed_and_edge_lines_are_ignored():
    tex = _summary({
        "G1": {"checks": [_check("Fatigue Normal Stress", 1.54, "FAIL")]},
        "G2": {"checks": [_check("Fatigue Normal Stress", 1.55, "FAIL"), _check("ULS Flexure", 0.4, "PASS")]},
        "G3": {"checks": [_check("ULS Flexure", 1.2, "FAIL")]},
        # Edge-beam grillage lines carry results too but are not girders of the bridge.
        "G5": {"checks": [_check("Fatigue Normal Stress", 3.0, "FAIL")]},
    })
    box = tex[tex.index("Critical Checks"):tex.index(r"\end{minipage}")]
    assert "Fatigue Normal Stress & G1, G2 & \\statusfail{1.55}" in box
    assert "ULS Flexure & G3 & \\statusfail{1.20}" in box
    assert "G5" not in box and "3.00" not in tex


def test_passing_design_gets_a_pass_verdict():
    tex = _summary({"G1": {"checks": [_check("ULS Flexure", 0.5, "PASS")]}}, n_girders="1")
    assert r"Design verdict: \statuspass{PASS}" in tex
    assert "All design checks pass." in tex


def test_load_cases_sort_the_same_whatever_the_input_order():
    names = ["SLS_QP_2: a", "BASIC_10: b", "Envelope SLS", "DD", "BASIC_2: c", "SW",
             "Envelope ULS", "SEISMIC_1: d", "WL Uplift"]
    expected = ["SW", "DD", "WL Uplift", "BASIC_2: c", "BASIC_10: b", "SEISMIC_1: d",
                "SLS_QP_2: a", "Envelope ULS", "Envelope SLS"]
    for _ in range(5):
        random.shuffle(names)
        assert sorted(names, key=_load_case_order) == expected


def test_check_names_are_spelled_out():
    assert _readable_check("Int.Stiff: Leg ≤ H_limit") == "Intermediate stiffener outstand (IRC 22 Cl. 509.7.2.4)"
    assert _readable_check("Brg.Stiff: Web Buckling") == "Bearing stiffener web buckling"
    assert _readable_check("ULS Flexure") == "ULS Flexure"
    assert _deck_check_name("ur_oh_crack") == "Deck slab (overhang): crack width"


def test_wearing_course_load_gives_the_surface_load():
    text = _wearing_course_load({KEY_WC_MATERIAL: "Concrete", KEY_WC_THICKNESS: 50.0, KEY_WC_DENSITY: 24.0})
    assert text.startswith("Concrete, 50 mm thick at 24 kN/m") and text.endswith("= 1.20 kN/m\\textsuperscript{2}")
    assert _wearing_course_load({KEY_WC_MATERIAL: "Concrete", KEY_WC_THICKNESS: "nan", KEY_WC_DENSITY: 24}) == "Concrete"


def test_design_log_lists_every_line_coloured_by_level():
    tex = design_log_chapter(["[10:00:01]   Stage 1 complete\n\n[10:00:02]   WARNING : wide overhang"])
    assert tex.count(r"\par") == 2
    assert r"\textcolor{statusPass}{[10:" in tex
    assert r"\textcolor{logWarning}{[10:" in tex
    assert design_log_chapter([]) == ""
