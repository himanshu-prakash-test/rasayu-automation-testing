"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (DELETE Negative Operations).
Validates TC-RAC-VISIT-DEL-NEG-01 to TC-RAC-VISIT-DEL-NEG-03.
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
@pytest.mark.delete
@pytest.mark.negative
class TestRacVisitDeleteNeg:
    """Negative validation test cases for RAC Visit Master Delete operations."""

    def test_tc_rac_visit_del_neg_01_cancel_deletion_confirmation(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-DEL-NEG-01: Cancel deletion in the Delete confirmation dialog for a Visit Master record."""
        visit_page.verify_delete_negative_cancel("TC-RAC-VISIT-DEL-NEG-01")

    def test_tc_rac_visit_del_neg_02_prevent_deletion_linked_patient_visit(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-DEL-NEG-02: Attempt to delete a Visit Master record referenced by existing Patient Visit transactions."""
        visit_page.verify_delete_negative_in_use("TC-RAC-VISIT-DEL-NEG-02")

    def test_tc_rac_visit_del_neg_03_restrict_delete_read_only_user(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-DEL-NEG-03: Verify History audit log entries for Visit Master records cannot be edited or deleted via UI."""
        visit_page.verify_delete_negative_read_only("TC-RAC-VISIT-DEL-NEG-03")
