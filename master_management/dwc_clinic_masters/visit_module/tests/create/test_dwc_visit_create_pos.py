"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (CREATE Positive Operations).
Validates TC-DWC-VIS-CREATE-POS-01 to TC-DWC-VIS-CREATE-POS-04.
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
@pytest.mark.create
@pytest.mark.positive
class TestDwcVisitCreatePos:
    """Positive test cases for DWC Visit Master Create operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_create_pos_01_mandatory_only(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-POS-01: Create active DWC Symptom master record."""
        visit_page.create_visit_record_from_data("TC-DWC-VIS-CREATE-POS-01")

    def test_tc_dwc_vis_create_pos_02_blank_description(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-POS-02: Create active Symptom with blank description."""
        visit_page.create_visit_record_from_data("TC-DWC-VIS-CREATE-POS-02")

    def test_tc_dwc_vis_create_pos_03_inactive_status(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-POS-03: Create inactive DWC Consent Form master record."""
        visit_page.create_visit_record_from_data("TC-DWC-VIS-CREATE-POS-03")

    def test_tc_dwc_vis_create_pos_04_keyboard_navigation(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-POS-04: Create Anupashaya record using keyboard navigation and shortcut."""
        visit_page.create_visit_record_via_keyboard("TC-DWC-VIS-CREATE-POS-04")
