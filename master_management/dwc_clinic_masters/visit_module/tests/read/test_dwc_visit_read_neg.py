"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (READ Negative Operations).
Validates TC-DWC-VIS-READ-NEG-01 to TC-DWC-VIS-READ-NEG-03.
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
@pytest.mark.read
@pytest.mark.negative
class TestDwcVisitReadNeg:
    """Negative test cases for DWC Visit Master Read operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_read_neg_01_empty_search_states(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-NEG-01: Verify empty state for non-matching table and sidebar search queries."""
        visit_page.verify_visit_read_neg_empty_state("TC-DWC-VIS-READ-NEG-01")

    def test_tc_dwc_vis_read_neg_02_clinic_isolation(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-NEG-02: Verify DWC-only record is isolated from RAC clinic view."""
        visit_page.verify_visit_clinic_isolation("TC-DWC-VIS-READ-NEG-02")

    def test_tc_dwc_vis_read_neg_03_rbac_route_access(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-NEG-03: Block direct URL access to Symptom Master for FRONT_DESK role."""
        visit_page.verify_visit_read_only_access("TC-DWC-VIS-READ-NEG-03")
