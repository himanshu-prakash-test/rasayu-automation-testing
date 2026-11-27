from typing import Optional
from playwright.sync_api import Page, Locator, expect
try:
    from shared_tools.base.base_page import BasePage
except ImportError:
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
        return self.page.locator("button:has-text('Baseline'), a:has-text('Baseline'), .nav-tabs a[href*='baseline'], #baseline-tab").first

    @property
    def save_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Save baseline'), button:has-text('Save'), input[type='submit'][name='_save'], input[value='Save']"
        ).first

    @property
    def file_input(self) -> Locator:
        return self.page.locator("input[type='file']")

    @property
    def error_banner(self) -> Locator:
        return self.page.locator("p.errornote, .alert-danger, ul.grp-messagelist li.grp-error, .ant-alert-error, .ant-message-error")

    def open_baseline_workspace(self, patient_id: Optional[str] = None) -> None:
        """Navigates to the patient directory, searches for the patient, and loads the profile."""
        if not patient_id:
            try:
                from transaction_management.baseline_module.baseline_data import get_default_patient_id
            except ImportError:
                from baseline_data import get_default_patient_id
            patient_id = get_default_patient_id()
        self.logger.info(f"Loading Baseline workspace for patient ID: '{patient_id}'")
        
        # Ensure we are on patient list view
        if "/patients" in self.page.url and not self.page.url.endswith("/patients") and not self.page.url.endswith("/patients/"):
            patients_nav = self.page.locator("a[title='Patients'], a[href='/patients']").first
            if patients_nav.is_visible():
                patients_nav.click()
                self.page.wait_for_timeout(1000)
        elif "/patients" not in self.page.url:
            patients_nav = self.page.locator("a[title='Patients'], a[href='/patients']").first
            if patients_nav.is_visible():
                patients_nav.click()
            else:
                from utils.env_config import config
                patients_url = f"{config.main_app_url.rstrip('/')}/patients"
                self.page.goto(patients_url, wait_until="domcontentloaded")
            self.page.wait_for_timeout(1000)

        self.patient_search.search_patient(patient_id)
        self.patient_search.open_patient_record(patient_id)

        # Ensure workspace skeleton is gone
        try:
            self.page.wait_for_selector(".ant-skeleton, .ant-spin-spinning", state="detached", timeout=25000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

        if self.baseline_tab.is_visible():
            self.safe_click(self.baseline_tab, "Baseline Clinical Tab")
            self.page.wait_for_timeout(500)

    def switch_subtab(self, tab_name: str) -> None:
        """Switches to the requested clinical sub-tab."""
        self.logger.info(f"Switching to sub-tab: '{tab_name}'")
        try:
            self.page.wait_for_selector(".ant-skeleton", state="detached", timeout=10000)
        except Exception:
            pass

        variations = [tab_name]
        if "&" in tab_name:
            variations.append(tab_name.replace("&", "and"))
        elif " and " in tab_name:
            variations.append(tab_name.replace(" and ", " & "))

        tab_found = False
        for v in variations:
            tab = self.page.locator(
                f"button:has-text('{v}'), a:has-text('{v}'), div[role='tab']:has-text('{v}')"
            ).first
            if tab.is_visible():
                self.safe_click(tab, f"Sub-tab ({v})")
                self.page.wait_for_timeout(600)
                tab_found = True
                break

        if not tab_found:
            section = self.page.locator(
                f"fieldset:has-text('{tab_name}'), h2:has-text('{tab_name}'), h3:has-text('{tab_name}'), .ant-collapse-header:has-text('{tab_name}')"
            ).first
            if section.is_visible():
                section.scroll_into_view_if_needed()
                self.page.wait_for_timeout(400)

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
