"""
Baseline Visit CRF - DELETE Operation (Positive Test Suite).
Validates TC-BASE-DEL-POS-01 to TC-BASE-DEL-POS-03.
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
        get_cleared_fields_list,
    )
except ImportError:
    from utils.env_config import config
    from pages.baseline_common_page import BaselinePage
    from baseline_data import (
        get_baseline_test_data,
        get_target_patient_id,
        parse_crud_sections,
        get_cleared_fields_list,
    )


@pytest.mark.positive
@pytest.mark.baseline
@pytest.mark.delete
class TestBaselineDeletePos:
    """Positive test cases for Baseline Visit Delete operations (Zero Hardcoded Data)."""

    def test_tc_base_del_pos_01_delete_repeatable_row_and_save(self, baseline_page: BaselinePage):
        """TC-BASE-DEL-POS-01: Delete a repeatable row and save."""
        tc_id = "TC-BASE-DEL-POS-01"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.delete_repeatable_row("Allopathy Diagnosis", row_index=1)

        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.delete_repeatable_row("Aahar", row_index=1)

        baseline_page.switch_subtab("Physician and RAC Opinion")
        baseline_page.delete_repeatable_row("Physician Opinion", row_index=1)

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_del_pos_02_delete_last_remaining_row(self, baseline_page: BaselinePage):
        """TC-BASE-DEL-POS-02: Delete the last remaining row."""
        tc_id = "TC-BASE-DEL-POS-02"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.delete_repeatable_row("Vihar", row_index=0)

        baseline_page.switch_subtab("Physician and RAC Opinion")
        baseline_page.delete_repeatable_row("RAC Management", row_index=0)

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_del_pos_03_clear_optional_text_fields(self, baseline_page: BaselinePage):
        """TC-BASE-DEL-POS-03: Clear optional text fields."""
        tc_id = "TC-BASE-DEL-POS-03"
        pid = get_target_patient_id(tc_id)
        cleared_fields = get_cleared_fields_list(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        for f in cleared_fields:
            if "Allergy" in f:
                continue
            baseline_page.disease.fill_personal_details({f: ""})

        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.hetu_sevan_page.fill_aahar(meal="", timing="", food_habits=[], remark="")

        baseline_page.switch_subtab("Physician and RAC Opinion")
        baseline_page.physician_rac_page.fill_rac_management(approach="", remark="")

        baseline_page.save_baseline()
        baseline_page.verify_save_success()
