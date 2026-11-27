"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (UPDATE Positive Operations).
Validates TC-DWC-VIS-UPD-POS-01 to TC-DWC-VIS-UPD-POS-04.
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
@pytest.mark.positive
class TestDwcVisitUpdatePos:
    """Positive test cases for DWC Visit Master Update operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_upd_pos_01_update_name_and_description(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-UPD-POS-01: Update Symptom Name and Description."""
        visit_page.update_visit_name_and_description("TC-DWC-VIS-UPD-POS-01")

    def test_tc_dwc_vis_upd_pos_02_toggle_status_active_inactive(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-UPD-POS-02: Toggle Consent Form record status Active → Inactive → Active."""
        visit_page.toggle_visit_status("TC-DWC-VIS-UPD-POS-02")

    def test_tc_dwc_vis_upd_pos_03_clear_optional_description(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-UPD-POS-03: Clear Symptom Description to blank and verify placeholder."""
        visit_page.clear_visit_description("TC-DWC-VIS-UPD-POS-03")

    def test_tc_dwc_vis_upd_pos_04_update_via_keyboard_shortcut(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-UPD-POS-04: Update Description using Alt + S and verify audit in History."""
        visit_page.update_visit_via_shortcut("TC-DWC-VIS-UPD-POS-04")
