"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (DELETE Positive Operations).
Validates TC-DWC-VIS-DEL-POS-01 to TC-DWC-VIS-DEL-POS-03.
Strictly 100% Zero Hardcoding: dynamically loads all data from 'CRUDmaster-dwc-visit' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from master_management.dwc_clinic_masters.visit_module.pages.dwc_visit_master_page import DwcVisitMasterPage
except ImportError:
    from pages.dwc_visit_master_page import DwcVisitMasterPage


@pytest.fixture
def visit_page(authenticated_page: Page) -> DwcVisitMasterPage:
    """Provides an authenticated DwcVisitMasterPage session on /masters."""
    vp = DwcVisitMasterPage(authenticated_page)
    vp.navigate_to_masters_page()
    return vp


@pytest.mark.master
@pytest.mark.dwc
@pytest.mark.visit
@pytest.mark.delete
@pytest.mark.positive
class TestDwcVisitDeletePos:
    """Positive test cases for DWC Visit Master Delete operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_del_pos_01_delete_unused_record_reload_persistence(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-DEL-POS-01: Delete unused Symptom record and verify count returns to 32."""
        visit_page.delete_visit_record_with_reload("TC-DWC-VIS-DEL-POS-01")

    def test_tc_dwc_vis_del_pos_02_search_and_delete_entry_counter(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-DEL-POS-02: Search and delete Symptom record from filtered view."""
        visit_page.search_and_delete_entry_counter("TC-DWC-VIS-DEL-POS-02")

    def test_tc_dwc_vis_del_pos_03_delete_and_verify_history(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-DEL-POS-03: Delete Consent Form record and verify deletion log in History."""
        visit_page.delete_and_verify_history("TC-DWC-VIS-DEL-POS-03")
