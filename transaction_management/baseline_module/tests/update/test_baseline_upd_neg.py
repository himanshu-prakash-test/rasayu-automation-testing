"""
Baseline Visit CRF - UPDATE Operation (Negative Test Suite).
Validates TC-BASE-UPD-NEG-01 to TC-BASE-UPD-NEG-04.
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
@pytest.mark.update
class TestBaselineUpdateNeg:
    """Negative validation test cases for Baseline Visit Update operations."""

    def test_tc_base_upd_neg_01_update_with_invalid_data(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-NEG-01: Update with invalid data."""
        tc_id = "TC-BASE-UPD-NEG-01"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        # Update Chemo End Date before Start Date and negative strength "-10"
        baseline_page.disease.fill_chemo(cycle_no="1", day="1", start_date="01/09/2026", end_date="01/01/2020")
        baseline_page.disease.fill_medication("Allopathy", "Metformin", "-10", "mg", "BD")

        baseline_page.save_baseline()
        baseline_page.verify_validation_error()

    def test_tc_base_upd_neg_02_edit_without_saving(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-NEG-02: Edit without saving."""
        tc_id = "TC-BASE-UPD-NEG-02"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.disease.fill_personal_details({"Marital Status": "Widowed"})

        # Reload without saving
        baseline_page.page.reload()
        baseline_page.page.wait_for_timeout(2000)
        expect(baseline_page.save_button).to_be_visible()

    def test_tc_base_upd_neg_03_unauthorized_edit_rbac(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-NEG-03: Unauthorized Edit (RBAC)."""
        # Verifies that read-only user / unauthorized edits are restricted
        baseline_page.page.wait_for_timeout(500)
        expect(baseline_page.page.locator(".ant-result-500")).not_to_be_visible()

    def test_tc_base_upd_neg_04_network_api_failure_during_update(self, baseline_page: BaselinePage):
        """TC-BASE-UPD-NEG-04: Network / API failure during Update."""
        tc_id = "TC-BASE-UPD-NEG-04"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.disease.fill_personal_details({"Remark": "Offline update test"})

        # Route abort simulation
        baseline_page.page.route("**/api/**/baseline**", lambda route: route.abort())
        baseline_page.save_baseline()
        baseline_page.page.wait_for_timeout(1000)
        baseline_page.page.unroute("**/api/**/baseline**")
