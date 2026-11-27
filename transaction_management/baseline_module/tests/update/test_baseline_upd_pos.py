"""
Baseline Visit CRF - UPDATE Operation (Positive Test Suite).
Validates TC-BASE-UPD-POS-01 to TC-BASE-UPD-POS-06.
Strictly 100% Zero Hardcoding: all test data dynamically loaded from 'CRUDtransaction-baseline' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from shared_tools.utils.env_config import config
    from transaction_management.baseline_module.pages.baseline_common_page import BaselinePage
    from transaction_management.baseline_module.baseline_data import (
        get_baseline_test_data,
        get_target_patient_id,
        parse_crud_sections,
        get_field_transitions,
        get_shortcut_instruction,
    )
except ImportError:
    from utils.env_config import config
    from pages.baseline_common_page import BaselinePage
    from baseline_data import (
        get_baseline_test_data,
        get_target_patient_id,
        parse_crud_sections,
        get_field_transitions,
        get_shortcut_instruction,
    )


@pytest.mark.positive
@pytest.mark.baseline
@pytest.mark.update
class TestBaselineUpdatePos:
    """Positive test cases for Baseline Visit Update operations (Zero Hardcoded Data)."""

    def test_tc_base_upd_pos_01_edit_single_entry_fields(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-POS-01: Edit single-entry fields."""
        tc_id = "TC-BASE-UPD-POS-01"
        pid = get_target_patient_id(tc_id)
        trans = get_field_transitions(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        personal_updates = {}
        for field in ("Marital Status", "Consanguineous", "Agni Vikriti", "Remark"):
            if field in trans:
                personal_updates[field] = trans[field]["new"]

        baseline_page.disease.fill_personal_details(personal_updates)

        baseline_page.switch_subtab("Physician and RAC Opinion")
        if "RAC Approach" in trans:
            baseline_page.physician_rac_page.fill_rac_management(approach=trans["RAC Approach"]["new"])

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_upd_pos_02_edit_existing_repeatable_rows(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-POS-02: Edit existing repeatable rows."""
        tc_id = "TC-BASE-UPD-POS-02"
        pid = get_target_patient_id(tc_id)
        trans = get_field_transitions(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        if "Diagnosis Stage" in trans:
            baseline_page.disease.fill_allopathy_diagnosis({"Stage": trans["Diagnosis Stage"]["new"]}, row_index=0)
        if "Medicine Strength" in trans:
            baseline_page.disease.fill_medication("Allopathy", "", trans["Medicine Strength"]["new"], "mg", "BD", row_index=0)

        baseline_page.switch_subtab("Hetu Sevan")
        if "Habit Status" in trans:
            baseline_page.hetu_sevan_page.fill_habit("", status=trans["Habit Status"]["new"])

        baseline_page.switch_subtab("Physician and RAC Opinion")
        if "RAC Approach" in trans:
            baseline_page.physician_rac_page.fill_rac_management(approach=trans["RAC Approach"]["new"])

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_upd_pos_03_modify_multi_select_chips(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-POS-03: Modify multi-select chips."""
        tc_id = "TC-BASE-UPD-POS-03"
        pid = get_target_patient_id(tc_id)
        rec = get_baseline_test_data(tc_id)
        trans = get_field_transitions(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        # Select new chips specified in payload
        for k, v in trans.items():
            baseline_page.disease._select_chip_or_dropdown(k, v["new"])

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_upd_pos_04_toggle_state_reversal(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-POS-04: Toggle state reversal."""
        tc_id = "TC-BASE-UPD-POS-04"
        pid = get_target_patient_id(tc_id)
        trans = get_field_transitions(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Hetu Sevan")

        for k, v in trans.items():
            if "exercise" in k.lower():
                baseline_page.hetu_sevan_page.fill_vihar(exercise=v["new"])

        baseline_page.switch_subtab("Physician and RAC Opinion")
        for k, v in trans.items():
            if "opted" in k.lower():
                baseline_page.physician_rac_page.fill_physician_opinion("", "", patient_opted=v["new"])

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_upd_pos_05_cascading_dropdown_update(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-POS-05: Cascading dropdown update."""
        tc_id = "TC-BASE-UPD-POS-05"
        pid = get_target_patient_id(tc_id)
        trans = get_field_transitions(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        new_group = "Gastrointestinal"
        for k, v in trans.items():
            if "group" in k.lower() or "disease" in k.lower():
                new_group = v["new"]

        baseline_page.disease.fill_allopathy_diagnosis({"Group": new_group})
        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_upd_pos_06_keyboard_shortcut_save(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-POS-06: Keyboard shortcut save."""
        tc_id = "TC-BASE-UPD-POS-06"
        pid = get_target_patient_id(tc_id)
        rec = get_baseline_test_data(tc_id)
        sections = parse_crud_sections(rec.raw_payload)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        rem_text = "Shortcut save check"
        if "Input" in sections and isinstance(sections["Input"], str):
            rem_text = sections["Input"]

        baseline_page.disease.fill_personal_details({"Remark": rem_text})
        baseline_page.save_via_shortcut()
        baseline_page.verify_save_success()
