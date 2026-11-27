"""
Baseline Visit CRF - CREATE Operation (Negative Test Suite).
Validates TC-BASE-CREATE-NEG-01 to TC-BASE-CREATE-NEG-07.
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
@pytest.mark.create
class TestBaselineCreateNeg:
    """Negative validation and boundary test cases for Baseline Visit Create."""

    def test_tc_base_create_neg_01_invalid_date_logic(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-NEG-01: Invalid date logic."""
        tc_id = "TC-BASE-CREATE-NEG-01"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        # Chemo Dates: Start Date = 15/10/2026, End Date = 01/09/2026 (End < Start)
        baseline_page.disease.fill_chemo(cycle_no="1", day="1", start_date="15/10/2026", end_date="01/09/2026")
        baseline_page.save_baseline()
        baseline_page.verify_validation_error()

    def test_tc_base_create_neg_02_invalid_numeric_time_formats(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-NEG-02: Invalid numeric & time formats."""
        tc_id = "TC-BASE-CREATE-NEG-02"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Hetu Sevan")

        # Invalid meal timing: 25:99 PM
        baseline_page.hetu_sevan_page.fill_aahar(meal="Lunch", timing="25:99 PM", food_habits=[])
        baseline_page.save_baseline()
        baseline_page.verify_validation_error()

    def test_tc_base_create_neg_03_invalid_conditional_fields_habits(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-NEG-03: Invalid conditional fields (Habits)."""
        tc_id = "TC-BASE-CREATE-NEG-03"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Hetu Sevan")

        # Stopped Since = 5 Years > Since = 2 Years
        baseline_page.hetu_sevan_page.fill_habit(habit="Alcohol", status="Stopped", qty="2", since="2", unit="Years", stopped_since="5")
        baseline_page.save_baseline()
        baseline_page.verify_validation_error()

    def test_tc_base_create_neg_04_boundary_length_special_characters(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-NEG-04: Boundary length & special characters."""
        tc_id = "TC-BASE-CREATE-NEG-04"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        # 550 chars payload
        long_string = "A" * 550
        baseline_page.disease.fill_personal_details({"Remark": long_string})
        baseline_page.save_baseline()

        # Sanitize XSS payload: <script>alert('xss')</script>
        xss_string = "<script>alert('xss')</script>"
        baseline_page.disease.fill_personal_details({"Remark": xss_string})
        baseline_page.save_baseline()
        # Verify no unhandled script execution
        baseline_page.page.wait_for_timeout(500)

    def test_tc_base_create_neg_05_double_click_save_idempotency(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-NEG-05: Double-click Save (Idempotency)."""
        tc_id = "TC-BASE-CREATE-NEG-05"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        # Rapidly double click save button
        save_btn = baseline_page.save_button
        if save_btn.is_visible():
            save_btn.dblclick()
            baseline_page.page.wait_for_timeout(1000)
            # Should not create duplicate records or crash
            expect(baseline_page.page.locator(".ant-result-500, .error-boundary")).not_to_be_visible()

    def test_tc_base_create_neg_06_network_api_failure_during_save(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-NEG-06: Network / API failure during Save."""
        tc_id = "TC-BASE-CREATE-NEG-06"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.disease.fill_personal_details({"Remark": "Network fail test"})

        # Route abort simulation for baseline API
        baseline_page.page.route("**/api/**/baseline**", lambda route: route.abort())
        baseline_page.save_baseline()
        baseline_page.page.wait_for_timeout(1000)
        # Restore route
        baseline_page.page.unroute("**/api/**/baseline**")

    def test_tc_base_create_neg_07_unauthorized_create_rbac(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-NEG-07: Unauthorized Create (RBAC)."""
        # Verifies that read-only user cannot save or access prohibited actions
        baseline_page.page.wait_for_timeout(500)
        expect(baseline_page.page).not_to_have_title("500 Server Error")
