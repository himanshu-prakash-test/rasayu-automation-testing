
import pytest
from playwright.sync_api import Page

try:
    from shared_tools.utils.env_config import config
    from master_management.rac_clinic_masters.baseline_module.pages.master_delete_page import MasterDeletePage
except ImportError:
    from utils.env_config import config
    from ...pages.master_delete_page import MasterDeletePage


@pytest.fixture
def delete_page(authenticated_page: Page) -> MasterDeletePage:
    """Provides an authenticated MasterDeletePage session on https://rasayu-stg.corecotechnologies.com/masters."""
    dp = MasterDeletePage(authenticated_page)
    dp.navigate_to_masters_page()
    return dp


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.delete
@pytest.mark.baseline
class TestRacBaselineDeletePos:
    """Master Management test suite for RAC Clinic Delete Baseline (15 Test Cases)."""

    # ==========================================
    # POSITIVE TEST CASES (TC-DEL-POS-MASTER-RAC-01 to 10)
    # ==========================================

    def test_tc_del_pos_master_rac_01_verify_delete_confirmation_dialog_appears(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-01: Verify Delete confirmation dialog appears with Confirm and Cancel options."""
        delete_page.verify_delete_dialog_visible("TC-DEL-POS-MASTER-RAC-01")

    def test_tc_del_pos_master_rac_02_delete_active_record(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-02: Delete an Active record (Disease at Baseline — Standalone)."""
        delete_page.execute_delete_active_record("TC-DEL-POS-MASTER-RAC-02")

    def test_tc_del_pos_master_rac_03_delete_inactive_record(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-03: Delete an Inactive record (Disease at Baseline — Standalone)."""
        delete_page.execute_delete_inactive_record("TC-DEL-POS-MASTER-RAC-03")

    def test_tc_del_pos_master_rac_04_delete_child_record(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-04: Delete a child record (Disease at Baseline — Dependent)."""
        delete_page.execute_delete_child_record("TC-DEL-POS-MASTER-RAC-04")

    def test_tc_del_pos_master_rac_05_delete_hetu_sevan_record(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-05: Delete a record (Hetu Sevan)."""
        delete_page.execute_delete_hetu_sevan("TC-DEL-POS-MASTER-RAC-05")

    def test_tc_del_pos_master_rac_06_delete_physician_opinion_record(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-06: Delete a record (Physician Opinion & RAC Management)."""
        delete_page.execute_delete_physician_opinion("TC-DEL-POS-MASTER-RAC-06")

    def test_tc_del_pos_master_rac_07_delete_while_search_or_sort_active(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-07: Delete while Search or Status Sort is active."""
        delete_page.execute_delete_filtered("TC-DEL-POS-MASTER-RAC-07")

    def test_tc_del_pos_master_rac_08_pagination_update_deleting_page_2_record(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-08: Pagination update when deleting the last record on Page 2."""
        delete_page.execute_delete_page2("TC-DEL-POS-MASTER-RAC-08")

    def test_tc_del_pos_master_rac_09_ui_persistence_after_browser_refresh(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-09: UI persistence after browser refresh."""
        delete_page.execute_delete_refresh_persistence("TC-DEL-POS-MASTER-RAC-09")

    def test_tc_del_pos_master_rac_10_history_modal_reflects_deletion(self, delete_page: MasterDeletePage):
        """TC-DEL-POS-MASTER-RAC-10: History modal reflects deletion."""
        delete_page.execute_delete_history("TC-DEL-POS-MASTER-RAC-10")

    # ==========================================
