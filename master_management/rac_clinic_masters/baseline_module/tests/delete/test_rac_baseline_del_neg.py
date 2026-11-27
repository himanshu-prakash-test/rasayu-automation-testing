import pytest
from playwright.sync_api import Page
try:
    from master_management.rac_clinic_masters.baseline_module.pages.master_delete_page import MasterDeletePage
except ImportError:
    from pages.master_delete_page import MasterDeletePage


@pytest.fixture
def delete_page(authenticated_page: Page) -> MasterDeletePage:
    dp = MasterDeletePage(authenticated_page)
    dp.navigate_to_masters_page()
    return dp


@pytest.mark.master
@pytest.mark.rac
@pytest.mark.negative
@pytest.mark.delete
@pytest.mark.baseline
class TestRacBaselineDeleteNeg:
    """Master Management negative test suite for RAC Clinic Delete Baseline."""

    def test_tc_del_neg_master_rac_01_cancel_deletion_via_button_x_or_esc(self, delete_page: MasterDeletePage):
        """TC-DEL-NEG-MASTER-RAC-01: Cancel deletion via Cancel button, X, or Esc."""
        delete_page.execute_negative_cancel_delete("TC-DEL-NEG-MASTER-RAC-01")

    def test_tc_del_neg_master_rac_02_attempt_delete_parent_linked_to_children(self, delete_page: MasterDeletePage):
        """TC-DEL-NEG-MASTER-RAC-02: Attempt to delete a parent record linked to child records."""
        delete_page.execute_negative_delete_parent_with_children("TC-DEL-NEG-MASTER-RAC-02")

    def test_tc_del_neg_master_rac_03_attempt_delete_record_linked_to_patient(self, delete_page: MasterDeletePage):
        """TC-DEL-NEG-MASTER-RAC-03: Attempt to delete a master record linked to Patient Records."""
        delete_page.execute_negative_delete_linked_patient_record("TC-DEL-NEG-MASTER-RAC-03")

    def test_tc_del_neg_master_rac_04_rapid_double_click_on_delete_confirmation(self, delete_page: MasterDeletePage):
        """TC-DEL-NEG-MASTER-RAC-04: Rapid double-click on Delete confirmation button."""
        delete_page.execute_negative_double_click_delete("TC-DEL-NEG-MASTER-RAC-04")

    def test_tc_del_neg_master_rac_05_switch_masters_after_delete_dialog(self, delete_page: MasterDeletePage):
        """TC-DEL-NEG-MASTER-RAC-05: Switch masters while Delete confirmation is open / after cancel."""
        delete_page.execute_negative_switch_masters_after_delete("TC-DEL-NEG-MASTER-RAC-05")
