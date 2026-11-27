import pytest
from playwright.sync_api import Page, expect

try:
    from shared_tools.utils.env_config import config
    from shared_tools.auth.login_page import LoginPage
    from master_management.rac_clinic_masters.baseline_module.pages.master_create_page import RacBaselineMasterPage
except ImportError:
    from utils.env_config import config
    from auth.login_page import LoginPage
    from ...pages.master_create_page import RacBaselineMasterPage


@pytest.fixture
def master_page(authenticated_page: Page) -> RacBaselineMasterPage:
    """Provides an authenticated RacBaselineMasterPage session on https://rasayu-stg.corecotechnologies.com/masters."""
    mp = RacBaselineMasterPage(authenticated_page)
    mp.navigate_to_baseline_master_home()
    return mp


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.create
@pytest.mark.positive
@pytest.mark.baseline
class TestRacBaselineCreatePos:
    """Master Management test suite for RAC Clinic Create Baseline (22 Test Cases)."""

    # ==========================================
    # POSITIVE TEST CASES (TC-POS-MASTER-RAC-01 to 15)
    # ==========================================

    def test_tc_pos_master_rac_01_mandatory_field_standalone(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-01: Create with only mandatory field filled (Disease at Baseline — Standalone)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-01")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-01")

    def test_tc_pos_master_rac_02_mandatory_plus_optional_standalone(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-02: Create with mandatory + optional fields filled (Disease at Baseline — Standalone)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-02")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-02")

    def test_tc_pos_master_rac_03_mandatory_fields_dependent(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-03: Create with all mandatory fields filled (Disease at Baseline — Dependent)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-03")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-03")

    def test_tc_pos_master_rac_04_mandatory_field_hetu_sevan(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-04: Create with only mandatory field filled (Hetu Sevan)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-04")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-04")

    def test_tc_pos_master_rac_05_mandatory_plus_optional_hetu_sevan(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-05: Create with mandatory + optional fields filled (Hetu Sevan)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-05")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-05")

    def test_tc_pos_master_rac_06_mandatory_field_physician_opinion(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-06: Create with only mandatory field filled (Physician Opinion & RAC Management)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-06")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-06")

    def test_tc_pos_master_rac_07_mandatory_plus_optional_physician_opinion(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-07: Create with mandatory + optional fields filled (Physician Opinion & RAC Management)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-07")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-07")

    def test_tc_pos_master_rac_08_default_status_and_inactive_record(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-08: Default Status & creating an Inactive record."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-08")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-08")

    def test_tc_pos_master_rac_09_entry_counter_and_row_update(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-09: Table row, entry counter & action icons update."""
        master_page.execute_counter_update_test("TC-POS-MASTER-RAC-09")

    def test_tc_pos_master_rac_10_save_via_keyboard_shortcut(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-10: Save using keyboard shortcut (Alt + S)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-10")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-10")

    def test_tc_pos_master_rac_11_pagination_rollover(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-11: Pagination rollover (15 / page)."""
        master_page.create_master_record_from_test_data("TC-POS-MASTER-RAC-11")
        master_page.verify_master_record_in_list("TC-POS-MASTER-RAC-11")

    def test_tc_pos_master_rac_12_create_while_search_or_sort_active(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-12: Create while Search or Sort is active."""
        master_page.execute_search_active_create_test("TC-POS-MASTER-RAC-12")

    def test_tc_pos_master_rac_13_ui_persistence_after_refresh(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-13: UI persistence after browser refresh."""
        master_page.execute_refresh_persistence_test("TC-POS-MASTER-RAC-13")

    def test_tc_pos_master_rac_14_history_modal_reflects_creation(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-14: History modal reflects creation."""
        master_page.execute_history_modal_test("TC-POS-MASTER-RAC-14")

    def test_tc_pos_master_rac_15_clean_modal_state_switching_masters(self, master_page: RacBaselineMasterPage):
        """TC-POS-MASTER-RAC-15: Clean modal state when switching masters."""
        master_page.execute_modal_reset_test("TC-POS-MASTER-RAC-15")

    # ==========================================
