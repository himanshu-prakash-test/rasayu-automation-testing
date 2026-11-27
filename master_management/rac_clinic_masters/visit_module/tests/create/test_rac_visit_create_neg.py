"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (CREATE Negative Operations).
Validates TC-RAC-VISIT-CREATE-NEG-01 to TC-RAC-VISIT-CREATE-NEG-04.
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
@pytest.mark.negative
class TestRacVisitCreateNeg:
    """Negative validation and boundary test cases for RAC Visit Master Create operations."""

    def test_tc_rac_visit_create_neg_01_reject_empty_or_whitespace_name(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-NEG-01: Attempt to create a Visit Master record with the mandatory field left blank."""
        visit_page.verify_create_negative_empty_name("TC-RAC-VISIT-CREATE-NEG-01")

    def test_tc_rac_visit_create_neg_02_reject_duplicate_name(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-NEG-02: Attempt to create a duplicate Visit Master record."""
        visit_page.verify_create_negative_duplicate("TC-RAC-VISIT-CREATE-NEG-02")

    def test_tc_rac_visit_create_neg_03_reject_oversized_name_and_xss(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-NEG-03: Attempt to create a Visit Master record with whitespace-only or over-length input."""
        visit_page.verify_create_negative_oversized_xss("TC-RAC-VISIT-CREATE-NEG-03")

    def test_tc_rac_visit_create_neg_04_cancel_discard_and_double_click_save(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-CREATE-NEG-04: Attempt to create a Visit Master record with HTML/script injection payload."""
        visit_page.verify_create_negative_cancel_and_double_click("TC-RAC-VISIT-CREATE-NEG-04")
