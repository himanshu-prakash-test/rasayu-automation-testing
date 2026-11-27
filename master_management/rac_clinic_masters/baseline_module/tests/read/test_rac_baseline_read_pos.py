"""
Master Management Automation Test Suite: RAC Clinic - Baseline Module (READ Positive Operations).
Validates TC-RAC-BASE-READ-POS-01 to TC-RAC-BASE-READ-POS-11.
Strictly 100% Zero Hardcoding: dynamically loads all data from 'readmaster-rac-baseline' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from master_management.rac_clinic_masters.baseline_module.pages.master_read_page import MasterReadPage
except ImportError:
    from ...pages.master_read_page import MasterReadPage


@pytest.fixture
def read_page(authenticated_page: Page) -> MasterReadPage:
    """Provides an authenticated MasterReadPage session on https://rasayu-stg.corecotechnologies.com/masters."""
    rp = MasterReadPage(authenticated_page)
    rp.navigate_to_masters_page()
    return rp


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.read
@pytest.mark.positive
@pytest.mark.baseline
class TestRacBaselineReadPos:
    """Master Management test suite for RAC Clinic Read Baseline (Positive Cases)."""

    def test_tc_rac_base_read_pos_01_verify_accordions_and_badge_counts(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-01: Verify all 3 sub-module accordions expand/collapse and badge counts match."""
        read_page.verify_accordions_and_counts("TC-RAC-BASE-READ-POS-01")

    def test_tc_rac_base_read_pos_02_verify_standard_master_table_controls(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-02: Verify header, toolbar controls, action buttons across sub-modules."""
        read_page.verify_standard_master_table_controls("TC-RAC-BASE-READ-POS-02")

    def test_tc_rac_base_read_pos_03_verify_columns_alignment_null_placeholders_status_pills(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-03: Verify column alignment, overflow scrolling, null placeholders (—), and status pills."""
        read_page.verify_columns_alignment_and_styling("TC-RAC-BASE-READ-POS-03")

    def test_tc_rac_base_read_pos_04_verify_data_persistence_after_page_reload(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-04: Verify master records across all three sub-modules remain intact after reload."""
        read_page.verify_persistence_after_reload("TC-RAC-BASE-READ-POS-04")

    def test_tc_rac_base_read_pos_05_verify_sidebar_search_filtering(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-05: Verify sidebar search input filters master links dynamically."""
        read_page.verify_sidebar_search_filtering("TC-RAC-BASE-READ-POS-05")

    def test_tc_rac_base_read_pos_06_verify_table_search_accuracy(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-06: Verify table search bar filters rows accurately for exact, partial, and lowercase text."""
        read_page.verify_table_search_accuracy("TC-RAC-BASE-READ-POS-06")

    def test_tc_rac_base_read_pos_07_verify_status_column_sorting(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-07: Verify ascending and descending UI sorting on Status column."""
        read_page.verify_status_sorting("TC-RAC-BASE-READ-POS-07")

    def test_tc_rac_base_read_pos_08_verify_pagination_controls(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-08: Verify page navigation arrows and page-size dropdown behavior."""
        read_page.verify_pagination_controls("TC-RAC-BASE-READ-POS-08")

    def test_tc_rac_base_read_pos_09_verify_history_modal_opens(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-09: Verify clicking History button opens audit log modal across sub-modules."""
        read_page.verify_history_modal_opens("TC-RAC-BASE-READ-POS-09")

    def test_tc_rac_base_read_pos_10_verify_active_masters_populate_patient_baseline_dropdowns(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-10: Verify Active RAC masters populate Patient Baseline dropdowns while Inactive are excluded."""
        read_page.verify_dropdown_sync_with_baseline("TC-RAC-BASE-READ-POS-10")

    def test_tc_rac_base_read_pos_11_verify_quick_jump_shortcut(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-POS-11: Verify Ctrl + K opens quick-navigation modal and jumps to target master."""
        read_page.verify_quick_jump_shortcut("TC-RAC-BASE-READ-POS-11")
