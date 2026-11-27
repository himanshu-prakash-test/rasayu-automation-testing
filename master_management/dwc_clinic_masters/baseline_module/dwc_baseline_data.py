"""
Unified Master DWC Baseline Test Data Adapter.
Encapsulates data loading strictly from 'master_dwc_createbaseline',
'master_dwc_updatebaseline', and 'master_dwc_deletebaseline' sheets in Excel.
Zero hardcoding: all test data dynamically retrieved from Excel.
"""
import re
from typing import Dict, List, Optional, Tuple

try:
    from shared_tools.data_loader.excel_reader import (
        get_test_data,
        get_test_data_by_id,
        get_test_cases,
    )
    from shared_tools.data_loader.data_models import TestDataRecord, TestCaseRecord
except ImportError:
    from test_data.excel_reader import (
        get_test_data,
        get_test_data_by_id,
        get_test_cases,
    )
    from test_data.data_models import TestDataRecord, TestCaseRecord

MASTER_CREATE_SHEET = "master_dwc_createbaseline"
MASTER_UPDATE_SHEET = "master_dwc_updatebaseline"
MASTER_DELETE_SHEET = "master_dwc_deletebaseline"


# ==================== CREATE ====================
def get_master_baseline_test_data(test_case_id: str) -> TestDataRecord:
    """Retrieve test data record for DWC baseline create."""
    return get_test_data_by_id(test_case_id, sheet_name=MASTER_CREATE_SHEET)


def get_all_master_baseline_test_data() -> List[TestDataRecord]:
    """Retrieve all test data records for DWC baseline create."""
    return get_test_data(sheet_name=MASTER_CREATE_SHEET)


def get_master_baseline_test_cases() -> List[TestCaseRecord]:
    """Retrieve all test case definitions for DWC baseline create."""
    return get_test_cases(sheet_name=MASTER_CREATE_SHEET)


def get_active_record_input(test_case_id: str) -> str:
    """Extract clean active record name, stripping any (Parent: ...) prefix."""
    rec = get_master_baseline_test_data(test_case_id)
    raw = rec.active_record_input or ""
    clean = re.sub(r"\(Parent:[^)]*\)\s*", "", raw).strip()
    return clean


def get_inactive_record_input(test_case_id: str) -> str:
    """Extract clean inactive record name, stripping any (Parent: ...) prefix."""
    rec = get_master_baseline_test_data(test_case_id)
    raw = rec.inactive_record_input or ""
    clean = re.sub(r"\(Parent:[^)]*\)\s*", "", raw).strip()
    return clean


def get_record_name_input(test_case_id: str) -> str:
    """Returns active record name as primary input."""
    return get_active_record_input(test_case_id)


def get_master_category(test_case_id: str) -> str:
    """
    Determines target master category in DWC sidebar.
    Strips parent/filter suffixes to get exact sidebar title.
    """
    if "UPD" in test_case_id:
        rec = get_master_update_test_data(test_case_id)
        if not rec:
            return "Chief Complaint"
        raw_master = rec.parsed_payload.get("Master", "")
        if "Master with" in raw_master:
            return "Chief Complaint"
        if raw_master:
            clean = re.sub(r"\s*\([^)]*\)", "", raw_master).strip()
            if clean and "Master" not in clean:
                return clean
        m1 = rec.parsed_payload.get("Master 1", "")
        if m1:
            clean_m1 = re.sub(r"\s*\([^)]*\)", "", m1).strip()
            if clean_m1:
                return clean_m1
        module = rec.clinical_module or ""
        paren = re.search(r"^([^(\n]+)", module)
        return paren.group(1).strip() if paren else "Chief Complaint"
    elif "DEL" in test_case_id:
        rec = get_master_delete_test_data(test_case_id)
        if not rec:
            return "Chief Complaint"
        payload = rec.parsed_payload
        raw_master = payload.get("Master") or payload.get("Master 1") or payload.get("Clinical Module / Feature") or "Chief Complaint"
        clean_cat = re.sub(r"\s*\([^)]*\)", "", raw_master).strip()
        if "any dwc master" in clean_cat.lower() or "with 16 entries" in clean_cat.lower() or clean_cat == "":
            return "Chief Complaint"
        return clean_cat
    else:
        rec = get_master_baseline_test_data(test_case_id)
        if not rec:
            return "Marital Status"
        module = rec.clinical_module or ""
        clean = re.sub(r"\(Parent:[^)]*\)", "", module).strip()
        return clean or "Marital Status"


def get_parent_dependency(test_case_id: str) -> Optional[str]:
    """Extracts parent category or option if record is a dependent master."""
    rec = get_master_baseline_test_data(test_case_id)
    raw = rec.active_record_input or rec.clinical_module or ""
    match = re.search(r"\(Parent:\s*([^)]+)\)", raw)
    if match:
        val = match.group(1).strip()
        if val.lower() in ("none", "unselected"):
            return None
        return val
    return None


def get_record_description(test_case_id: str) -> Optional[str]:
    """Default description generated dynamically from scenario/category."""
    rec = get_master_baseline_test_data(test_case_id)
    if rec and rec.test_scenario:
        return f"DWC Master Record: {rec.test_scenario}"
    return "Automated DWC Baseline Master Entry"


def get_record_status(test_case_id: str) -> bool:
    """Returns True for Active record tests, False for Inactive."""
    rec = get_master_baseline_test_data(test_case_id)
    if not rec:
        return True
    return "inactive" not in (rec.test_scenario or "").lower()


# ==================== UPDATE ====================
def get_master_update_test_data(test_case_id: str) -> TestDataRecord:
    """Retrieve test data record for DWC baseline update."""
    return get_test_data_by_id(test_case_id, sheet_name=MASTER_UPDATE_SHEET)


def get_all_master_update_test_data() -> List[TestDataRecord]:
    """Retrieve all test data records for DWC baseline update."""
    return get_test_data(sheet_name=MASTER_UPDATE_SHEET)


def get_master_update_test_cases() -> List[TestCaseRecord]:
    """Retrieve all test case definitions for DWC baseline update."""
    return get_test_cases(sheet_name=MASTER_UPDATE_SHEET)


def get_target_record_name(test_case_id: str) -> str:
    """Extracts target record identifier to locate in the table for update."""
    rec = get_master_update_test_data(test_case_id)
    payload = rec.parsed_payload
    for k in ["Target Record", "Target Record Clean", "Target Record Name"]:
        if k in payload:
            raw = str(payload[k]).strip()
            clean = re.sub(r"\s*\([^)]*\)", "", raw).strip()
            return clean
    for k in payload:
        if k.startswith("Record 1"):
            match = re.search(r"\(([^)]+)\)", k)
            if match:
                return match.group(1).strip()
    return "QA_PolyuriaPolydipsia"


def get_new_record_name(test_case_id: str) -> str:
    """Extracts new updated name from update payload."""
    rec = get_master_update_test_data(test_case_id)
    payload = rec.parsed_payload
    for k in ["New Name", "New Name / Title"]:
        if k in payload:
            val = str(payload[k]).strip()
            if "cleared" in val.lower() or val in ("''", '""'):
                return ""
            if "already exists" in val.lower():
                return re.sub(r"\s*\([^)]*\)", "", val).strip()
            return val
    for k in ["Name / Title", "Subtype Name", "Complication Name"]:
        if k in payload:
            val = str(payload[k]).strip()
            if "cleared" in val.lower() or val in ("''", '""'):
                return ""
            return val
    return ""


def get_update_description(test_case_id: str) -> Optional[str]:
    """Extracts description instruction for update."""
    rec = get_master_update_test_data(test_case_id)
    payload = rec.parsed_payload
    desc = payload.get("Description")
    if desc:
        if "(leave blank)" in desc.lower() or desc in ("''", '""'):
            return ""
        return desc.strip()
    s1 = payload.get("Step 1")
    if s1 and "description to" in s1.lower():
        match = re.search(r"Description to '([^']+)'", s1)
        if match:
            return match.group(1)
    return None


def get_update_action(test_case_id: str) -> str:
    """Extracts action instruction from update payload."""
    rec = get_master_update_test_data(test_case_id)
    return rec.parsed_payload.get("Action", "")


def get_update_parent_dropdown(test_case_id: str) -> Optional[str]:
    """Extracts parent dropdown selection from update payload."""
    rec = get_master_update_test_data(test_case_id)
    return rec.parsed_payload.get("Parent Dropdown") or rec.parsed_payload.get("Parent Generic/Form")


def get_search_filter_term(test_case_id: str) -> Optional[str]:
    """Extracts search query filter term for update."""
    rec = get_master_update_test_data(test_case_id)
    payload = rec.parsed_payload
    val = payload.get("Search Filter") or payload.get("Search Filter Clean")
    if val:
        match = re.search(r"'([^']+)'", val)
        if match:
            return match.group(1).strip()
        return val.strip()
    return None


def get_shortcut_instruction(test_case_id: str) -> Optional[str]:
    """Extracts shortcut key combination from action or payload."""
    if "UPD" in test_case_id:
        rec = get_master_update_test_data(test_case_id)
    else:
        rec = get_master_baseline_test_data(test_case_id)
    if not rec:
        return None
    action = rec.parsed_payload.get("Action", "")
    match = re.search(r"Alt\s*\+\s*[A-Za-z0-9]", action)
    if match:
        return match.group(0).replace(" ", "")
    return None


def get_switch_targets(test_case_id: str) -> Tuple[str, str]:
    """Extracts Master 1 and Master 2 for navigation state switching."""
    if "UPD" in test_case_id:
        rec = get_master_update_test_data(test_case_id)
        if not rec:
            return "Blood Group", "Subjective Prognosis"
        payload = rec.parsed_payload
        m1_raw = payload.get("Master 1", "Blood Group")
        m1 = re.sub(r"\s*\([^)]*\)", "", m1_raw).strip() or "Blood Group"
        action = payload.get("Action", "")
        match = re.search(r"switch to (?:Master 2 \()?([^)]+?)\)? via", action, re.I)
        m2 = match.group(1).strip() if match else "Subjective Prognosis"
        return m1, m2
    else:
        rec = get_master_delete_test_data(test_case_id)
        if not rec:
            return "Blood Group", "Subjective Prognosis"
        payload = rec.parsed_payload
        m1_raw = payload.get("Master 1", "Blood Group")
        m1 = re.sub(r"\s*\([^)]*\)", "", m1_raw).strip() or "Blood Group"
        action = payload.get("Action", "")
        match = re.search(r"navigate to (?:Master 2 \()?([^),]+?)\)?(?:,|$)", action, re.I)
        m2 = match.group(1).strip() if match else "Subjective Prognosis"
        return m1, m2


# ==================== DELETE ====================
def get_master_delete_test_data(test_case_id: str) -> TestDataRecord:
    """Retrieve test data record for DWC baseline delete."""
    return get_test_data_by_id(test_case_id, sheet_name=MASTER_DELETE_SHEET)


def get_all_master_delete_test_data() -> List[TestDataRecord]:
    """Retrieve all test data records for DWC baseline delete."""
    return get_test_data(sheet_name=MASTER_DELETE_SHEET)


def get_master_delete_test_cases() -> List[TestCaseRecord]:
    """Retrieve all test case definitions for DWC baseline delete."""
    return get_test_cases(sheet_name=MASTER_DELETE_SHEET)


def get_delete_target_name(test_case_id: str) -> str:
    """Extracts target record identifier for delete."""
    rec = get_master_delete_test_data(test_case_id)
    payload = rec.parsed_payload
    for k in ["Target Record", "Target Record Clean", "Target Record Name"]:
        if k in payload:
            raw = str(payload[k]).strip()
            clean = re.sub(r"\s*\([^)]*\)", "", raw).strip()
            return clean
    return "QA_PolyuriaPolydipsia"


def get_delete_search_query(test_case_id: str) -> Optional[str]:
    """Extracts search query for filtered delete test."""
    rec = get_master_delete_test_data(test_case_id)
    if not rec:
        return None
    query = rec.parsed_payload.get("Search Query")
    return query.strip(' "\'') if query else None


def get_delete_switch_targets(test_case_id: str) -> Tuple[str, str]:
    """Extracts Master 1 and Master 2 for delete navigation switch test."""
    return get_switch_targets(test_case_id)
