"""
Master Management Automation Test Suite: RAC Clinic - Visit Masters Module (READ Positive Operations).
Validates TC-RAC-VISIT-READ-POS-01 to TC-RAC-VISIT-READ-POS-05.
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
@pytest.mark.positive
class TestRacVisitReadPos:
    """Positive test cases for RAC Visit Master Read operations (Zero Hardcoded Data)."""

    def test_tc_rac_visit_read_pos_01_accordion_badge_count_and_items(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-POS-01: Verify Visit Module sub-module accordion(s) expand/collapse properly and badge counts match."""
        visit_page.verify_visit_accordion_and_counts("TC-RAC-VISIT-READ-POS-01")

    def test_tc_rac_visit_read_pos_02_standard_table_columns_across_masters(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-POS-02: Verify selecting any Visit master renders the standard master table header and toolbar controls."""
        visit_page.verify_visit_table_columns("TC-RAC-VISIT-READ-POS-02")

    def test_tc_rac_visit_read_pos_03_sidebar_and_table_search(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-POS-03: Verify column alignment, null placeholders, and status pill styling in Visit master tables."""
        visit_page.verify_visit_search("TC-RAC-VISIT-READ-POS-03")

    def test_tc_rac_visit_read_pos_04_status_column_sort_and_pagination(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-POS-04: Verify that the Visit master table search bar filters rows accurately for exact, partial, and lowercase text."""
        visit_page.verify_visit_sort_and_pagination("TC-RAC-VISIT-READ-POS-04")

    def test_tc_rac_visit_read_pos_05_history_modal_and_reload_persistence(self, visit_page: VisitMasterPage):
        """TC-RAC-VISIT-READ-POS-05: Verify sorting, pagination, History modal, and post-reload persistence on Visit master tables."""
        visit_page.verify_visit_history_and_reload("TC-RAC-VISIT-READ-POS-05")
