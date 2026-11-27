"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (DELETE Positive Operations).
Validates TC-RAC-VISIT-DEL-POS-01 to TC-RAC-VISIT-DEL-POS-03.
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
@pytest.mark.positive
class TestRacVisitDeletePos:
    """Positive test cases for RAC Visit Master Delete operations (Zero Hardcoded Data)."""

    def test_tc_rac_visit_del_pos_01_delete_unused_record_reload_persistence(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-DEL-POS-01: Verify Delete confirmation dialog appears for a Visit Master record."""
        visit_page.delete_visit_record_with_reload("TC-RAC-VISIT-DEL-POS-01")

    def test_tc_rac_visit_del_pos_02_search_and_delete_entry_counter(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-DEL-POS-02: Delete an unused Active Visit Master record."""
        visit_page.search_and_delete_entry_counter("TC-RAC-VISIT-DEL-POS-02")

    def test_tc_rac_visit_del_pos_03_delete_record_history_audit_log(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-DEL-POS-03: Delete an unused Inactive Visit Master record."""
        visit_page.delete_and_verify_history("TC-RAC-VISIT-DEL-POS-03")
