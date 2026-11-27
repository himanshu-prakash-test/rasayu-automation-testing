import pytest
from playwright.sync_api import Page
try:
    from master_management.rac_clinic_masters.baseline_module.pages.master_update_page import MasterUpdatePage
except ImportError:
    from pages.master_update_page import MasterUpdatePage


@pytest.fixture
def update_page(authenticated_page: Page) -> MasterUpdatePage:
    up = MasterUpdatePage(authenticated_page)
    up.navigate_to_masters_page()
    return up


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.negative
@pytest.mark.update
@pytest.mark.baseline
class TestRacBaselineUpdateNeg:
    """Master Management negative test suite for RAC Clinic Update Baseline."""

    def test_tc_upd_neg_master_rac_01_clear_mandatory_field_standalone(self, update_page: MasterUpdatePage):
        """TC-UPD-NEG-MASTER-RAC-01: Clear mandatory field & save (Disease at Baseline — Standalone)."""
        update_page.execute_negative_clear_mandatory("TC-UPD-NEG-MASTER-RAC-01")

    def test_tc_upd_neg_master_rac_02_clear_mandatory_name_field_dependent(self, update_page: MasterUpdatePage):
        """TC-UPD-NEG-MASTER-RAC-02: Clear mandatory name field & save (Disease at Baseline — Dependent)."""
        update_page.execute_negative_clear_mandatory("TC-UPD-NEG-MASTER-RAC-02")

    def test_tc_upd_neg_master_rac_03_clear_mandatory_parent_dropdown_dependent(self, update_page: MasterUpdatePage):
        """TC-UPD-NEG-MASTER-RAC-03: Clear/deselect mandatory parent dropdown & save."""
        update_page.execute_negative_clear_parent("TC-UPD-NEG-MASTER-RAC-03")

    def test_tc_upd_neg_master_rac_04_clear_mandatory_field_hetu_sevan(self, update_page: MasterUpdatePage):
        """TC-UPD-NEG-MASTER-RAC-04: Clear mandatory field & save (Hetu Sevan)."""
        update_page.execute_negative_clear_mandatory("TC-UPD-NEG-MASTER-RAC-04")

    def test_tc_upd_neg_master_rac_05_clear_mandatory_field_physician_opinion(self, update_page: MasterUpdatePage):
        """TC-UPD-NEG-MASTER-RAC-05: Clear mandatory field & save (Physician Opinion & RAC Management)."""
        update_page.execute_negative_clear_mandatory("TC-UPD-NEG-MASTER-RAC-05")

    def test_tc_upd_neg_master_rac_06_cancel_close_edit_modal_without_saving(self, update_page: MasterUpdatePage):
        """TC-UPD-NEG-MASTER-RAC-06: Cancel / Close edit modal without saving."""
        update_page.execute_negative_cancel("TC-UPD-NEG-MASTER-RAC-06")

    def test_tc_upd_neg_master_rac_07_rapid_double_click_on_save_update(self, update_page: MasterUpdatePage):
        """TC-UPD-NEG-MASTER-RAC-07: Rapid double-click on Save button during update."""
        update_page.execute_negative_double_click("TC-UPD-NEG-MASTER-RAC-07")
