"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (READ Negative Operations).
Validates TC-RAC-VISIT-READ-NEG-01 to TC-RAC-VISIT-READ-NEG-03.
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
@pytest.mark.read
@pytest.mark.negative
class TestRacVisitReadNeg:
    """Negative validation test cases for RAC Visit Master Read operations."""

    def test_tc_rac_visit_read_neg_01_empty_state_search(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-NEG-01: Verify empty-state UI handling when searching for a non-existent Visit master record."""
        visit_page.verify_visit_read_neg_empty_state("TC-RAC-VISIT-READ-NEG-01")

    def test_tc_rac_visit_read_neg_02_clinic_isolation_dwc_switch(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-NEG-02: Verify RAC Visit master records do not appear when switching to the DWC clinic toggle."""
        visit_page.verify_visit_clinic_isolation("TC-RAC-VISIT-READ-NEG-02")

    def test_tc_rac_visit_read_neg_03_restricted_role_access(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-NEG-03: Verify users without Master Management permissions cannot access Visit masters."""
        visit_page.verify_visit_read_only_access("TC-RAC-VISIT-READ-NEG-03")
