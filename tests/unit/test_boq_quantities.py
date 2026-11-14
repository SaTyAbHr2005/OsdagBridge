"""Bill of materials: end diaphragm members and crash barrier volume."""

import math

import pytest

from osdagbridge.core.boq.boq_generator import calculate_material_quantities, end_diaphragm_quantities
from osdagbridge.core.utils.common import KEY_SPAN, KEY_TS_GIRDER_SPACING, KEY_TS_NO_OF_GIRDERS

ED = "member_properties.end_diaphragm_details."
DEPTH = "member_properties.girder_details.section_input.depth"


def _bracing_pair(index, end):
    key = f".G{index}G{index + 1}.E{index}{end}"
    return {ED + "type" + key: "Cross Bracing", ED + "section_properties.area" + key: "19.1",
            ED + "bracing_section" + key: "Double Angle (Long Leg)", ED + "bracing_type" + key: "X-Bracing",
            ED + "top_chord" + key: "Yes", ED + "bottom_chord" + key: "Yes",
            ED + "top_chord_section_type" + key: "Double Angle (Long Leg)",
            ED + "bottom_chord_section_type" + key: "Double Angle (Long Leg)"}


def test_cross_bracing_end_diaphragms_match_hand_calculation():
    inputs = {KEY_TS_NO_OF_GIRDERS: "4", KEY_TS_GIRDER_SPACING: "2.1", DEPTH: "1.67"}
    for i in (1, 2, 3):
        inputs.update(_bracing_pair(i, "M1"))
        inputs.update(_bracing_pair(i, "M2"))
    rows = {r["label"]: r for r in end_diaphragm_quantities(inputs)}
    area = 2 * 19.1e-4                                  # double angle, m2
    diagonal = math.hypot(2.1, 0.85 * 1.67)             # X bracing over 0.85 x girder depth
    # 3 pairs x 2 supports, 2 diagonals and 2 chords each.
    assert rows["End Diaphragm - Diagonals"]["qty"] == "12"
    assert rows["End Diaphragm - Diagonals"]["weight_t"] == pytest.approx(12 * area * diagonal * 7.85)
    assert rows["End Diaphragm - Chords"]["weight_t"] == pytest.approx(12 * area * 2.1 * 7.85)


def test_end_without_its_own_values_shares_the_other_end():
    inputs = {KEY_TS_NO_OF_GIRDERS: "2", KEY_TS_GIRDER_SPACING: "2.5",
              ED + "type.G1G2.E1M1": "Rolled Beam", ED + "section_properties.area.G1G2.E1M1": "100"}
    (row,) = end_diaphragm_quantities(inputs)
    assert row["qty"] == "2"                            # one beam at each support
    assert row["weight_t"] == pytest.approx(2 * 0.01 * 2.5 * 7.85)


def test_quantity_times_unit_weight_equals_total_for_each_row():
    inputs = {KEY_TS_NO_OF_GIRDERS: "3", KEY_TS_GIRDER_SPACING: "2.0",
              ED + "type.G1G2.E1M1": "Rolled Beam", ED + "section_properties.area.G1G2.E1M1": "100",
              ED + "type.G2G3.E2M1": "Rolled Beam", ED + "section_properties.area.G2G3.E2M1": "50"}
    rows = end_diaphragm_quantities(inputs)
    assert len(rows) == 2                               # two sizes, two rows
    for row in rows:
        assert int(row["qty"]) * float(row["wt_single"]) == pytest.approx(row["weight_t"], abs=1e-3)


def test_no_inputs_give_no_rows():
    assert end_diaphragm_quantities({}) == []


@pytest.mark.parametrize("area", ["0.3023", "302300"])   # m2 from the form, mm2 from the defaults
def test_crash_barrier_volume(area):
    q = calculate_material_quantities({KEY_SPAN: "30", KEY_TS_NO_OF_GIRDERS: "4",
                                       "typical_section.crash_barrier.area": area}, {})
    assert q["crash_barrier_vol_total"] == "18.14"      # 2 barriers x 0.3023 m2 x 30 m
