from typing import Optional
from playwright.sync_api import Page, Locator, expect
from base.base_page import BasePage
from .patient_search import PatientSearchSection
from .subtabs import (
    DemographicsSubTab,
    DiagnosisSubTab,
    HistorySubTab,
    VitalsStagingSubTab,
    HetuSevanSubTab,
    AdvisoryOpinionSubTab,
)


class BaselinePage(BasePage):
    """Unified Page Object coordinating all sections of the Baseline Visit module."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="BaselinePage")
        self.patient_search = PatientSearchSection(page)
        self.demographics = DemographicsSubTab(page)
        self.diagnosis = DiagnosisSubTab(page)
        self.history = HistorySubTab(page)
        self.vitals_staging = VitalsStagingSubTab(page)
        self.hetu_sevan = HetuSevanSubTab(page)
        self.advisory = AdvisoryOpinionSubTab(page)

    @property
    def baseline_tab(self) -> Locator:
        return self.page.locator("a:has-text('Baseline'), .nav-tabs a[href*='baseline'], #baseline-tab")

    @property
    def save_button(self) -> Locator:
        return self.page.locator(
            "input[type='submit'][name='_save'], input[value='Save'], button:has-text('Save Baseline')"
        ).first

    @property
    def file_input(self) -> Locator:
        return self.page.locator("input[type='file']")

    @property
    def error_banner(self) -> Locator:
        return self.page.locator("p.errornote, .alert-danger, ul.grp-messagelist li.grp-error")

    def open_baseline_workspace(self, patient_id: Optional[str] = None) -> None:
        """Navigates to the patient directory, searches for the patient, and loads the profile."""
        if not patient_id:
            from baseline_data import get_default_patient_id
            patient_id = get_default_patient_id()
        self.logger.info(f"Loading Baseline workspace for patient ID: '{patient_id}'")
        self.navigate_to("/admin/crf/patient/")
        self.patient_search.search_patient(patient_id)
        self.patient_search.open_patient_record(patient_id)

        if self.baseline_tab.is_visible():
            self.safe_click(self.baseline_tab, "Baseline Clinical Tab")

    def switch_subtab(self, tab_name: str) -> None:
        """Switches to the requested clinical sub-tab."""
        self.logger.info(f"Switching to sub-tab: '{tab_name}'")
        tab = self.page.locator(f"a:has-text('{tab_name}'), button:has-text('{tab_name}')").first
        if tab.is_visible():
            self.safe_click(tab, f"Sub-tab ({tab_name})")
            self.page.wait_for_timeout(300)
        else:
            section = self.page.locator(
                f"fieldset:has-text('{tab_name}'), h2:has-text('{tab_name}'), h3:has-text('{tab_name}')"
            ).first
            if section.is_visible():
                section.scroll_into_view_if_needed()

    def save_baseline_form(self) -> None:
        """Triggers the form save execution."""
        self.logger.info("Executing save on Baseline form")
        self.safe_click(self.save_button, "Save Button")
        self.wait_for_ready()

    def upload_attachment(self, file_path: str) -> None:
        """Uploads a file attachment for validation checks."""
        self.logger.info(f"Uploading file: {file_path}")
        if self.file_input.is_visible():
            self.file_input.set_input_files(file_path)

    def verify_form_submission_error(self, expected_substring: Optional[str] = None) -> None:
        """Verifies that an error banner prevents invalid baseline form submission."""
        self.logger.info("Verifying form submission error banner")
        expect(self.error_banner.first).to_be_visible(timeout=8000)
        if expected_substring:
            text = self.error_banner.first.inner_text()
            assert expected_substring.lower() in text.lower()
