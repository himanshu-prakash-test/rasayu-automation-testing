"""
Master Management Automation Test Suite: DWC Clinic - Baseline Module (DELETE Positive Operations).
Validates TC-DEL-POS-MASTER-DWC-01 to TC-DEL-POS-MASTER-DWC-11.
Strictly 100% Zero Hardcoding: dynamically loads all data from 'master_dwc_deletebaseline' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from master_management.dwc_clinic_masters.baseline_module.pages.dwc_delete_page import DwcBaselineMasterDeletePage
except ImportError:
    from ...pages.dwc_delete_page import DwcBaselineMasterDeletePage


@pytest.fixture
def delete_page(authenticated_page: Page) -> DwcBaselineMasterDeletePage:
    """Provides an authenticated DwcBaselineMasterDeletePage session on /masters."""
    dp = DwcBaselineMasterDeletePage(authenticated_page)
    dp.navigate_to_masters_page()
    return dp


@pytest.mark.master
@pytest.mark.dwc
@pytest.mark.delete
@pytest.mark.positive
@pytest.mark.baseline
class TestDwcBaselineDelPos:
    """Positive test cases for DWC Baseline Master Delete operations (Zero Hardcoded Data)."""

    def test_tc_del_pos_master_dwc_01_confirm_dialog_appearance(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-01: Confirmation Dialog Check on Delete Trigger."""
        delete_page.verify_delete_dialog_visible("TC-DEL-POS-MASTER-DWC-01")

    def test_tc_del_pos_master_dwc_02_delete_active_record(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-02: Delete Active Record — Standalone Master."""
        delete_page.execute_delete_active_record("TC-DEL-POS-MASTER-DWC-02")

    def test_tc_del_pos_master_dwc_03_delete_inactive_record(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-03: Delete Inactive Record — Standalone Master."""
        delete_page.execute_delete_inactive_record("TC-DEL-POS-MASTER-DWC-03")

    def test_tc_del_pos_master_dwc_04_delete_child_record(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-04: Delete Child Record — Dependent Master."""
        delete_page.execute_delete_child_record("TC-DEL-POS-MASTER-DWC-04")

    def test_tc_del_pos_master_dwc_05_delete_pharmacology_record(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-05: Delete Child Record — Multi-Parent Pharmacology Master."""
        delete_page.execute_delete_pharmacology("TC-DEL-POS-MASTER-DWC-05")

    def test_tc_del_pos_master_dwc_06_delete_hetu_sevan(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-06: Delete Record — Hetu Sevan Dependent Master."""
        delete_page.execute_delete_hetu_sevan("TC-DEL-POS-MASTER-DWC-06")

    def test_tc_del_pos_master_dwc_07_delete_lab_parameter(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-07: Delete Record — Lab Investigation Dependent Master."""
        delete_page.execute_delete_lab_parameter("TC-DEL-POS-MASTER-DWC-07")

    def test_tc_del_pos_master_dwc_08_delete_filtered(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-08: Delete Record While Search / Sort Filter Active."""
        delete_page.execute_delete_filtered("TC-DEL-POS-MASTER-DWC-08")

    def test_tc_del_pos_master_dwc_09_delete_page2(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-09: Delete Last Record on Page 2."""
        delete_page.execute_delete_page2("TC-DEL-POS-MASTER-DWC-09")

    def test_tc_del_pos_master_dwc_10_refresh_persistence(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-10: Persistence of Deletion After Browser Refresh."""
        delete_page.execute_delete_refresh_persistence("TC-DEL-POS-MASTER-DWC-10")

    def test_tc_del_pos_master_dwc_11_history_modal_audit(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-POS-MASTER-DWC-11: History Modal Verification After Deletion."""
        delete_page.execute_delete_history("TC-DEL-POS-MASTER-DWC-11")
