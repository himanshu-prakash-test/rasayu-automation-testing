from typing import Optional, Dict
from playwright.sync_api import Page, Locator, expect
try:
    from shared_tools.base.base_page import BasePage
except ImportError:
    from base.base_page import BasePage


class DemographicsSubTab(BasePage):
    """Personal Details, Marital Status, Allergies, and Diet."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="DemographicsSubTab")

    @property
    def marital_status_select(self) -> Locator:
        return self.page.locator("select[name*='marital_status'], #id_marital_status")

    @property
    def consanguineous_select(self) -> Locator:
        return self.page.locator("select[name*='consanguineous'], #id_consanguineous")

    @property
    def remarks_input(self) -> Locator:
        return self.page.locator("textarea[name*='remarks'], textarea[name*='notes'], #id_remarks")

    @property
    def allergy_input(self) -> Locator:
        return self.page.locator("input[name*='allergy'], .select2-search__field, #id_allergies")

    def select_marital_status(self, status: str) -> None:
        if self.marital_status_select.is_visible():
            self.safe_select(self.marital_status_select, status, "Marital Status")
        else:
            radio = self.page.locator(f"input[type='radio'][value*='{status}' i], label:has-text('{status}')").first
            if radio.is_visible():
                radio.click()

    def select_consanguineous(self, value: str) -> None:
        if self.consanguineous_select.is_visible():
            self.safe_select(self.consanguineous_select, value, "Consanguineous")

    def add_allergy_tag(self, tag: str) -> None:
        self.logger.info(f"Adding allergy tag: '{tag}'")
        if self.allergy_input.is_visible():
            self.safe_fill(self.allergy_input, tag, "Allergy Tag")
            self.allergy_input.press("Enter")

    def enter_remarks(self, text: str) -> None:
        if self.remarks_input.is_visible():
            self.safe_fill(self.remarks_input, text, "Remarks")


class DiagnosisSubTab(BasePage):
    """Allopathy and Ayurvedic Diagnosis entries, Chief Complaints & validation."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="DiagnosisSubTab")

    @property
    def disease_group_select(self) -> Locator:
        return self.page.locator("select[name*='disease_group'], select[name*='group_of_disease']")

    @property
    def specific_disease_select(self) -> Locator:
        return self.page.locator("select[name*='disease'], select[name*='allopathy_disease']")

    @property
    def diagnosis_year_input(self) -> Locator:
        return self.page.locator("input[name*='year'], input[name*='diagnosis_year']")

    @property
    def add_diagnosis_btn(self) -> Locator:
        return self.page.locator("button:has-text('Add Diagnosis'), .grp-add-handler, a:has-text('Add another')").first

    @property
    def nidan_select(self) -> Locator:
        return self.page.locator("select[name*='nidan'], select[name*='ayurvedic_nidan']")

    @property
    def dosha_select(self) -> Locator:
        return self.page.locator("select[name*='dosha'], select[name*='dosha_drushti']")

    @property
    def agni_select(self) -> Locator:
        return self.page.locator("select[name*='agni'], select[name*='agni_vikriti']")

    @property
    def chief_complaint_input(self) -> Locator:
        return self.page.locator("input[name*='complaint'], textarea[name*='complaint'], select[name*='complaint']")

    @property
    def severity_select(self) -> Locator:
        return self.page.locator("select[name*='severity'], input[name*='severity']")

    @property
    def duration_input(self) -> Locator:
        return self.page.locator("input[name*='duration']")

    @property
    def error_box(self) -> Locator:
        return self.page.locator(".grp-errors, .errorlist, p.errornote, span.help-inline.error")

    def add_allopathy_diagnosis(self, disease_group: str, specific_disease: str, diagnosis_year: str) -> None:
        self.logger.info(f"Adding Allopathy Diagnosis: {disease_group} -> {specific_disease} ({diagnosis_year})")
        if self.disease_group_select.is_visible():
            self.safe_select(self.disease_group_select, disease_group, "Disease Group")
        if self.specific_disease_select.is_visible():
            self.safe_select(self.specific_disease_select, specific_disease, "Specific Disease")
        if self.diagnosis_year_input.is_visible():
            self.safe_fill(self.diagnosis_year_input, diagnosis_year, "Diagnosis Year")
        if self.add_diagnosis_btn.is_visible():
            self.safe_click(self.add_diagnosis_btn, "Add Diagnosis Button")

    def record_ayurvedic_diagnosis(
        self,
        nidan: Optional[str] = None,
        dosha: Optional[str] = None,
        agni: Optional[str] = None
    ) -> None:
        self.logger.info(f"Recording Ayurvedic Diagnosis: Nidan={nidan}, Dosha={dosha}, Agni={agni}")
        if nidan and self.nidan_select.is_visible():
            self.safe_select(self.nidan_select, nidan, "Ayurvedic Nidan")
        if dosha and self.dosha_select.is_visible():
            self.safe_select(self.dosha_select, dosha, "Dosha Drushti")
        if agni and self.agni_select.is_visible():
            self.safe_select(self.agni_select, agni, "Agni Vikriti")

    def add_chief_complaint(self, complaint: str, severity: str, duration: str) -> None:
        self.logger.info(f"Adding Chief Complaint: {complaint} ({severity}, {duration})")
        if complaint and self.chief_complaint_input.is_visible():
            self.safe_fill(self.chief_complaint_input, complaint, "Chief Complaint")
        if severity and self.severity_select.is_visible():
            self.safe_select(self.severity_select, severity, "Severity")
        if duration and self.duration_input.is_visible():
            self.safe_fill(self.duration_input, duration, "Duration")

    def verify_validation_error(self, expected_substring: str) -> None:
        expect(self.error_box.first).to_be_visible(timeout=5000)
        assert expected_substring.lower() in self.error_box.first.inner_text().lower()


class HistorySubTab(BasePage):
    """Medical, Family, Surgical, Chemotherapy, and Radiation Oncology History."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="HistorySubTab")

    @property
    def condition_input(self) -> Locator:
        return self.page.locator("input[name*='condition'], select[name*='condition']")

    @property
    def condition_year_input(self) -> Locator:
        return self.page.locator("input[name*='onset'], input[name*='diagnosis_month_year']")

    @property
    def lineage_select(self) -> Locator:
        return self.page.locator("select[name*='lineage'], select[name*='parent_lineage']")

    @property
    def relation_select(self) -> Locator:
        return self.page.locator("select[name*='relation']")

    @property
    def family_disease_input(self) -> Locator:
        return self.page.locator("input[name*='disease'], select[name*='family_disease']")

    @property
    def medicine_pathy_select(self) -> Locator:
        return self.page.locator("select[name*='pathy']")

    @property
    def generic_name_input(self) -> Locator:
        return self.page.locator("input[name*='generic_name'], input[name*='medicine']")

    @property
    def strength_input(self) -> Locator:
        return self.page.locator("input[name*='strength'], input[name*='dosage']")

    @property
    def frequency_select(self) -> Locator:
        return self.page.locator("select[name*='frequency'], input[name*='frequency']")

    @property
    def surgery_input(self) -> Locator:
        return self.page.locator("input[name*='surgery'], select[name*='surgery']")

    @property
    def surgery_date_input(self) -> Locator:
        return self.page.locator("input[name*='surgery_date'], input[name*='date_of_surgery']")

    @property
    def histopathology_input(self) -> Locator:
        return self.page.locator("textarea[name*='histopathology'], input[name*='histopathology']")

    @property
    def radiation_site_input(self) -> Locator:
        return self.page.locator("input[name*='site'], select[name*='radiation_site']")

    @property
    def dose_input(self) -> Locator:
        return self.page.locator("input[name*='dose'], input[name*='total_dose']")

    @property
    def fractions_input(self) -> Locator:
        return self.page.locator("input[name*='fraction'], input[name*='fractions']")

    @property
    def start_date_input(self) -> Locator:
        return self.page.locator("input[name*='start_date'], input[name*='radiation_start']")

    @property
    def end_date_input(self) -> Locator:
        return self.page.locator("input[name*='end_date'], input[name*='radiation_end']")

    def add_medical_history(self, condition: str, year: str) -> None:
        self.logger.info(f"Adding Medical History: {condition} ({year})")
        if self.condition_input.is_visible():
            self.safe_fill(self.condition_input, condition, "Condition")
        if self.condition_year_input.is_visible():
            self.safe_fill(self.condition_year_input, year, "Onset Year")

    def add_family_history(self, lineage: str, relation: str, disease: str) -> None:
        self.logger.info(f"Adding Family History: {lineage} - {relation} - {disease}")
        if lineage and self.lineage_select.is_visible():
            self.safe_select(self.lineage_select, lineage, "Lineage")
        if relation and self.relation_select.is_visible():
            self.safe_select(self.relation_select, relation, "Relation")
        if disease and self.family_disease_input.is_visible():
            self.safe_fill(self.family_disease_input, disease, "Disease")

    def add_current_medicine(self, pathy: str, generic_name: str, strength: str, frequency: str) -> None:
        self.logger.info(f"Adding Current Medicine: {generic_name} ({strength}, {frequency})")
        if pathy and self.medicine_pathy_select.is_visible():
            self.safe_select(self.medicine_pathy_select, pathy, "Pathy")
        if generic_name and self.generic_name_input.is_visible():
            self.safe_fill(self.generic_name_input, generic_name, "Generic Name")
        if strength and self.strength_input.is_visible():
            self.safe_fill(self.strength_input, strength, "Strength")
        if frequency and self.frequency_select.is_visible():
            self.safe_select(self.frequency_select, frequency, "Frequency")

    def add_surgery_details(self, surgery: str, date: str, histopathology: str) -> None:
        self.logger.info(f"Adding Surgical History: {surgery} on {date}")
        if surgery and self.surgery_input.is_visible():
            self.safe_fill(self.surgery_input, surgery, "Surgery")
        if date and self.surgery_date_input.is_visible():
            self.safe_fill(self.surgery_date_input, date, "Surgery Date")
        if histopathology and self.histopathology_input.is_visible():
            self.safe_fill(self.histopathology_input, histopathology, "Histopathology")

    def add_radiation_details(
        self,
        site: Optional[str] = None,
        dose: Optional[str] = None,
        fractions: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> None:
        self.logger.info("Adding Radiation Oncology details")
        if site and self.radiation_site_input.is_visible():
            self.safe_fill(self.radiation_site_input, site, "Site")
        if dose and self.dose_input.is_visible():
            self.safe_fill(self.dose_input, dose, "Dose")
        if fractions and self.fractions_input.is_visible():
            self.safe_fill(self.fractions_input, fractions, "Fractions")
        if start_date and self.start_date_input.is_visible():
            self.safe_fill(self.start_date_input, start_date, "Start Date")
        if end_date and self.end_date_input.is_visible():
            self.safe_fill(self.end_date_input, end_date, "End Date")


class VitalsStagingSubTab(BasePage):
    """Vitals, Hemodynamics, ECOG score, Staging & Lab investigations."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="VitalsStagingSubTab")

    @property
    def pulse_input(self) -> Locator:
        return self.page.locator("input[name*='pulse']")

    @property
    def bp_input(self) -> Locator:
        return self.page.locator("input[name*='bp'], input[name*='blood_pressure']")

    @property
    def weight_input(self) -> Locator:
        return self.page.locator("input[name*='weight']")

    @property
    def ecog_input(self) -> Locator:
        return self.page.locator("input[name*='ecog'], select[name*='ecog']")

    @property
    def tumor_select(self) -> Locator:
        return self.page.locator("select[name*='tumor'], select[name*='tnm_t']")

    @property
    def node_select(self) -> Locator:
        return self.page.locator("select[name*='node'], select[name*='tnm_n']")

    @property
    def metastasis_select(self) -> Locator:
        return self.page.locator("select[name*='metastasis'], select[name*='tnm_m']")

    @property
    def hb_input(self) -> Locator:
        return self.page.locator("input[name*='hb'], input[name*='hemoglobin']")

    @property
    def wbc_input(self) -> Locator:
        return self.page.locator("input[name*='wbc'], input[name*='leukocytes']")

    @property
    def platelets_input(self) -> Locator:
        return self.page.locator("input[name*='platelet']")

    @property
    def sgot_input(self) -> Locator:
        return self.page.locator("input[name*='sgot'], input[name*='ast']")

    @property
    def cr_input(self) -> Locator:
        return self.page.locator("input[name*='creatinine'], input[name*='cr']")

    def enter_vitals(
        self,
        pulse: Optional[str] = None,
        bp: Optional[str] = None,
        weight: Optional[str] = None,
        ecog: Optional[str] = None
    ) -> None:
        self.logger.info("Entering vital signs")
        if pulse and self.pulse_input.is_visible():
            self.safe_fill(self.pulse_input, pulse, "Pulse")
        if bp and self.bp_input.is_visible():
            self.safe_fill(self.bp_input, bp, "Blood Pressure")
        if weight and self.weight_input.is_visible():
            self.safe_fill(self.weight_input, weight, "Weight")
        if ecog and self.ecog_input.is_visible():
            tag = self.ecog_input.first.evaluate("el => el.tagName.toLowerCase()")
            if tag == "select":
                self.safe_select(self.ecog_input, ecog, "ECOG Select")
            else:
                self.safe_fill(self.ecog_input, ecog, "ECOG Input")

    def set_tnm_staging(self, tumor: str, node: str, metastasis: str) -> None:
        self.logger.info(f"Setting TNM: T={tumor}, N={node}, M={metastasis}")
        if self.tumor_select.is_visible():
            self.safe_select(self.tumor_select, tumor, "Tumor")
        if self.node_select.is_visible():
            self.safe_select(self.node_select, node, "Node")
        if self.metastasis_select.is_visible():
            self.safe_select(self.metastasis_select, metastasis, "Metastasis")

    def add_lab_investigations(
        self,
        hb: str = "",
        wbc: str = "",
        platelets: str = "",
        sgot: str = "",
        cr: str = ""
    ) -> None:
        self.logger.info(f"Adding Lab Investigations: Hb={hb}, WBC={wbc}, Plt={platelets}")
        if hb and self.hb_input.is_visible():
            self.safe_fill(self.hb_input, hb, "Hemoglobin")
        if wbc and self.wbc_input.is_visible():
            self.safe_fill(self.wbc_input, wbc, "WBC")
        if platelets and self.platelets_input.is_visible():
            self.safe_fill(self.platelets_input, platelets, "Platelets")
        if sgot and self.sgot_input.is_visible():
            self.safe_fill(self.sgot_input, sgot, "SGOT/SGPT")
        if cr and self.cr_input.is_visible():
            self.safe_fill(self.cr_input, cr, "Creatinine")


class HetuSevanSubTab(BasePage):
    """Hetu Sevan (Etiological factors: Aharaja, Viharaja, and Manasika)."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="HetuSevanSubTab")

    @property
    def aharaja_input(self) -> Locator:
        return self.page.locator("textarea[name*='aharaja'], input[name*='aharaja'], select[name*='aharaja']")

    @property
    def viharaja_input(self) -> Locator:
        return self.page.locator("textarea[name*='viharaja'], input[name*='viharaja'], select[name*='viharaja']")

    @property
    def manasika_input(self) -> Locator:
        return self.page.locator("textarea[name*='manasika'], input[name*='manasika'], select[name*='manasika']")

    @property
    def notes_input(self) -> Locator:
        return self.page.locator("textarea[name*='hetu_notes'], textarea[name*='notes']")

    def record_aharaja_viharaja(self, aharaja: str, viharaja: str) -> None:
        self.logger.info(f"Recording Aharaja & Viharaja: {aharaja} | {viharaja}")
        if aharaja and self.aharaja_input.is_visible():
            self.safe_fill(self.aharaja_input, aharaja, "Aharaja Factors")
        if viharaja and self.viharaja_input.is_visible():
            self.safe_fill(self.viharaja_input, viharaja, "Viharaja Factors")

    def record_manasika_hetu(self, manasika: str, notes: str = "") -> None:
        self.logger.info(f"Recording Manasika Hetu: {manasika}")
        if manasika and self.manasika_input.is_visible():
            self.safe_fill(self.manasika_input, manasika, "Manasika Factors")
        if notes and self.notes_input.is_visible():
            self.safe_fill(self.notes_input, notes, "Hetu Notes")


class AdvisoryOpinionSubTab(BasePage):
    """RAC Protocol, Diet, Second Opinion, and Management Approach."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="AdvisoryOpinionSubTab")

    @property
    def protocol_select(self) -> Locator:
        return self.page.locator("select[name*='protocol'], select[name*='rcc_protocol']")

    @property
    def diet_input(self) -> Locator:
        return self.page.locator("textarea[name*='diet'], textarea[name*='lifestyle']")

    @property
    def physician_type_select(self) -> Locator:
        return self.page.locator("select[name*='physician_type']")

    @property
    def opinion_input(self) -> Locator:
        return self.page.locator("textarea[name*='opinion']")

    @property
    def approach_select(self) -> Locator:
        return self.page.locator("select[name*='approach'], select[name*='therapy_approach']")

    @property
    def prognosis_select(self) -> Locator:
        return self.page.locator("select[name*='prognosis'], input[name*='prognosis']")

    @property
    def timeline_input(self) -> Locator:
        return self.page.locator("input[name*='timeline'], select[name*='timeline']")

    @property
    def finalize_button(self) -> Locator:
        return self.page.locator("button:has-text('Finalize'), input[value*='Finalize']")

    def set_advisory_protocol(self, protocol: str, diet: str) -> None:
        self.logger.info(f"Setting Advisory Protocol: '{protocol}'")
        if self.protocol_select.is_visible():
            self.safe_select(self.protocol_select, protocol, "Protocol")
        if self.diet_input.is_visible():
            self.safe_fill(self.diet_input, diet, "Diet Plan")

    def add_physician_opinion(self, p_type: str, opinion: str) -> None:
        self.logger.info(f"Adding Physician Opinion ({p_type})")
        if p_type and self.physician_type_select.is_visible():
            self.safe_select(self.physician_type_select, p_type, "Physician Type")
        if opinion and self.opinion_input.is_visible():
            self.safe_fill(self.opinion_input, opinion, "Opinion")

    def set_management_approach(self, approach: str) -> None:
        self.logger.info(f"Setting Management Approach: '{approach}'")
        if self.approach_select.is_visible():
            self.safe_select(self.approach_select, approach, "Approach")

    def record_physician_assessment(self, notes: str, prognosis: str, timeline: str = "") -> None:
        self.logger.info(f"Recording Physician Assessment: {prognosis} ({timeline})")
        if notes and self.opinion_input.is_visible():
            self.safe_fill(self.opinion_input, notes, "Assessment Notes")
        if prognosis and self.prognosis_select.is_visible():
            self.safe_select(self.prognosis_select, prognosis, "Prognosis")
        if timeline and self.timeline_input.is_visible():
            self.safe_fill(self.timeline_input, timeline, "Timeline")

    def click_finalize(self) -> None:
        self.logger.info("Clicking Finalize Baseline button")
        if self.finalize_button.is_visible():
            self.safe_click(self.finalize_button, "Finalize Button")
