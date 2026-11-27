"""
Master Management Automation Test Suite: DWC Clinic - Visit Masters Module (READ Positive Operations).
Validates TC-DWC-VIS-READ-POS-01 to TC-DWC-VIS-READ-POS-05.
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
@pytest.mark.positive
class TestDwcVisitReadPos:
    """Positive test cases for DWC Visit Master Read operations (Zero Hardcoded Data)."""

    def test_tc_dwc_vis_read_pos_01_accordion_badge_count(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-POS-01: Verify VISIT MASTERS accordion badge count and all 20 items under DWC."""
        visit_page.verify_visit_accordion_and_counts("TC-DWC-VIS-READ-POS-01")

    def test_tc_dwc_vis_read_pos_02_table_rows_and_placeholders(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-POS-02: Verify Symptom Master table rows and placeholder rendering."""
        visit_page.verify_visit_table_columns("TC-DWC-VIS-READ-POS-02")

    def test_tc_dwc_vis_read_pos_03_sidebar_and_table_search(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-POS-03: Search masters in sidebar and filter records in Symptom table."""
        visit_page.verify_visit_search("TC-DWC-VIS-READ-POS-03")

    def test_tc_dwc_vis_read_pos_04_pagination_and_sorting(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-POS-04: Verify Symptom Master pagination and Status column sorting."""
        visit_page.verify_visit_sort_and_pagination("TC-DWC-VIS-READ-POS-04")

    def test_tc_dwc_vis_read_pos_05_history_and_reload(self, visit_page: DwcVisitMasterPage):
        """TC-DWC-VIS-READ-POS-05: Verify Symptom Master History and active/inactive visibility in Patient Visit."""
        visit_page.verify_visit_history_and_reload("TC-DWC-VIS-READ-POS-05")
