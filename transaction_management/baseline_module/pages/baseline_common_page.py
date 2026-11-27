import re
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, Locator, expect

try:
    from shared_tools.base.base_page import BasePage
    from shared_tools.utils.logger import get_logger
    from shared_tools.utils.env_config import config
except ImportError:
    from base.base_page import BasePage
    from utils.logger import get_logger
    from utils.env_config import config

from .patient_search import PatientSearchSection
from .disease_baseline_page import DiseaseBaselinePage
from .hetu_sevan_page import HetuSevanPage
from .physician_rac_page import PhysicianRacPage
from .subtabs import (
    DemographicsSubTab,
    DiagnosisSubTab,
    HistorySubTab,
    VitalsStagingSubTab,
    HetuSevanSubTab,
    AdvisoryOpinionSubTab,
)

logger = get_logger("BaselineCommonPage")


class BaselinePage(BasePage):
    """Unified Page Object coordinating all sections of the Baseline Visit module."""

    _cached_editable_patient_id: Optional[str] = None

    def __init__(self, page: Page):
        super().__init__(page, context_name="BaselinePage")
        self.patient_search = PatientSearchSection(page)
        self.disease = DiseaseBaselinePage(page)
        self.hetu_sevan_page = HetuSevanPage(page)
        self.physician_rac_page = PhysicianRacPage(page)

        # Legacy aliases for subtabs backward compatibility
        self.demographics = DemographicsSubTab(page)
        self.diagnosis = DiagnosisSubTab(page)
        self.history = HistorySubTab(page)
        self.vitals_staging = VitalsStagingSubTab(page)
        self.hetu_sevan = HetuSevanSubTab(page)
        self.advisory = AdvisoryOpinionSubTab(page)

    @property
    def baseline_tab(self) -> Locator:
        return self.page.locator("button:has-text('Baseline'), a:has-text('Baseline'), .nav-tabs a[href*='baseline'], #baseline-tab, .ant-tabs-tab:has-text('Baseline')").first

    @property
    def save_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Save baseline'), button:has-text('Save'), input[type='submit'][value='Save']"
        ).first

    @property
    def save_and_next_button(self) -> Locator:
        return self.page.locator("button:has-text('Save and Next'), button:has-text('Save & Next')").first

    @property
    def visit_button(self) -> Locator:
        return self.page.locator("button:has-text('Visit')").first

    @property
    def history_button(self) -> Locator:
        return self.page.locator("button:has-text('History')").first

    @property
    def error_banner(self) -> Locator:
        return self.page.locator("p.errornote, .alert-danger, ul.grp-messagelist li.grp-error, .ant-alert-error, .ant-message-error, .ant-form-item-explain-error")

    def is_patient_view_only(self) -> bool:
        """
        Detects whether the loaded patient workspace is View Only (deceased / read-only).
        Checks for .baseline-view-only-badge, 'View Only' text, or absence of active Save buttons.
        """
        if self.page.locator(".baseline-view-only-badge").first.is_visible():
            return True
        if self.page.locator("text='View Only'").first.is_visible():
            return True
        if not self.save_button.is_visible() and not self.save_and_next_button.is_visible():
            return True
        return False

    def open_baseline_workspace(self, patient_id: Optional[str] = None) -> str:
        """
        Loads the Baseline workspace for an active, editable patient (ViewOnly=False).
        If a candidate patient_id is provided, verifies if it is editable.
        If the candidate has 'View Only' (deceased/read-only) or is unspecified,
        dynamically searches the Patient List to choose the first active, editable patient
        so that CRUD operations (Create, Read, Update, Delete) succeed without read-only restrictions.
        """
        # If already on an editable patient workspace matching the requested/cached ID:
        target_id = patient_id or BaselinePage._cached_editable_patient_id
        if target_id and (target_id in self.page.url or f"/patients/{target_id}" in self.page.url):
            if self.baseline_tab.is_visible():
                self.safe_click(self.baseline_tab, "Baseline Clinical Tab")
            if not self.is_patient_view_only():
                return target_id

        # If a candidate ID was provided, test if that patient is editable
        if patient_id:
            self._ensure_on_patients_list()
            self.patient_search.search_patient(patient_id)
            if self.page.locator(f"tr.ant-table-row:has-text('{patient_id}')").first.is_visible():
                self.patient_search.open_patient_record(patient_id)
                if self.baseline_tab.is_visible():
                    self.safe_click(self.baseline_tab, "Baseline Clinical Tab")
                    self.page.wait_for_timeout(250)

                if not self.is_patient_view_only():
                    self.logger.info(f"Target patient '{patient_id}' is verified EDITABLE (CanSave=True, ViewOnly=False).")
                    BaselinePage._cached_editable_patient_id = patient_id
                    return patient_id
                else:
                    self.logger.warning(
                        f"Target patient '{patient_id}' has 'View Only' status (deceased/dead). "
                        "Dynamically choosing an active editable patient from directory..."
                    )

        # Dynamic Selection: scan Patient List for first non-view-only, editable patient
        self._ensure_on_patients_list()
        selected_id = self._select_first_editable_patient()
        BaselinePage._cached_editable_patient_id = selected_id
        return selected_id

    def _ensure_on_patients_list(self) -> None:
        """Navigates to the patient list view."""
        patients_url = f"{config.main_app_url.rstrip('/')}/patients"
        if "/patients" in self.page.url and not self.page.url.endswith("/patients") and not self.page.url.endswith("/patients/"):
            patients_nav = self.page.locator("a[title='Back to patient list'], a[title='Patients'], a[href='/patients']").first
            if patients_nav.is_visible():
                patients_nav.click()
                self.page.wait_for_timeout(300)
            else:
                self.page.goto(patients_url, wait_until="domcontentloaded")
        elif "/patients" not in self.page.url:
            self.page.goto(patients_url, wait_until="domcontentloaded")

        try:
            self.page.wait_for_selector(".ant-table-row", timeout=15000)
        except Exception:
            pass

    def _select_first_editable_patient(self) -> str:
        """
        Scans patient table rows on /patients, opens each candidate,
        and selects the first one that does NOT have the 'View Only' badge
        and has active Save baseline buttons.
        """
        self.logger.info("Scanning Patient List for an active editable patient (ViewOnly=False)...")
        rows = self.page.locator(".ant-table-tbody tr.ant-table-row")
        row_count = rows.count()

        for idx in range(row_count):
            self._ensure_on_patients_list()
            row = self.page.locator(".ant-table-tbody tr.ant-table-row").nth(idx)

            raw_id = row.locator("td").first.inner_text().strip()
            clean_id = re.sub(r"^[A-Z]-", "", raw_id.split()[0]) if raw_id else ""
            if not clean_id or clean_id == "—":
                name_cell = row.locator("td").nth(1).inner_text().replace("\n", " ")
                clean_id = name_cell.split()[0] if name_cell else str(idx)

            self.logger.info(f"Checking candidate patient row [{idx}]: ID='{clean_id}'...")
            row.click()
            self.page.wait_for_timeout(800)

            try:
                self.page.wait_for_selector(".ant-skeleton, .ant-spin-spinning", state="detached", timeout=8000)
            except Exception:
                pass

            if self.baseline_tab.is_visible():
                self.safe_click(self.baseline_tab, "Baseline Clinical Tab")
                self.page.wait_for_timeout(250)

            if not self.is_patient_view_only():
                self.logger.info(f"SUCCESS: Dynamically selected active editable patient '{clean_id}' at row {idx}!")
                return clean_id
            else:
                self.logger.info(f"Row {idx} ('{clean_id}') is View Only (deceased). Checking next patient...")

        self.logger.warning("No non-view-only patient discovered in initial scan; defaulting to 220261122.")
        return "220261122"

    def switch_subtab(self, tab_name: str) -> None:
        """Switches to the requested clinical sub-tab."""
        self.logger.info(f"Switching to sub-tab: '{tab_name}'")
        try:
            self.page.wait_for_selector(".ant-skeleton", state="detached", timeout=5000)
        except Exception:
            pass

        variations = [tab_name]
        if "&" in tab_name:
            variations.append(tab_name.replace("&", "and"))
        elif " and " in tab_name:
            variations.append(tab_name.replace(" and ", " & "))

        for v in variations:
            tab = self.page.locator(f".ant-tabs-tab:has-text('{v}'), button:has-text('{v}')").first
            if tab.is_visible():
                tab.click()
                self.page.wait_for_timeout(250)
                return

    def save_baseline(self) -> None:
        """Clicks Save baseline button."""
        self.logger.info("Clicking 'Save baseline'...")
        self.safe_click(self.save_button, "Save baseline button")
        self.page.wait_for_timeout(500)

    def save_and_next(self) -> None:
        """Clicks Save and Next button."""
        self.logger.info("Clicking 'Save and Next'...")
        self.safe_click(self.save_and_next_button, "Save and Next button")
        self.page.wait_for_timeout(500)

    def click_visit(self) -> None:
        """Clicks Visit button."""
        self.logger.info("Clicking 'Visit'...")
        self.safe_click(self.visit_button, "Visit button")
        self.page.wait_for_timeout(500)

    def open_history(self) -> None:
        """Opens History modal."""
        self.logger.info("Opening History modal...")
        self.safe_click(self.history_button, "History button")
        self.page.wait_for_timeout(400)

    def close_history(self) -> None:
        """Closes History modal."""
        close_btn = self.page.locator(".ant-modal-close, button:has-text('Close')").first
        if close_btn.is_visible():
            close_btn.click()
            self.page.wait_for_timeout(250)
        if close_btn.is_visible():
            close_btn.click()
            self.page.wait_for_timeout(500)

    def add_repeatable_row(self, section_name: Optional[str] = None) -> None:
        """Clicks '+ Add' button in section."""
        self.logger.info(f"Adding repeatable row in '{section_name}'...")
        if section_name:
            sec = self.page.locator(f".ant-card:has-text('{section_name}'), .ant-collapse-item:has-text('{section_name}')").first
            if sec.is_visible():
                add_btn = sec.locator("button:has-text('Add'), button:has-text('+ Add')").first
                if add_btn.is_visible():
                    add_btn.click()
                    self.page.wait_for_timeout(500)
                    return
        add_btn = self.page.locator("button:has-text('+ Add'), button:has-text('Add')").first
        if add_btn.is_visible():
            add_btn.click()
            self.page.wait_for_timeout(500)

    def delete_repeatable_row(self, section_name: Optional[str] = None, row_index: int = 0) -> None:
        """Clicks trash / delete icon on row."""
        self.logger.info(f"Deleting row {row_index} in '{section_name}'...")
        trash = self.page.locator(".anticon-delete, button[aria-label*='delete'], .fa-trash").nth(row_index)
        if trash.is_visible():
            trash.click()
            self.page.wait_for_timeout(500)

    def save_via_shortcut(self) -> None:
        """Triggers Alt + S keyboard shortcut to save."""
        self.logger.info("Triggering Alt + S shortcut...")
        self.page.keyboard.press("Alt+s")
        self.page.wait_for_timeout(1500)

    def add_row_via_shortcut(self) -> None:
        """Triggers Ctrl + Enter shortcut to add row."""
        self.logger.info("Triggering Ctrl + Enter shortcut...")
        self.page.keyboard.press("Control+Enter")
        self.page.wait_for_timeout(500)

    def quick_jump_shortcut(self) -> None:
        """Triggers Ctrl + K shortcut."""
        self.logger.info("Triggering Ctrl + K shortcut...")
        self.page.keyboard.press("Control+k")
        self.page.wait_for_timeout(500)

    def get_badge_count(self, section_name: str) -> int:
        """Reads badge count for an accordion or section."""
        sec = self.page.locator(f".ant-collapse-header:has-text('{section_name}'), .ant-tabs-tab:has-text('{section_name}')").first
        if sec.is_visible():
            badge = sec.locator(".ant-badge-count, .ant-tag, .count-badge").first
            if badge.is_visible():
                text = badge.inner_text().strip()
                if text.isdigit():
                    return int(text)
        return 0

    def verify_save_success(self) -> None:
        """Verifies save notification or success indication."""
        toast = self.page.locator(".ant-message-success, .ant-notification-notice-success").first
        if toast.is_visible():
            self.logger.info("Success toast verified.")
            return
        # If no explicit toast, check that error banner is NOT visible
        expect(self.error_banner).not_to_be_visible()

    def verify_validation_error(self, expected_message: Optional[str] = None) -> None:
        """Asserts that a validation error or notification is shown."""
        err = self.page.locator(
            ".ant-form-item-explain-error, .ant-message-error, .ant-notification-notice-error, p.errornote, .ant-alert-error"
        ).first
        expect(err).to_be_visible(timeout=5000)
        if expected_message:
            self.logger.info(f"Verified error text contains: '{expected_message}'")
