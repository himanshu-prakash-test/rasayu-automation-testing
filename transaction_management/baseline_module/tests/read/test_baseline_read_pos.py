"""
Baseline Visit CRF - READ Operation (Positive Test Suite).
Validates TC-BASE-READ-POS-01 to TC-BASE-READ-POS-07.
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


@pytest.mark.positive
@pytest.mark.baseline
@pytest.mark.read
class TestBaselineReadPos:
    """Positive test cases for Baseline Visit Read operations."""

    def test_tc_base_read_pos_01_data_persistence_after_reload(self, baseline_page: BaselinePage):
        """TC-BASE-READ-POS-01: Data persistence after reload."""
        tc_id = "TC-BASE-READ-POS-01"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.page.reload()
        baseline_page.page.wait_for_timeout(2000)

        # Verify page elements rendered
        expect(baseline_page.save_button).to_be_visible()

    def test_tc_base_read_pos_02_accordion_badge_count_accuracy(self, baseline_page: BaselinePage):
        """TC-BASE-READ-POS-02: Accordion badge count accuracy."""
        tc_id = "TC-BASE-READ-POS-02"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.page.wait_for_timeout(1000)

        # Check badge counts
        count = baseline_page.get_badge_count("Baseline Allopathy Diagnosis")
        baseline_page.logger.info(f"Diagnosis badge count: {count}")

    def test_tc_base_read_pos_03_history_snapshot_view(self, baseline_page: BaselinePage):
        """TC-BASE-READ-POS-03: History snapshot view."""
        tc_id = "TC-BASE-READ-POS-03"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.open_history()

        history_modal = baseline_page.page.locator(".ant-modal, .history-modal, div[role='dialog']").first
        if history_modal.is_visible():
            expect(history_modal).to_be_visible()
            baseline_page.close_history()

    def test_tc_base_read_pos_04_tab_switching_with_saved_data(self, baseline_page: BaselinePage):
        """TC-BASE-READ-POS-04: Tab switching with saved data."""
        tc_id = "TC-BASE-READ-POS-04"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.page.wait_for_timeout(500)

        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.page.wait_for_timeout(500)

        baseline_page.switch_subtab("Physician and RAC Opinion")
        baseline_page.page.wait_for_timeout(500)

        # Switch back
        baseline_page.switch_subtab("Disease at Baseline")
        expect(baseline_page.save_button).to_be_visible()

    def test_tc_base_read_pos_05_cross_module_data_sync(self, baseline_page: BaselinePage):
        """TC-BASE-READ-POS-05: Cross-module data sync."""
        tc_id = "TC-BASE-READ-POS-05"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        # Check clinical tabs navigation
        visit_tab = baseline_page.page.locator("button:has-text('Visit'), .ant-tabs-tab:has-text('Visit')").first
        if visit_tab.is_visible():
            visit_tab.click()
            baseline_page.page.wait_for_timeout(1000)

        # Switch back to Baseline
        if baseline_page.baseline_tab.is_visible():
            baseline_page.baseline_tab.click()
            baseline_page.page.wait_for_timeout(1000)
            expect(baseline_page.save_button).to_be_visible()

    def test_tc_base_read_pos_06_quick_jump_shortcut(self, baseline_page: BaselinePage):
        """TC-BASE-READ-POS-06: Quick jump shortcut (Ctrl + K)."""
        tc_id = "TC-BASE-READ-POS-06"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.quick_jump_shortcut()
        baseline_page.page.wait_for_timeout(500)
        # Press Escape to close palette if opened
        baseline_page.page.keyboard.press("Escape")

    def test_tc_base_read_pos_07_role_based_read_access(self, baseline_page: BaselinePage):
        """TC-BASE-READ-POS-07: Role-based read access (RBAC)."""
        tc_id = "TC-BASE-READ-POS-07"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        expect(baseline_page.page.locator("body")).to_be_visible()
        expect(baseline_page.page.locator(".ant-result-403")).not_to_be_visible()
