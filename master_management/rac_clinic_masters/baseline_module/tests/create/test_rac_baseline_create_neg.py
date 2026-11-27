import pytest
from playwright.sync_api import Page
try:
    from master_management.rac_clinic_masters.baseline_module.pages.master_create_page import RacBaselineMasterPage
except ImportError:
    from pages.master_create_page import RacBaselineMasterPage


@pytest.fixture
def master_page(authenticated_page: Page) -> RacBaselineMasterPage:
    mp = RacBaselineMasterPage(authenticated_page)
    mp.navigate_to_baseline_master_home()
    return mp


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.create
@pytest.mark.negative
@pytest.mark.baseline
class TestRacBaselineCreateNeg:
    """Master Management negative test suite for RAC Clinic Create Baseline."""

    def test_tc_neg_rac_master_01_mandatory_empty_standalone(self, master_page: RacBaselineMasterPage):
        """TC-NEG-RAC-MASTER-01: Submit with mandatory field empty (Disease at Baseline — Standalone)."""
        master_page.execute_negative_validation("TC-NEG-RAC-MASTER-01")

    def test_tc_neg_rac_master_02_name_empty_parent_selected(self, master_page: RacBaselineMasterPage):
        """TC-NEG-RAC-MASTER-02: Submit with name empty & parent selected (Disease at Baseline — Dependent)."""
        master_page.execute_negative_validation("TC-NEG-RAC-MASTER-02")

    def test_tc_neg_rac_master_03_parent_unselected_name_filled(self, master_page: RacBaselineMasterPage):
        """TC-NEG-RAC-MASTER-03: Submit with parent unselected & name filled (Disease at Baseline — Dependent)."""
        master_page.execute_negative_validation("TC-NEG-RAC-MASTER-03")

    def test_tc_neg_rac_master_04_mandatory_empty_hetu_sevan(self, master_page: RacBaselineMasterPage):
        """TC-NEG-RAC-MASTER-04: Submit with mandatory field empty (Hetu Sevan)."""
        master_page.execute_negative_validation("TC-NEG-RAC-MASTER-04")

    def test_tc_neg_rac_master_05_mandatory_empty_physician_opinion(self, master_page: RacBaselineMasterPage):
        """TC-NEG-RAC-MASTER-05: Submit with mandatory field empty (Physician Opinion & RAC Management)."""
        master_page.execute_negative_validation("TC-NEG-RAC-MASTER-05")

    def test_tc_neg_rac_master_06_cancel_close_modal_without_saving(self, master_page: RacBaselineMasterPage):
        """TC-NEG-RAC-MASTER-06: Cancel / Close modal without saving."""
        master_page.execute_cancel_test("TC-NEG-RAC-MASTER-06")

    def test_tc_neg_rac_master_07_rapid_double_click_on_save(self, master_page: RacBaselineMasterPage):
        """TC-NEG-RAC-MASTER-07: Rapid double-click on Save button."""
        master_page.execute_double_click_test("TC-NEG-RAC-MASTER-07")
