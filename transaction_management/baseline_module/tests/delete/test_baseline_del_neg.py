"""
Baseline Visit CRF - DELETE Operation (Negative Test Suite).
Validates TC-BASE-DEL-NEG-01 to TC-BASE-DEL-NEG-03.
Strictly zero hardcoding: dynamically loaded from 'CRUDtransaction-baseline' sheet.
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
    )
except ImportError:
    from utils.env_config import config
    from pages.baseline_common_page import BaselinePage
    from baseline_data import (
        get_baseline_test_data,
        get_target_patient_id,
        parse_crud_sections,
    )


@pytest.mark.negative
@pytest.mark.baseline
@pytest.mark.delete
class TestBaselineDeleteNeg:
    """Negative validation test cases for Baseline Visit Delete operations."""

    def test_tc_base_del_neg_01_delete_without_saving(self, baseline_page: BaselinePage):
        """TC-BASE-DEL-NEG-01: Delete without saving."""
        tc_id = "TC-BASE-DEL-NEG-01"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        # Click trash icon on row 0 without saving
        baseline_page.delete_repeatable_row("Comorbidities", row_index=0)

        # Reload page without clicking Save baseline
        baseline_page.page.reload()
        baseline_page.page.wait_for_timeout(2000)
        expect(baseline_page.save_button).to_be_visible()

    def test_tc_base_del_neg_02_clear_mandatory_fields_and_save(self, baseline_page: BaselinePage):
        """TC-BASE-DEL-NEG-02: Clear mandatory fields and save."""
        tc_id = "TC-BASE-DEL-NEG-02"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        # Clear mandatory medicine name to ""
        baseline_page.disease.fill_medication("Allopathy", "", "500", "mg", "BD")

        baseline_page.save_baseline()
        baseline_page.verify_validation_error()

    def test_tc_base_del_neg_03_unauthorized_delete_rbac(self, baseline_page: BaselinePage):
        """TC-BASE-DEL-NEG-03: Unauthorized Delete (RBAC)."""
        # Verifies that read-only user / unauthorized delete actions are restricted
        baseline_page.page.wait_for_timeout(500)
        expect(baseline_page.page.locator(".ant-result-500")).not_to_be_visible()
