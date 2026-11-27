"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (UPDATE Positive Operations).
Validates TC-RAC-VISIT-UPD-POS-01 to TC-RAC-VISIT-UPD-POS-04.
Strictly 100% Zero Hardcoding: dynamically loads all data from 'CRUDmaster-rac-visit' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from master_management.rac_clinic_masters.visit_module.pages.visit_master_page import VisitMasterPage
except ImportError:
    from pages.visit_master_page import VisitMasterPage


@pytest.fixture
def visit_page(authenticated_page: Page) -> VisitMasterPage:
    """Provides an authenticated VisitMasterPage session on https://rasayu-stg.corecotechnologies.com/masters."""
    vp = VisitMasterPage(authenticated_page)
    vp.navigate_to_masters_page()
    return vp


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.visit
@pytest.mark.update
@pytest.mark.positive
class TestRacVisitUpdatePos:
    """Positive test cases for RAC Visit Master Update operations (Zero Hardcoded Data)."""

    def test_tc_rac_visit_upd_pos_01_edit_name_and_description(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-UPD-POS-01: Verify Edit modal pre-populates existing Visit Master record data."""
        visit_page.update_visit_name_and_description("TC-RAC-VISIT-UPD-POS-01")

    def test_tc_rac_visit_upd_pos_02_toggle_status_active_inactive(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-UPD-POS-02: Update mandatory field only on an existing Visit Master record."""
        visit_page.toggle_visit_status("TC-RAC-VISIT-UPD-POS-02")

    def test_tc_rac_visit_upd_pos_03_clear_description_to_blank(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-UPD-POS-03: Update or clear optional Description field on a Visit Master record."""
        visit_page.clear_visit_description("TC-RAC-VISIT-UPD-POS-03")

    def test_tc_rac_visit_upd_pos_04_update_via_keyboard_shortcut_history(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-UPD-POS-04: Toggle Visit Master record Status between Active and Inactive."""
        visit_page.update_visit_via_shortcut("TC-RAC-VISIT-UPD-POS-04")
