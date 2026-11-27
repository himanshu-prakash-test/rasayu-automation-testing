"""
Master Management Automation Test Suite: RAC Clinic - Disease at Baseline (Update Module).
Executes end-to-end automation testing strictly based on the 'master-rac-updatebaseline' sheet
in Test Cases and Test Data workbooks.
Validates all 22 test cases (15 Positive + 7 Negative).
Zero hardcoding: all master categories, records, descriptions, status toggles, shortcuts,
and actions are dynamically resolved from Excel.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from shared_tools.utils.env_config import config
    from shared_tools.auth.login_page import LoginPage
    from master_management.rac_clinic_masters.baseline_module.pages.master_update_page import MasterUpdatePage
except ImportError:
    from utils.env_config import config
    from auth.login_page import LoginPage
    from ...pages.master_update_page import MasterUpdatePage


@pytest.fixture
def update_page(authenticated_page: Page) -> MasterUpdatePage:
    """Provides an authenticated MasterUpdatePage session on https://rasayu-stg.corecotechnologies.com/masters."""
    up = MasterUpdatePage(authenticated_page)
    up.navigate_to_masters_page()
    return up


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.update
@pytest.mark.baseline
class TestRacBaselineUpdatePos:
    """Master Management test suite for RAC Clinic Update Baseline (22 Test Cases)."""

    # ==========================================
    # POSITIVE TEST CASES (TC-UPD-POS-MASTER-RAC-01 to 15)
    # ==========================================

    def test_tc_upd_pos_master_rac_01_verify_edit_modal_prepopulated(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-01: Verify Edit modal pre-populates existing data."""
        update_page.verify_edit_modal_prepopulated("TC-UPD-POS-MASTER-RAC-01")

    def test_tc_upd_pos_master_rac_02_update_mandatory_field_standalone(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-02: Update mandatory field only (Disease at Baseline — Standalone)."""
        update_page.execute_mandatory_field_update("TC-UPD-POS-MASTER-RAC-02")

    def test_tc_upd_pos_master_rac_03_update_or_clear_optional_description(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-03: Update or clear optional Description field."""
        update_page.execute_description_update_and_clear("TC-UPD-POS-MASTER-RAC-03")

    def test_tc_upd_pos_master_rac_04_update_parent_dropdown_and_name_dependent(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-04: Update parent dropdown and/or name (Disease at Baseline — Dependent)."""
        update_page.execute_dependent_master_update("TC-UPD-POS-MASTER-RAC-04")

    def test_tc_upd_pos_master_rac_05_update_mandatory_and_optional_hetu_sevan(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-05: Update mandatory & optional fields (Hetu Sevan)."""
        update_page.execute_hetu_sevan_update("TC-UPD-POS-MASTER-RAC-05")

    def test_tc_upd_pos_master_rac_06_update_mandatory_and_optional_physician_opinion(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-06: Update mandatory & optional fields (Physician Opinion & RAC Management)."""
        update_page.execute_physician_opinion_update("TC-UPD-POS-MASTER-RAC-06")

    def test_tc_upd_pos_master_rac_07_toggle_status_active_inactive(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-07: Toggle Status (Active ↔ Inactive)."""
        update_page.execute_status_toggle_update("TC-UPD-POS-MASTER-RAC-07")

    def test_tc_upd_pos_master_rac_08_verify_id_counter_action_icons_intact(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-08: Verify ID, entry counter & action icons stay intact after update."""
        update_page.execute_counter_preserved_update("TC-UPD-POS-MASTER-RAC-08")

    def test_tc_upd_pos_master_rac_09_save_update_via_keyboard_shortcut(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-09: Save update using keyboard shortcut (Alt + S)."""
        update_page.execute_shortcut_update("TC-UPD-POS-MASTER-RAC-09")

    def test_tc_upd_pos_master_rac_10_update_while_search_or_sort_active(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-10: Update while Search or Status Sort is active."""
        update_page.execute_filtered_update("TC-UPD-POS-MASTER-RAC-10")

    def test_tc_upd_pos_master_rac_11_update_record_on_page_2(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-11: Update a record on Page 2 (Pagination state)."""
        update_page.execute_page2_update("TC-UPD-POS-MASTER-RAC-11")

    def test_tc_upd_pos_master_rac_12_ui_persistence_after_refresh(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-12: UI persistence after browser refresh."""
        update_page.execute_refresh_persistence("TC-UPD-POS-MASTER-RAC-12")

    def test_tc_upd_pos_master_rac_13_history_modal_reflects_update(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-13: History modal reflects the update."""
        update_page.execute_history_modal_update("TC-UPD-POS-MASTER-RAC-13")

    def test_tc_upd_pos_master_rac_14_clean_modal_state_switching_masters_after_update(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-14: Clean modal state when switching masters after update."""
        update_page.execute_clean_modal_switching("TC-UPD-POS-MASTER-RAC-14")

    def test_tc_upd_pos_master_rac_15_open_edit_modal_save_without_modifications(self, update_page: MasterUpdatePage):
        """TC-UPD-POS-MASTER-RAC-15: Open Edit modal and save without modifying any fields."""
        update_page.execute_save_without_modification("TC-UPD-POS-MASTER-RAC-15")

    # ==========================================
