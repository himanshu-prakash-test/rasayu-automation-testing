"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (CREATE Positive Operations).
Validates TC-RAC-VISIT-CREATE-POS-01 to TC-RAC-VISIT-CREATE-POS-04.
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
@pytest.mark.create
@pytest.mark.positive
class TestRacVisitCreatePos:
    """Positive test cases for RAC Visit Master Create operations (Zero Hardcoded Data)."""

    def test_tc_rac_visit_create_pos_01_mandatory_only_visit_mode(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-POS-01: Create a Visit Master record with only the mandatory field filled."""
        visit_page.create_visit_record_from_data("TC-RAC-VISIT-CREATE-POS-01")

    def test_tc_rac_visit_create_pos_02_mandatory_plus_optional_symptom_type(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-POS-02: Create a Visit Master record with mandatory and optional Description fields filled."""
        visit_page.create_visit_record_from_data("TC-RAC-VISIT-CREATE-POS-02")

    def test_tc_rac_visit_create_pos_03_inactive_clinical_response(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-POS-03: Create a dependent Visit Master record mapped to an Active parent record."""
        visit_page.create_visit_record_from_data("TC-RAC-VISIT-CREATE-POS-03")

    def test_tc_rac_visit_create_pos_04_keyboard_navigation_shortcut(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-POS-04: Verify newly created Active Visit Master record appears in Patient Visit dropdowns."""
        visit_page.create_visit_record_via_keyboard("TC-RAC-VISIT-CREATE-POS-04")
