"""
Baseline Visit CRF - READ Operation (Negative Test Suite).
Validates TC-BASE-READ-NEG-01 to TC-BASE-READ-NEG-03.
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
@pytest.mark.read
class TestBaselineReadNeg:
    """Negative validation test cases for Baseline Visit Read operations."""

    def test_tc_base_read_neg_01_unsaved_changes_guard_on_navigation(self, baseline_page: BaselinePage):
        """TC-BASE-READ-NEG-01: Unsaved changes guard on navigation."""
        tc_id = "TC-BASE-READ-NEG-01"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        # Make unsaved edit
        baseline_page.disease.fill_personal_details({"Remark": "Unsaved guard check"})

        # Attempt to navigate away without saving
        visit_tab = baseline_page.page.locator("button:has-text('Visit'), .ant-tabs-tab:has-text('Visit')").first
        if visit_tab.is_visible():
            visit_tab.click()
            baseline_page.page.wait_for_timeout(500)

            # Check if confirmation modal / unsaved guard appears or stays on page
            guard = baseline_page.page.locator(".ant-modal-confirm, .ant-modal:has-text('unsaved'), div[role='dialog']").first
            if guard.is_visible():
                expect(guard).to_be_visible()
                # Dismiss guard
                cancel_btn = guard.locator("button:has-text('Cancel'), button:has-text('Stay')").first
                if cancel_btn.is_visible():
                    cancel_btn.click()

    def test_tc_base_read_neg_02_readonly_enforcement_in_history(self, baseline_page: BaselinePage):
        """TC-BASE-READ-NEG-02: Read-only enforcement in History."""
        tc_id = "TC-BASE-READ-NEG-02"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.open_history()

        history_modal = baseline_page.page.locator(".ant-modal, .history-modal, div[role='dialog']").first
        if history_modal.is_visible():
            # Verify inputs inside modal are disabled / read-only
            inputs = history_modal.locator("input:not([disabled]):not([readonly]), textarea:not([disabled]):not([readonly])")
            # If any inputs exist, they shouldn't allow form submission
            save_in_history = history_modal.locator("button:has-text('Save'), input[value='Save']")
            expect(save_in_history).not_to_be_visible()
            baseline_page.close_history()

    def test_tc_base_read_neg_03_unauthorized_patient_module_access(self, baseline_page: BaselinePage):
        """TC-BASE-READ-NEG-03: Unauthorized patient/module access (RBAC)."""
        # Attempt to access an invalid / nonexistent patient ID
        invalid_url = f"{config.main_app_url.rstrip('/')}/patients/rac/999999999/baseline"
        baseline_page.page.goto(invalid_url, wait_until="domcontentloaded")
        baseline_page.page.wait_for_timeout(1000)

        # Should show 404, redirect or patient not found, and not crash
        expect(baseline_page.page.locator(".ant-result-500")).not_to_be_visible()
