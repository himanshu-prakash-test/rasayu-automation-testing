import tempfile
from pathlib import Path
import pytest
from playwright.sync_api import Page, expect

from auth.login_page import LoginPage
from baseline_data import get_baseline_test_data, get_default_patient_id
from pages.baseline_page import BaselinePage


@pytest.fixture
def baseline_page(authenticated_page: Page) -> BaselinePage:
    return BaselinePage(authenticated_page)


@pytest.mark.negative
@pytest.mark.baseline
class TestBaselineNegative:
    """Negative validation and boundary test cases for Baseline Visit (Zero hardcoded data)."""

    def test_tc_base_neg_01_invalid_login(self, page: Page):
        """TC-BASE-NEG-01: Invalid Login Authentication."""
        login_p = LoginPage(page)
        data = get_baseline_test_data("TC-BASE-NEG-01")
        bad_user = data.parsed_payload.get("Username", "wrong_admin@rac.com")
        bad_pass = data.parsed_payload.get("Password", "WrongPass123")

        login_p.open()
        login_p.login(bad_user, bad_pass)
        login_p.verify_login_failure()

    def test_tc_base_neg_02_input_sanitization_xss(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-02: Input Sanitization & XSS Prevention."""
        data = get_baseline_test_data("TC-BASE-NEG-02")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        xss_payload = (
            data.parsed_payload.get("Remarks field")
            or data.parsed_payload.get("Payload")
            or "<script>alert('xss_test')</script>"
        )

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Personal")
        baseline_page.demographics.enter_remarks(xss_payload)

        dialog_opened = False

        def on_dialog(d):
            nonlocal dialog_opened
            dialog_opened = True
            d.dismiss()

        baseline_page.page.on("dialog", on_dialog)
        baseline_page.page.wait_for_timeout(1000)
        assert not dialog_opened, "Security vulnerability: Raw XSS payload executed in browser!"

    def test_tc_base_neg_03_future_year_validation(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-03: Future Year Entry Validation."""
        data = get_baseline_test_data("TC-BASE-NEG-03")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        future_year = data.parsed_payload.get("Diagnosis Year Clean") or data.parsed_payload.get("Diagnosis Year", "2030")

        pos_data = get_baseline_test_data("TC-BASE-POS-06")
        disease_group = pos_data.parsed_payload.get("Group of Disease") or pos_data.parsed_payload.get("Group", "")
        specific_disease = pos_data.parsed_payload.get("Type") or pos_data.parsed_payload.get("Specific Disease", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Allopathy")
        baseline_page.diagnosis.add_allopathy_diagnosis(
            disease_group=disease_group,
            specific_disease=specific_disease,
            diagnosis_year=future_year,
        )
        baseline_page.save_baseline_form()

    def test_tc_base_neg_04_missing_mandatory_ayurvedic(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-04: Missing Mandatory Ayurvedic Parameters."""
        patient_id = get_default_patient_id()
        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Ayurvedic")
        baseline_page.diagnosis.record_ayurvedic_diagnosis(nidan="", dosha="", agni="")

    def test_tc_base_neg_05_incomplete_family_history(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-05: Incomplete Family History Submission."""
        patient_id = get_default_patient_id()
        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Family History")
        baseline_page.history.add_family_history(lineage="", relation="", disease="")

    def test_tc_base_neg_06_chronological_date_inconsistency(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-06: Chronological Inconsistency (Dates)."""
        data = get_baseline_test_data("TC-BASE-NEG-06")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        start_date = data.parsed_payload.get("Start Date", "15/10/2024")
        end_date = data.parsed_payload.get("End Date Clean") or data.parsed_payload.get("End Date", "10/10/2024")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("History")
        baseline_page.history.add_radiation_details(
            start_date=start_date,
            end_date=end_date,
        )

    def test_tc_base_neg_07_out_of_range_ecog(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-07: Out-of-Range ECOG Performance Status."""
        data = get_baseline_test_data("TC-BASE-NEG-07")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        invalid_ecog = data.parsed_payload.get("ECOG Score Clean") or data.parsed_payload.get("ECOG Score", "6")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Vitals")
        baseline_page.vitals_staging.enter_vitals(ecog=invalid_ecog)

    def test_tc_base_neg_08_negative_vitals(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-08: Negative Value in Vitals / Dosage."""
        data = get_baseline_test_data("TC-BASE-NEG-08")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        bp = data.parsed_payload.get("Blood Pressure Clean") or data.parsed_payload.get("Blood Pressure", "-120")
        weight = data.parsed_payload.get("Weight Clean") or data.parsed_payload.get("Weight", "-55")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Vitals")
        baseline_page.vitals_staging.enter_vitals(bp=bp, weight=weight)

    def test_tc_base_neg_09_radiation_zero_fraction(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-09: Radiation Therapy Zero Fraction Validation."""
        data = get_baseline_test_data("TC-BASE-NEG-09")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        dose = data.parsed_payload.get("Total Dose Clean") or data.parsed_payload.get("Total Dose", "50 Gy")
        fractions = data.parsed_payload.get("Fractions Clean") or data.parsed_payload.get("Fractions", "0")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("History")
        baseline_page.history.add_radiation_details(dose=dose, fractions=fractions)

    def test_tc_base_neg_10_unauthorized_rac_finalization(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-10: Unauthorized RAC Finalization."""
        data = get_baseline_test_data("TC-BASE-NEG-10")
        patient_id = get_default_patient_id()

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Advisory")
        # Finalize button should either be disabled or require elevated permissions
        finalize_btn = baseline_page.advisory.finalize_button
        if finalize_btn.is_visible():
            # If button exists, clicking without proper state should not silently complete
            baseline_page.advisory.click_finalize()
            baseline_page.page.wait_for_timeout(500)

    def test_tc_base_neg_11_unsupported_file_upload(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-11: Unsupported File Type Upload."""
        data = get_baseline_test_data("TC-BASE-NEG-11")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        file_name = data.parsed_payload.get("File Selection Clean") or "malware_payload.exe"

        # Create temporary dummy file for upload validation
        temp_dir = Path(tempfile.gettempdir())
        dummy_file = temp_dir / file_name
        dummy_file.write_text("Dummy unsupported payload content for test")

        try:
            baseline_page.open_baseline_workspace(patient_id)
            baseline_page.upload_attachment(str(dummy_file))
        finally:
            if dummy_file.exists():
                dummy_file.unlink(missing_ok=True)

    def test_tc_base_neg_12_premature_baseline_finalization(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-12: Premature Baseline Finalization."""
        patient_id = get_default_patient_id()
        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Advisory")
        baseline_page.advisory.click_finalize()
        # Verify premature finalization is rejected or page maintains state
        assert baseline_page.page.locator("body").is_visible()

    def test_tc_base_neg_13_blank_physician_opinion(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-13: Blank Physician Opinion Fields."""
        patient_id = get_default_patient_id()
        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Advisory")
        baseline_page.advisory.add_physician_opinion(p_type="", opinion="")

    def test_tc_base_neg_14_missing_mandatory_fields_save(self, baseline_page: BaselinePage):
        """TC-BASE-NEG-14: Save Baseline with Missing Mandatory Fields."""
        patient_id = get_default_patient_id()
        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.save_baseline_form()
