"""
Disease Baseline Page Object:
Handles Tab 1 - Personal Medical Details, Baseline Allopathy Diagnosis,
Baseline Ayurvedic Diagnosis, Past Medical History / Comorbidities,
Current Medications, and Chemotherapy / Radiation.
"""
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, Locator, expect

try:
    from shared_tools.base.base_page import BasePage
    from shared_tools.utils.logger import get_logger
except ImportError:
    from base.base_page import BasePage
    from utils.logger import get_logger

logger = get_logger("DiseaseBaselinePage")


class DiseaseBaselinePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page, context_name="DiseaseBaselinePage")

    # ---------- Personal Medical Details ----------
    def fill_personal_details(self, data: Dict[str, Any]) -> None:
        """Fills Marital Status, Consanguineous, Agni Vikriti, and Remarks."""
        logger.info(f"Filling Personal Details: {data}")

        # Marital Status
        m_status = data.get("Marital Status")
        if m_status:
            m_loc = self.page.locator(
                f"label:has-text('{m_status}'), input[value*='{m_status}' i], select[name*='marital_status']"
            ).first
            if m_loc.is_visible():
                m_loc.click()

        # Consanguineous
        consang = data.get("Consanguineous")
        if consang:
            c_loc = self.page.locator(
                f".ant-form-item:has-text('Consanguineous') label:has-text('{consang}'), "
                f"select[name*='consanguineous'], input[name*='consanguineous'][value*='{consang}' i]"
            ).first
            if c_loc.is_visible():
                c_loc.click()

        # Agni Vikriti
        agni = data.get("Agni Vikriti")
        if agni:
            a_loc = self.page.locator(
                f"label:has-text('{agni}'), select[name*='agni'], input[placeholder*='Agni']"
            ).first
            if a_loc.is_visible():
                a_loc.click()

        # Remark
        remark = data.get("Remark") or data.get("Remarks")
        if remark:
            rem_loc = self.page.locator(
                ".ant-form-item:has-text('Remark') textarea, textarea[name*='remark'], #id_remarks"
            ).first
            if rem_loc.is_visible():
                self.safe_fill(rem_loc, remark, "Personal Remark")

    # ---------- Allergy & Multi-select Chips ----------
    def select_allergy_chips(self, allergy_types: List[str], reasons: List[str]) -> None:
        """Selects multiple chips for Allergy Type and Allergy Reason."""
        for a_type in allergy_types:
            self._select_chip_or_dropdown("Allergy", a_type)
        for reason in reasons:
            self._select_chip_or_dropdown("Reason", reason)

    # ---------- Allopathy Diagnosis ----------
    def fill_allopathy_diagnosis(self, diag_data: Dict[str, Any], row_index: int = 0) -> None:
        """Fills Group of Disease, Disease Type, Subtype, Stage, Date of Diagnosis, and Year."""
        logger.info(f"Filling Allopathy Diagnosis (row {row_index}): {diag_data}")

        # Group
        group = diag_data.get("Group")
        if group:
            self._select_ant_or_html_select("Group of Disease", group, row_index)

        # Type
        dtype = diag_data.get("Type")
        if dtype:
            self._select_ant_or_html_select("Disease Type", dtype, row_index)

        # Subtype
        subtype = diag_data.get("Subtype")
        if subtype:
            self._select_ant_or_html_select("Disease Subtype", subtype, row_index)

        # Stage
        stage = diag_data.get("Stage")
        if stage:
            self._select_ant_or_html_select("Stage", stage, row_index)

        # Diagnosis Date
        diag_date = diag_data.get("Diagnosis Date")
        if diag_date:
            date_loc = self.page.locator(
                "input[placeholder*='Date of Diagnosis'], input[placeholder*='Select date']"
            ).nth(row_index)
            if date_loc.is_visible():
                self.safe_fill(date_loc, diag_date, "Diagnosis Date")

        # Year
        year = diag_data.get("Year")
        if year:
            year_loc = self.page.locator("input[placeholder*='Year'], input[name*='year']").nth(row_index)
            if year_loc.is_visible():
                self.safe_fill(year_loc, str(year), "Diagnosis Year")

    # ---------- Comorbidities ----------
    def fill_comorbidity(self, name: str, since: str = "5", unit: str = "Years", row_index: int = 0) -> None:
        logger.info(f"Filling Comorbidity: {name}, {since} {unit}")
        c_input = self.page.locator("input[placeholder*='Comorbidity'], input[name*='comorbidity']").nth(row_index)
        if c_input.is_visible():
            self.safe_fill(c_input, name, "Comorbidity Name")

        since_input = self.page.locator("input[placeholder*='Since'], input[name*='since']").nth(row_index)
        if since_input.is_visible():
            self.safe_fill(since_input, str(since), "Comorbidity Since")

    # ---------- Current Medications ----------
    def fill_medication(self, pathy: str, name: str, strength: str, unit: str, freq: str, row_index: int = 0) -> None:
        """Fills Current Medications across Allopathy, Ayurvedic, or Other Pathies."""
        logger.info(f"Filling Medication ({pathy}): {name} {strength}{unit} {freq}")
        # Switch to pathy tab if exists
        pathy_tab = self.page.locator(f".ant-tabs-tab:has-text('{pathy}'), button:has-text('{pathy}')").first
        if pathy_tab.is_visible():
            pathy_tab.click()
            self.page.wait_for_timeout(300)

        name_input = self.page.locator("input[placeholder*='Medicine'], input[placeholder*='Name']").nth(row_index)
        if name_input.is_visible():
            self.safe_fill(name_input, name, "Medicine Name")

        strength_input = self.page.locator("input[placeholder*='Strength'], input[name*='strength']").nth(row_index)
        if strength_input.is_visible():
            self.safe_fill(strength_input, str(strength), "Medicine Strength")

        freq_input = self.page.locator("input[placeholder*='Frequency'], select[name*='frequency']").nth(row_index)
        if freq_input.is_visible():
            self.safe_fill(freq_input, freq, "Frequency")

    # ---------- Chemo & Radiation ----------
    def fill_chemo(self, cycle_no: str, day: str, start_date: str, end_date: str) -> None:
        logger.info(f"Filling Chemo: Cycle={cycle_no}, Day={day}, Start={start_date}, End={end_date}")
        c_no = self.page.locator("input[placeholder*='Cycle'], input[name*='cycle']").first
        if c_no.is_visible():
            self.safe_fill(c_no, str(cycle_no), "Chemo Cycle No")

        d_input = self.page.locator("input[placeholder*='Day'], input[name*='day']").first
        if d_input.is_visible():
            self.safe_fill(d_input, str(day), "Chemo Day")

        start_input = self.page.locator("input[placeholder*='Start Date']").first
        if start_input.is_visible():
            self.safe_fill(start_input, start_date, "Chemo Start Date")

        end_input = self.page.locator("input[placeholder*='End Date']").first
        if end_input.is_visible():
            self.safe_fill(end_input, end_date, "Chemo End Date")

    # ---------- Helpers ----------
    def _select_chip_or_dropdown(self, label: str, value: str) -> None:
        chip = self.page.locator(f".ant-tag:has-text('{value}'), button:has-text('{value}')").first
        if chip.is_visible():
            chip.click()
            return
        box = self.page.locator(f".ant-form-item:has-text('{label}') .ant-select, .ant-form-item:has-text('{label}') input").first
        if box.is_visible():
            box.click()
            self.page.wait_for_timeout(300)
            opt = self.page.locator(f".ant-select-item-option:has-text('{value}')").first
            if opt.is_visible():
                opt.click()

    def _select_ant_or_html_select(self, label: str, value: str, index: int = 0) -> None:
        container = self.page.locator(f".ant-form-item:has-text('{label}')").nth(index)
        if container.is_visible():
            select_box = container.locator(".ant-select").first
            if select_box.is_visible():
                select_box.click()
                self.page.wait_for_timeout(300)
                opt = self.page.locator(f".ant-select-item-option:has-text('{value}')").first
                if opt.is_visible():
                    opt.click()
                    return
        # Native select fallback
        native_sel = self.page.locator(f"select[name*='{label.lower().replace(' ', '_')}']").first
        if native_sel.is_visible():
            native_sel.select_option(label=value)
