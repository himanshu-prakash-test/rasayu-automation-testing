"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (UPDATE Negative Operations).
Validates TC-RAC-VISIT-UPD-NEG-01 to TC-RAC-VISIT-UPD-NEG-03.
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
@pytest.mark.negative
class TestRacVisitUpdateNeg:
    """Negative validation test cases for RAC Visit Master Update operations."""

    def test_tc_rac_visit_upd_neg_01_reject_blank_name_on_edit(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-UPD-NEG-01: Attempt to update a Visit Master record with the mandatory field cleared."""
        visit_page.verify_update_negative_blank_name("TC-RAC-VISIT-UPD-NEG-01")

    def test_tc_rac_visit_upd_neg_02_reject_rename_to_duplicate(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-UPD-NEG-02: Attempt to update a Visit Master record name to a duplicate value."""
        visit_page.verify_update_negative_duplicate_name("TC-RAC-VISIT-UPD-NEG-02")

    def test_tc_rac_visit_upd_neg_03_discard_unsaved_edit_on_cancel(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-UPD-NEG-03: Cancel Edit modal after modifying Visit Master fields."""
        visit_page.verify_update_negative_cancel_discard("TC-RAC-VISIT-UPD-NEG-03")
