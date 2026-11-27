"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (CREATE Negative Operations).
Validates TC-DWC-VIS-CREATE-NEG-01 to TC-DWC-VIS-CREATE-NEG-04.
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
@pytest.mark.negative
class TestDwcVisitCreateNeg:
    """Negative test cases for DWC Visit Master Create operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_create_neg_01_blank_name_validation(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-NEG-01: Reject blank or whitespace-only Symptom Name."""
        visit_page.verify_create_negative_empty_name("TC-DWC-VIS-CREATE-NEG-01")

    def test_tc_dwc_vis_create_neg_02_duplicate_name_check(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-NEG-02: Reject duplicate Symptom Name (exact and case-insensitive)."""
        visit_page.verify_create_negative_duplicate("TC-DWC-VIS-CREATE-NEG-02")

    def test_tc_dwc_vis_create_neg_03_oversized_name_and_xss(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-NEG-03: Enforce max Name length (305 chars) and sanitize XSS in Description."""
        visit_page.verify_create_negative_oversized_xss("TC-DWC-VIS-CREATE-NEG-03")

    def test_tc_dwc_vis_create_neg_04_cancel_and_idempotency(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-CREATE-NEG-04: Discard on Cancel and prevent duplicate submission on rapid double-click."""
        visit_page.verify_create_negative_cancel_and_double_click("TC-DWC-VIS-CREATE-NEG-04")
