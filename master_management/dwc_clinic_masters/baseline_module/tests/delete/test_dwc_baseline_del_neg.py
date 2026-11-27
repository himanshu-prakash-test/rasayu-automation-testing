"""
Master Management Automation Test Suite: DWC Clinic - Baseline Module (DELETE Negative Operations).
Validates TC-DEL-NEG-MASTER-DWC-01 to TC-DEL-NEG-MASTER-DWC-06.
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
@pytest.mark.negative
@pytest.mark.baseline
class TestDwcBaselineDelNeg:
    """Negative test cases for DWC Baseline Master Delete operations (Zero Hardcoded Data)."""

    def test_tc_del_neg_master_dwc_01_cancel_deletion_modal(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-NEG-MASTER-DWC-01: Cancel Deletion via Cancel Button, Close Icon (X), or Esc Key."""
        delete_page.execute_negative_cancel_delete("TC-DEL-NEG-MASTER-DWC-01")

    def test_tc_del_neg_master_dwc_02_delete_parent_with_active_children(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-NEG-MASTER-DWC-02: Attempt Deletion of Parent Record with Active Child Records."""
        delete_page.execute_negative_delete_parent_active_child("TC-DEL-NEG-MASTER-DWC-02")

    def test_tc_del_neg_master_dwc_03_delete_parent_with_inactive_children(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-NEG-MASTER-DWC-03: Attempt Deletion of Parent Record Linked to Inactive Child Records."""
        delete_page.execute_negative_delete_parent_inactive_child("TC-DEL-NEG-MASTER-DWC-03")

    def test_tc_del_neg_master_dwc_04_delete_patient_linked_record(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-NEG-MASTER-DWC-04: Attempt Deletion of Master Record Linked to Patient Clinical Data."""
        delete_page.execute_negative_delete_linked_patient_record("TC-DEL-NEG-MASTER-DWC-04")

    def test_tc_del_neg_master_dwc_05_double_click_confirm_delete(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-NEG-MASTER-DWC-05: Rapid Double-Click on Confirm Delete Button."""
        delete_page.execute_negative_double_click_delete("TC-DEL-NEG-MASTER-DWC-05")

    def test_tc_del_neg_master_dwc_06_switch_masters_after_delete_cancel(self, delete_page: DwcBaselineMasterDeletePage):
        """TC-DEL-NEG-MASTER-DWC-06: Switch Masters Immediately After Cancelling Deletion."""
        delete_page.execute_negative_switch_masters_after_delete_cancel("TC-DEL-NEG-MASTER-DWC-06")
