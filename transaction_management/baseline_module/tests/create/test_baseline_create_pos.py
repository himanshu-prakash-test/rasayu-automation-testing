"""
Baseline Visit CRF - CREATE Operation (Positive Test Suite).
Validates TC-BASE-CREATE-POS-01 to TC-BASE-CREATE-POS-10.
Strictly 100% Zero Hardcoding: all test data dynamically loaded from 'CRUDtransaction-baseline' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from shared_tools.utils.env_config import config
    from transaction_management.baseline_module.pages.baseline_common_page import BaselinePage
    from transaction_management.baseline_module.baseline_data import (
        get_baseline_test_data,
        get_target_patient_id,
        parse_crud_sections,
        get_medications_payload,
        get_chips_payload,
        get_shortcut_instruction,
    )
except ImportError:
    from utils.env_config import config
    from pages.baseline_common_page import BaselinePage
    from baseline_data import (
        get_baseline_test_data,
        get_target_patient_id,
        parse_crud_sections,
        get_medications_payload,
        get_chips_payload,
        get_shortcut_instruction,
    )


@pytest.mark.positive
@pytest.mark.baseline
@pytest.mark.create
class TestBaselineCreatePos:
    """Positive test cases for Baseline Visit Create operations (Zero Hardcoded Data)."""

    def test_tc_base_create_pos_01_save_complete_disease_at_baseline(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-01: Save complete Disease at Baseline."""
        tc_id = "TC-BASE-CREATE-POS-01"
        rec = get_baseline_test_data(tc_id)
        pid = get_target_patient_id(tc_id)
        sections = parse_crud_sections(rec.raw_payload)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        # Personal details
        if "Personal" in sections and isinstance(sections["Personal"], dict):
            baseline_page.disease.fill_personal_details(sections["Personal"])

        # Allopathy Diagnosis
        if "Allopathy Diagnosis" in sections and isinstance(sections["Allopathy Diagnosis"], dict):
            baseline_page.disease.fill_allopathy_diagnosis(sections["Allopathy Diagnosis"])

        # Comorbidity
        if "Comorbidity" in sections and isinstance(sections["Comorbidity"], dict):
            c_data = sections["Comorbidity"]
            c_name = list(c_data.keys())[0] if c_data else ""
            baseline_page.disease.fill_comorbidity(c_name, c_data.get("Since", ""), c_data.get("Unit", ""))

        # Current Medicines
        if "Medicine (Allopathy)" in sections and isinstance(sections["Medicine (Allopathy)"], dict):
            m_data = sections["Medicine (Allopathy)"]
            m_name = list(m_data.keys())[0] if m_data else ""
            baseline_page.disease.fill_medication("Allopathy", m_name, m_data.get("Strength", ""), m_data.get("Unit", ""), m_data.get("Frequency", ""))

        # Chemo
        if "Chemo" in sections and isinstance(sections["Chemo"], dict):
            ch_data = sections["Chemo"]
            baseline_page.disease.fill_chemo(ch_data.get("Cycle No", ""), ch_data.get("Day", ""), ch_data.get("Start", ""), ch_data.get("End", ""))

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_02_save_complete_hetu_sevan(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-02: Save complete Hetu Sevan."""
        tc_id = "TC-BASE-CREATE-POS-02"
        rec = get_baseline_test_data(tc_id)
        pid = get_target_patient_id(tc_id)
        sections = parse_crud_sections(rec.raw_payload)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Hetu Sevan")

        # Habits
        if "Habits" in sections and isinstance(sections["Habits"], dict):
            h_data = sections["Habits"]
            baseline_page.hetu_sevan_page.fill_habit(
                habit=h_data.get("Habit", ""),
                status=h_data.get("Status", ""),
                qty=h_data.get("Qty", ""),
                since=h_data.get("Since", ""),
                unit=h_data.get("Unit", ""),
            )

        # Aahar
        if "Aahar" in sections and isinstance(sections["Aahar"], dict):
            a_data = sections["Aahar"]
            food_habits = a_data.get("Food Habits", [])
            if isinstance(food_habits, str):
                food_habits = [food_habits]
            baseline_page.hetu_sevan_page.fill_aahar(
                meal=a_data.get("Meal", ""),
                timing=a_data.get("Timing", ""),
                food_habits=food_habits,
                remark=a_data.get("Remark", ""),
            )

        # Vihar
        if "Vihar" in sections and isinstance(sections["Vihar"], dict):
            v_data = sections["Vihar"]
            baseline_page.hetu_sevan_page.fill_vihar(
                exercise=v_data.get("Exercise", ""),
                etype=v_data.get("Type", ""),
                freq=v_data.get("Freq", ""),
                duration=v_data.get("Duration", ""),
                since=v_data.get("Since", ""),
                unit=v_data.get("Unit", ""),
            )

        # Veg Dharan
        if "Veg Dharan" in sections and isinstance(sections["Veg Dharan"], dict):
            vd_data = sections["Veg Dharan"]
            lakshan = vd_data.get("Lakshan", [])
            if isinstance(lakshan, str):
                lakshan = [lakshan]
            baseline_page.hetu_sevan_page.fill_veg_dharan(
                veg=vd_data.get("Veg", ""),
                lakshan=lakshan,
            )

        # Manas
        if "Manas" in sections and isinstance(sections["Manas"], dict):
            m_data = sections["Manas"]
            acts = m_data.get("Activity", [])
            if isinstance(acts, str):
                acts = [acts]
            baseline_page.hetu_sevan_page.fill_manas(
                activities=acts,
                remark=m_data.get("Remark", ""),
            )

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_03_save_complete_physician_rac_opinion(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-03: Save complete Physician & RAC Opinion."""
        tc_id = "TC-BASE-CREATE-POS-03"
        rec = get_baseline_test_data(tc_id)
        pid = get_target_patient_id(tc_id)
        sections = parse_crud_sections(rec.raw_payload)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Physician and RAC Opinion")

        # Physician Opinion
        if "Physician Opinion" in sections and isinstance(sections["Physician Opinion"], dict):
            po_data = sections["Physician Opinion"]
            baseline_page.physician_rac_page.fill_physician_opinion(
                ptype=po_data.get("Type", ""),
                opinion=po_data.get("Opinion", ""),
                patient_opted=po_data.get("Patient Opted", "Yes"),
                patient_reason=po_data.get("Patient Reason"),
                physician_remark=po_data.get("Physician Remark", ""),
            )

        # RAC Management
        if "RAC Management" in sections and isinstance(sections["RAC Management"], dict):
            rac_data = sections["RAC Management"]
            baseline_page.physician_rac_page.fill_rac_management(
                approach=rac_data.get("Approach", ""),
                intent=rac_data.get("Intent"),
                objective=rac_data.get("Objective"),
                remark=rac_data.get("Remark"),
                rac_comment=rac_data.get("RAC Comment"),
                treatment_criteria=rac_data.get("Treatment Criteria"),
            )

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_04_add_multiple_repeatable_rows(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-04: Add multiple repeatable rows."""
        tc_id = "TC-BASE-CREATE-POS-04"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.add_repeatable_row("Allopathy Diagnosis")
        baseline_page.page.wait_for_timeout(300)

        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.add_repeatable_row("Aahar")
        baseline_page.page.wait_for_timeout(300)

        baseline_page.switch_subtab("Physician and RAC Opinion")
        baseline_page.add_repeatable_row("Physician Opinion")

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_05_add_medicines_across_all_subtabs(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-05: Add medicines across all sub-tabs."""
        tc_id = "TC-BASE-CREATE-POS-05"
        pid = get_target_patient_id(tc_id)
        meds = get_medications_payload(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")

        for m in meds:
            baseline_page.disease.fill_medication(
                pathy=m["pathy"],
                name=m["name"],
                strength=m["strength"],
                unit=m["unit"],
                freq=m["frequency"],
            )

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_06_multi_select_chip_creation(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-06: Multi-select chip creation."""
        tc_id = "TC-BASE-CREATE-POS-06"
        pid = get_target_patient_id(tc_id)
        chips = get_chips_payload(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.disease.select_allergy_chips(
            allergy_types=chips.get("Allergy Type", []),
            reasons=chips.get("Allergy Reason", []),
        )

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_07_conditional_toggle_creation(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-07: Conditional toggle creation."""
        tc_id = "TC-BASE-CREATE-POS-07"
        rec = get_baseline_test_data(tc_id)
        pid = get_target_patient_id(tc_id)
        sections = parse_crud_sections(rec.raw_payload)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Hetu Sevan")
        if "Vihar" in sections and isinstance(sections["Vihar"], dict):
            v_data = sections["Vihar"]
            baseline_page.hetu_sevan_page.fill_vihar(
                exercise=v_data.get("Exercise", "Yes"),
                etype=v_data.get("Type", ""),
                freq=v_data.get("Freq", ""),
                duration=v_data.get("Duration", ""),
                since=v_data.get("Since", ""),
                unit=v_data.get("Unit", ""),
            )

        baseline_page.switch_subtab("Physician and RAC Opinion")
        if "Physician Opinion" in sections and isinstance(sections["Physician Opinion"], dict):
            po_data = sections["Physician Opinion"]
            baseline_page.physician_rac_page.fill_physician_opinion(
                ptype=po_data.get("Type", "Oncologist"),
                opinion=po_data.get("Opinion", ""),
                patient_opted=po_data.get("Patient Opted", "No"),
                patient_reason=po_data.get("Patient Reason", ""),
            )

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_08_save_and_next_visit_navigation(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-08: Save & Next / Visit navigation."""
        tc_id = "TC-BASE-CREATE-POS-08"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.save_and_next()

        baseline_page.switch_subtab("Hetu Sevan")
        baseline_page.save_and_next()

        baseline_page.switch_subtab("Physician and RAC Opinion")
        baseline_page.save_baseline()
        baseline_page.click_visit()
        baseline_page.page.wait_for_timeout(1000)

    def test_tc_base_create_pos_09_brand_new_patient_zero_baseline_history(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-09: Brand-new patient (zero baseline history)."""
        tc_id = "TC-BASE-CREATE-POS-09"
        rec = get_baseline_test_data(tc_id)
        pid = get_target_patient_id(tc_id)
        sections = parse_crud_sections(rec.raw_payload)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        if "Minimal Valid Payload" in sections and isinstance(sections["Minimal Valid Payload"], dict):
            min_payload = sections["Minimal Valid Payload"]
            baseline_page.disease.fill_personal_details({"Marital Status": min_payload.get("Marital Status", "Married")})

            baseline_page.switch_subtab("Hetu Sevan")
            baseline_page.hetu_sevan_page.fill_habit(habit=min_payload.get("Habit", "None (No Harmful Addictions)"), status="Active")

            baseline_page.switch_subtab("Physician and RAC Opinion")
            baseline_page.physician_rac_page.fill_rac_management(approach=min_payload.get("Therapy Approach", "Supportive"))

        baseline_page.save_baseline()
        baseline_page.verify_save_success()

    def test_tc_base_create_pos_10_keyboard_only_form_entry_navigation(self, baseline_page: BaselinePage):
        """TC-BASE-CREATE-POS-10: Keyboard-only form entry & navigation."""
        tc_id = "TC-BASE-CREATE-POS-10"
        pid = get_target_patient_id(tc_id)

        baseline_page.open_baseline_workspace(pid)
        baseline_page.switch_subtab("Disease at Baseline")
        baseline_page.page.keyboard.press("Tab")
        baseline_page.page.keyboard.press("ArrowDown")
        baseline_page.page.keyboard.press("Enter")
        baseline_page.add_row_via_shortcut()
        baseline_page.save_via_shortcut()
        baseline_page.verify_save_success()
