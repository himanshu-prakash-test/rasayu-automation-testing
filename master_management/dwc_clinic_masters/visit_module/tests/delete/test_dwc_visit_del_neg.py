"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (DELETE Negative Operations).
Validates TC-DWC-VIS-DEL-NEG-01 to TC-DWC-VIS-DEL-NEG-03.
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
@pytest.mark.negative
class TestDwcVisitDeleteNeg:
    """Negative test cases for DWC Visit Master Delete operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_del_neg_01_cancel_confirmation_modal(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-DEL-NEG-01: Abort deletion when Cancel is clicked on confirmation modal."""
        visit_page.verify_delete_negative_cancel("TC-DWC-VIS-DEL-NEG-01")

    def test_tc_dwc_vis_del_neg_02_referential_integrity_in_use(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-DEL-NEG-02: Block deletion of Symptom linked to an existing DWC patient visit."""
        visit_page.verify_delete_negative_in_use("TC-DWC-VIS-DEL-NEG-02")

    def test_tc_dwc_vis_del_neg_03_rbac_delete_protection(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-DEL-NEG-03: Block delete action for non-admin / read-only user."""
        visit_page.verify_delete_negative_read_only("TC-DWC-VIS-DEL-NEG-03")
