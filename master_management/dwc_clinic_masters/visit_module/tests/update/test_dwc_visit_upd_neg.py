"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (UPDATE Negative Operations).
Validates TC-DWC-VIS-UPD-NEG-01 to TC-DWC-VIS-UPD-NEG-03.
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
@pytest.mark.update
@pytest.mark.negative
class TestDwcVisitUpdateNeg:
    """Negative test cases for DWC Visit Master Update operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_upd_neg_01_blank_name_rejection(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-UPD-NEG-01: Reject blank Symptom Name on update."""
        visit_page.verify_update_negative_blank_name("TC-DWC-VIS-UPD-NEG-01")

    def test_tc_dwc_vis_upd_neg_02_duplicate_name_rejection(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-UPD-NEG-02: Reject renaming Symptom to an existing Name."""
        visit_page.verify_update_negative_duplicate_name("TC-DWC-VIS-UPD-NEG-02")

    def test_tc_dwc_vis_upd_neg_03_cancel_discard_edits(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-UPD-NEG-03: Verify Cancel discards unsaved edits on existing record."""
        visit_page.verify_update_negative_cancel_discard("TC-DWC-VIS-UPD-NEG-03")
