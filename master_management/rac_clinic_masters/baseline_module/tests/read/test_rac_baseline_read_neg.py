"""
Master Management Automation Test Suite: RAC Clinic - Baseline Module (READ Negative Operations).
Validates TC-RAC-BASE-READ-NEG-01 to TC-RAC-BASE-READ-NEG-06.
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
@pytest.mark.negative
@pytest.mark.baseline
class TestRacBaselineReadNeg:
    """Master Management negative test suite for RAC Clinic Read Baseline."""

    def test_tc_rac_base_read_neg_01_table_search_empty_state(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-NEG-01: Empty-state UI handling when searching for non-existent record in master table."""
        read_page.verify_table_empty_state("TC-RAC-BASE-READ-NEG-01")

    def test_tc_rac_base_read_neg_02_sidebar_search_empty_state(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-NEG-02: Sidebar empty-state handling and recovery when searching for unknown master name."""
        read_page.verify_sidebar_empty_state("TC-RAC-BASE-READ-NEG-02")

    def test_tc_rac_base_read_neg_03_search_input_sanitization(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-NEG-03: Padded spaces and HTML/script strings in search inputs are sanitized safely."""
        read_page.verify_search_input_sanitization("TC-RAC-BASE-READ-NEG-03")

    def test_tc_rac_base_read_neg_04_history_modal_readonly_enforcement(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-NEG-04: Audit entries inside History modal cannot be edited or deleted."""
        read_page.verify_history_modal_readonly("TC-RAC-BASE-READ-NEG-04")

    def test_tc_rac_base_read_neg_05_clinic_isolation_dwc_switch(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-NEG-05: RAC-specific master records do not appear when switching to DWC clinic toggle."""
        read_page.verify_clinic_isolation_dwc_switch("TC-RAC-BASE-READ-NEG-05")

    def test_tc_rac_base_read_neg_06_unauthorized_master_access_rbac(self, read_page: MasterReadPage):
        """TC-RAC-BASE-READ-NEG-06: Users without Master Management permissions cannot access Masters in UI."""
        read_page.verify_restricted_rbac_access("TC-RAC-BASE-READ-NEG-06")
