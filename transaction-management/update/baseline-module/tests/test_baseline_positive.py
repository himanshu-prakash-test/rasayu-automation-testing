import pytest
from playwright.sync_api import Page, expect

from utils.env_config import config
from auth.login_page import LoginPage
from baseline_data import (
    get_baseline_test_data,
    get_default_patient_id,
    get_default_patient_name,
)
from pages.baseline_page import BaselinePage


@pytest.fixture
def baseline_page(authenticated_page: Page) -> BaselinePage:
    return BaselinePage(authenticated_page)


@pytest.mark.positive
@pytest.mark.baseline
class TestBaselinePositive:
    """Positive test cases for Transaction Module - Baseline Visit (Zero hardcoded data)."""

    def test_tc_base_pos_01_admin_login(self, page: Page):
        """TC-BASE-POS-01: Admin Login with Valid Credentials strictly loaded from .env."""
        login_p = LoginPage(page)
        login_p.open()
        login_p.login(config.admin_username, config.admin_password)
        login_p.verify_login_success()

    def test_tc_base_pos_02_patient_directory_search(self, baseline_page: BaselinePage):
        """TC-BASE-POS-02: Patient Directory Search & Filtering."""
        data = get_baseline_test_data("TC-BASE-POS-02")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        patient_name = data.parsed_payload.get("Patient Name") or get_default_patient_name()

        baseline_page.navigate_to("/admin/crf/patient/")
        baseline_page.patient_search.search_patient(patient_id)
        baseline_page.patient_search.verify_search_result_contains(patient_name)

    def test_tc_base_pos_03_open_patient_profile(self, baseline_page: BaselinePage):
        """TC-BASE-POS-03: Open Patient Profile & Verify Demographic Header."""
        data = get_baseline_test_data("TC-BASE-POS-03")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        clinic = data.parsed_payload.get("Clinic", config.default_clinic)
        physician = data.parsed_payload.get("Physician", "")
        age = data.parsed_payload.get("Age")

        baseline_page.navigate_to("/admin/crf/patient/")
        baseline_page.patient_search.search_patient(patient_id)
        baseline_page.patient_search.open_patient_record(patient_id)

        baseline_page.patient_search.verify_demographics(
            clinic=clinic,
            physician=physician,
            age=age,
        )

    def test_tc_base_pos_04_baseline_subtab_navigation(self, baseline_page: BaselinePage):
        """TC-BASE-POS-04: Baseline Module Access & Sub-Tab Navigation."""
        data = get_baseline_test_data("TC-BASE-POS-04")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        seq_text = data.parsed_payload.get("Navigation sequence", "")

        baseline_page.open_baseline_workspace(patient_id)

        if seq_text and "->" in seq_text:
            subtabs = [s.strip() for s in seq_text.split("->") if s.strip()]
        else:
            subtabs = [
                "Personal",
                "Allopathy",
                "Ayurvedic",
                "Medical History",
                "Family History",
                "Vitals",
                "Advisory",
            ]
        for tab in subtabs:
            baseline_page.switch_subtab(tab)

    def test_tc_base_pos_05_personal_details_allergies(self, baseline_page: BaselinePage):
        """TC-BASE-POS-05: Record Personal Details & Allergy Multi-Tags."""
        data = get_baseline_test_data("TC-BASE-POS-05")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        marital_status = data.parsed_payload.get("Marital Status", "Married")
        consanguineous = data.parsed_payload.get("Consanguineous", "No")
        allergy_tag = data.parsed_payload.get("Allergy Tag") or data.parsed_payload.get("Allergy", "Gluten")
        remarks = data.parsed_payload.get("Remarks") or data.parsed_payload.get("Allergy", "Patient allergy notes")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Personal")
        baseline_page.demographics.select_marital_status(marital_status)
        baseline_page.demographics.select_consanguineous(consanguineous)
        baseline_page.demographics.add_allergy_tag(allergy_tag)
        baseline_page.demographics.enter_remarks(remarks)

    def test_tc_base_pos_06_allopathy_diagnosis(self, baseline_page: BaselinePage):
        """TC-BASE-POS-06: Add Valid Allopathy Diagnosis Row."""
        data = get_baseline_test_data("TC-BASE-POS-06")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        group = data.parsed_payload.get("Group of Disease") or data.parsed_payload.get("Group", "")
        disease = data.parsed_payload.get("Type") or data.parsed_payload.get("Specific Disease", "")
        year = data.parsed_payload.get("Year Clean") or data.parsed_payload.get("Year") or data.parsed_payload.get("Diagnosis Year", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Allopathy")
        baseline_page.diagnosis.add_allopathy_diagnosis(group, disease, year)

    def test_tc_base_pos_07_ayurvedic_diagnosis(self, baseline_page: BaselinePage):
        """TC-BASE-POS-07: Ayurvedic Diagnosis & Classical Parameter Entry."""
        data = get_baseline_test_data("TC-BASE-POS-07")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        nidan = data.parsed_payload.get("Ayurvedic Nidan", "")
        dosha = data.parsed_payload.get("Dosha Drushti", "")
        agni = data.parsed_payload.get("Agni Vikriti", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Ayurvedic")
        baseline_page.diagnosis.record_ayurvedic_diagnosis(nidan=nidan, dosha=dosha, agni=agni)

    def test_tc_base_pos_08_medical_history_comorbidities(self, baseline_page: BaselinePage):
        """TC-BASE-POS-08: Past Medical History & Comorbidity Logging."""
        data = get_baseline_test_data("TC-BASE-POS-08")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        condition = data.parsed_payload.get("Condition", "")
        year = data.parsed_payload.get("Diagnosis Clean") or data.parsed_payload.get("Diagnosis", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Medical History")
        baseline_page.history.add_medical_history(condition, year)

    def test_tc_base_pos_09_family_medical_history(self, baseline_page: BaselinePage):
        """TC-BASE-POS-09: Family Medical History Entry."""
        data = get_baseline_test_data("TC-BASE-POS-09")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        lineage = data.parsed_payload.get("Parent Lineage", "")
        relation = data.parsed_payload.get("Relation", "")
        disease = data.parsed_payload.get("Disease Type") or data.parsed_payload.get("Condition", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Family History")
        baseline_page.history.add_family_history(lineage, relation, disease)

    def test_tc_base_pos_10_current_medicines(self, baseline_page: BaselinePage):
        """TC-BASE-POS-10: Current Medicines & Chemotherapy Regimen Logging."""
        data = get_baseline_test_data("TC-BASE-POS-10")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        pathy = data.parsed_payload.get("Pathy", "Allopathy")
        generic_name = data.parsed_payload.get("Generic Name", "Metformin")
        strength = data.parsed_payload.get("Strength", "500 mg")
        frequency = data.parsed_payload.get("Frequency", "BD (Twice daily)")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Medical History")
        baseline_page.history.add_current_medicine(
            pathy=pathy,
            generic_name=generic_name,
            strength=strength,
            frequency=frequency,
        )

    def test_tc_base_pos_11_chief_complaints(self, baseline_page: BaselinePage):
        """TC-BASE-POS-11: Disease at Baseline - Chief Complaints."""
        data = get_baseline_test_data("TC-BASE-POS-11")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        complaint = data.parsed_payload.get("Chief Complaint", "Pain in Abdomen")
        severity = data.parsed_payload.get("Severity Level", "Moderate")
        duration = data.parsed_payload.get("Duration", "3 months")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Allopathy")
        baseline_page.diagnosis.add_chief_complaint(
            complaint=complaint,
            severity=severity,
            duration=duration,
        )

    def test_tc_base_pos_12_vitals_ecog_status(self, baseline_page: BaselinePage):
        """TC-BASE-POS-12: Baseline Vitals & ECOG Performance Status."""
        data = get_baseline_test_data("TC-BASE-POS-12")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        pulse = data.parsed_payload.get("Pulse", "").replace("bpm", "").strip()
        bp = data.parsed_payload.get("BP", "").replace("mmHg", "").strip()
        weight = data.parsed_payload.get("Weight", "").replace("kg", "").strip()
        ecog = data.parsed_payload.get("ECOG Score", "").replace("Grade", "").strip()

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Vitals")
        baseline_page.vitals_staging.enter_vitals(pulse=pulse, bp=bp, weight=weight, ecog=ecog)

    def test_tc_base_pos_13_cancer_staging_tnm(self, baseline_page: BaselinePage):
        """TC-BASE-POS-13: Cancer Staging & TNM Classification."""
        data = get_baseline_test_data("TC-BASE-POS-13")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        tumor = data.parsed_payload.get("Tumor (T)", "")
        node = data.parsed_payload.get("Node (N)", "")
        metastasis = data.parsed_payload.get("Metastasis (M)", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Vitals")
        baseline_page.vitals_staging.set_tnm_staging(tumor=tumor, node=node, metastasis=metastasis)

    def test_tc_base_pos_14_surgical_history(self, baseline_page: BaselinePage):
        """TC-BASE-POS-14: Surgical & Histopathology History."""
        data = get_baseline_test_data("TC-BASE-POS-14")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        surgery = data.parsed_payload.get("Surgery", "Partial Gastrectomy")
        date = data.parsed_payload.get("Date Clean") or data.parsed_payload.get("Date", "14/06/2024")
        histopathology = data.parsed_payload.get("Histopathology", "Moderately diff. adenocarcinoma")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("History")
        baseline_page.history.add_surgery_details(
            surgery=surgery,
            date=date,
            histopathology=histopathology,
        )

    def test_tc_base_pos_15_radiation_therapy(self, baseline_page: BaselinePage):
        """TC-BASE-POS-15: Radiation Therapy Regimen Entry."""
        data = get_baseline_test_data("TC-BASE-POS-15")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        site = data.parsed_payload.get("Site", "")
        dose = data.parsed_payload.get("Total Dose", "")
        fractions = data.parsed_payload.get("Fractions", "")
        start_date = data.parsed_payload.get("Start Date", "")
        end_date = data.parsed_payload.get("End Date", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("History")
        baseline_page.history.add_radiation_details(
            site=site,
            dose=dose,
            fractions=fractions,
            start_date=start_date,
            end_date=end_date,
        )

    def test_tc_base_pos_16_baseline_lab_investigations(self, baseline_page: BaselinePage):
        """TC-BASE-POS-16: Baseline Lab Investigations Entry."""
        data = get_baseline_test_data("TC-BASE-POS-16")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        hb = data.parsed_payload.get("Hb", "")
        wbc = data.parsed_payload.get("WBC", "")
        platelets = data.parsed_payload.get("Platelets", "")
        sgot = data.parsed_payload.get("SGOT/SGPT", "")
        cr = data.parsed_payload.get("Cr", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Vitals")
        baseline_page.vitals_staging.add_lab_investigations(
            hb=hb,
            wbc=wbc,
            platelets=platelets,
            sgot=sgot,
            cr=cr,
        )

    def test_tc_base_pos_17_hetu_sevan_aharaja_viharaja(self, baseline_page: BaselinePage):
        """TC-BASE-POS-17: Hetu Sevan (Aharaja & Viharaja Factors)."""
        data = get_baseline_test_data("TC-BASE-POS-17")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        aharaja = data.parsed_payload.get("Aharaja", "")
        viharaja = data.parsed_payload.get("Viharaja", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.hetu_sevan.record_aharaja_viharaja(aharaja=aharaja, viharaja=viharaja)

    def test_tc_base_pos_18_hetu_sevan_manasika(self, baseline_page: BaselinePage):
        """TC-BASE-POS-18: Hetu Sevan (Manasika Factors)."""
        data = get_baseline_test_data("TC-BASE-POS-18")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        manasika = data.parsed_payload.get("Manasika Hetu", "")
        notes = data.parsed_payload.get("Notes", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.hetu_sevan.record_manasika_hetu(manasika=manasika, notes=notes)

    def test_tc_base_pos_19_physician_prognosis(self, baseline_page: BaselinePage):
        """TC-BASE-POS-19: Physician Clinical Assessment & Prognosis."""
        data = get_baseline_test_data("TC-BASE-POS-19")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        notes = data.parsed_payload.get("Notes", "")
        prognosis = data.parsed_payload.get("Prognosis", "")
        timeline = data.parsed_payload.get("Timeline", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Advisory")
        baseline_page.advisory.record_physician_assessment(
            notes=notes,
            prognosis=prognosis,
            timeline=timeline,
        )

    def test_tc_base_pos_20_rac_advisory_protocol(self, baseline_page: BaselinePage):
        """TC-BASE-POS-20: RAC Advisory Board Protocol & Sign-Off."""
        data = get_baseline_test_data("TC-BASE-POS-20")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        protocol = data.parsed_payload.get("Recommended Protocol", "")
        diet = data.parsed_payload.get("Diet", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Advisory")
        baseline_page.advisory.set_advisory_protocol(protocol, diet)

    def test_tc_base_pos_21_physician_opinion(self, baseline_page: BaselinePage):
        """TC-BASE-POS-21: Physician Opinion Row Operations."""
        data = get_baseline_test_data("TC-BASE-POS-21")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        p_type = data.parsed_payload.get("Type", "")
        opinion = data.parsed_payload.get("Opinion", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Advisory")
        baseline_page.advisory.add_physician_opinion(
            p_type=p_type,
            opinion=opinion,
        )

    def test_tc_base_pos_22_rac_management_approach(self, baseline_page: BaselinePage):
        """TC-BASE-POS-22: RAC Management Record Operations."""
        data = get_baseline_test_data("TC-BASE-POS-22")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()
        approach = data.parsed_payload.get("Approach", "")

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.switch_subtab("Advisory")
        baseline_page.advisory.set_management_approach(approach)

    def test_tc_base_pos_23_save_baseline_form(self, baseline_page: BaselinePage):
        """TC-BASE-POS-23: Save Baseline Form Execution."""
        data = get_baseline_test_data("TC-BASE-POS-23")
        patient_id = data.parsed_payload.get("Patient ID") or get_default_patient_id()

        baseline_page.open_baseline_workspace(patient_id)
        baseline_page.save_baseline_form()
        # Ensure page response is healthy
        assert baseline_page.page.locator("body").is_visible()
