from typing import Optional
from playwright.sync_api import Page, Locator, expect
try:
    from shared_tools.base.base_page import BasePage
except ImportError:
    from base.base_page import BasePage


class PatientSearchSection(BasePage):
    """Handles patient directory filtering, search result selection, and demographic verification."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="PatientSearchSection")

    @property
    def search_input(self) -> Locator:
        return self.page.locator(
            "input[placeholder*='Search by name or ID'], #searchbar, input[name='q'], input[type='search']"
        ).first

    @property
    def search_button(self) -> Locator:
        return self.page.locator("input[type='submit'][value*='Search'], button:has-text('Search'), #searchbar + input").first

    def search_patient(self, query: str) -> None:
        """Enters search term into the directory searchbar and submits."""
        self.logger.info(f"Searching for patient: '{query}'")
        self.safe_fill(self.search_input, query, "Patient Searchbar")
        self.search_input.press("Enter")
        self.page.wait_for_timeout(300)

    def verify_search_result_contains(self, patient_identifier: str) -> None:
        """Asserts that the result table contains the given patient record."""
        self.logger.info(f"Verifying search results contain: '{patient_identifier}'")
        row = self.page.locator(
            f"tr.ant-table-row:has-text('{patient_identifier}'), table tbody tr:has-text('{patient_identifier}')"
        )
        expect(row.first).to_be_visible(timeout=10000)

    def open_patient_record(self, patient_identifier: str) -> None:
        """Opens the matching patient change form or clinical workspace."""
        self.logger.info(f"Opening patient record for '{patient_identifier}'")
        row = self.page.locator(
            f"tr.ant-table-row:has-text('{patient_identifier}'), table tbody tr:has-text('{patient_identifier}')"
        ).first
        expect(row).to_be_visible(timeout=10000)
        self.safe_click(row, f"Patient Record ({patient_identifier})")

        # Wait for patient clinical workspace to load and skeleton placeholders to detach
        self.logger.info(f"Waiting for patient workspace ({patient_identifier}) to fully render...")
        try:
            self.page.wait_for_selector(".ant-skeleton, .ant-spin-spinning", state="detached", timeout=15000)
        except Exception:
            pass
        self.page.wait_for_timeout(300)

    def verify_demographics(
        self,
        age: Optional[str] = None,
        gender: Optional[str] = None,
        clinic: Optional[str] = None,
        physician: Optional[str] = None,
    ) -> None:
        """Verifies clinical demographic header values."""
        self.logger.info("Verifying demographic panel details")
        self.page.wait_for_timeout(1000)
        body_text = self.page.locator("body").inner_text()
        if age:
            assert age.lower() in body_text.lower(), f"Expected age '{age}' not found in body text"
        if clinic:
            assert clinic.lower() in body_text.lower(), f"Expected clinic '{clinic}' not found"
        if physician:
            assert physician.lower() in body_text.lower(), f"Expected physician '{physician}' not found"
