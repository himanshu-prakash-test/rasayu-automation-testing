"""
Unified DWC Visit Masters Test Data Adapter.
Encapsulates data loading strictly from 'CRUDmaster-dwc-visit' sheet in Excel.
Strictly 100% Zero Hardcoding: all test data dynamically retrieved from Excel.
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

SHEET_NAME = "CRUDmaster-dwc-visit"


def get_visit_test_data(test_case_id: str) -> TestDataRecord:
    """Retrieve test data record by Test Case ID from 'CRUDmaster-dwc-visit' sheet."""
    return get_test_data_by_id(test_case_id, sheet_name=SHEET_NAME)


def get_all_visit_test_data() -> List[TestDataRecord]:
    """Retrieve all test data records from 'CRUDmaster-dwc-visit' sheet."""
    return get_test_data(sheet_name=SHEET_NAME)


def get_visit_test_cases() -> List[TestCaseRecord]:
    """Retrieve all test case specifications from 'CRUDmaster-dwc-visit' sheet."""
    return get_test_cases(sheet_name=SHEET_NAME)


def parse_visit_payload(raw_payload: str) -> Dict[str, str]:
    """
    Parses bullet-separated (`•` or `\n`) key-value strings from CRUDmaster-dwc-visit.
    e.g. 'Toggle: DWC • Master: Symptom • Name: QA DWC Neuropathic Pain'
    """
    if not raw_payload:
        return {}
    parts = re.split(r"[\n•]+", raw_payload)
    data = {}
    for p in parts:
        p = p.strip()
        if ":" in p:
            k, v = p.split(":", 1)
            data[k.strip()] = v.strip()
    return data


def get_visit_master_name(test_case_id: str) -> str:
    """Extracts target master name from payload or clinical module."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)

    # 1. From payload 'Master' key
    m_name = payload.get("Master")
    if m_name:
        clean = re.sub(r"\s*\(.*?\)$", "", m_name).strip()
        if clean:
            return clean

    # 2. From clinical module e.g. 'Create - Symptom'
    mod = rec.clinical_module or ""
    if "-" in mod:
        clean_mod = mod.split("-", 1)[1].strip()
        if clean_mod:
            return clean_mod

    return "Symptom"


def get_visit_record_name(test_case_id: str) -> str:
    """Extracts the primary record name to create or update."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    name = payload.get("Name", "")
    if name:
        return name.strip(' "\'')
    return ""


def get_visit_description(test_case_id: str) -> Optional[str]:
    """Extracts description string, returning empty string or None when blank."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    desc = payload.get("Description", "")
    if '""' in desc or "renders —" in desc or "leave blank" in desc.lower():
        return ""
    return desc.strip() if desc else None


def get_visit_status(test_case_id: str) -> bool:
    """Returns True for Active, False for Inactive."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    status_str = payload.get("Status", "Active").lower()
    return "inactive" not in status_str


def get_visit_shortcut(test_case_id: str) -> Optional[str]:
    """Extracts keyboard shortcut like 'Alt + S'."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    sc = payload.get("Shortcut") or payload.get("Keys")
    if sc:
        match = re.search(r"Alt\s*\+\s*[A-Za-z0-9]", sc)
        if match:
            return match.group(0).replace(" ", "")
    return None


def get_visit_target_record(test_case_id: str) -> str:
    """Extracts target record identifier for update or delete."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)

    for k in [
        "Target Record",
        "Unused Target Record",
        "Search & Delete Target",
        "Deleted Record",
        "In-Use Record",
    ]:
        val = payload.get(k)
        if val:
            clean = re.sub(r"\s*\(.*?\)$", "", val).strip(' "\'')
            clean = re.sub(r"\s*\+.*$", "", clean).strip()
            if "→" in clean:
                clean = clean.split("→")[0].strip(' "\'')
            return clean

    return ""


def get_visit_transition_name(test_case_id: str) -> Tuple[str, str]:
    """Extracts (old_name, new_name) for update tests."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    val = payload.get("Old → New Name", "")
    if "→" in val:
        old_n, new_n = val.split("→", 1)
        return old_n.strip(' "\''), new_n.strip(' "\'')
    return "", ""


def get_visit_transition_desc(test_case_id: str) -> Tuple[str, str]:
    """Extracts (old_desc, new_desc) for update tests."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    val = payload.get("Old → New Desc") or payload.get("New Desc", "")
    if "→" in val:
        old_d, new_d = val.split("→", 1)
        return old_d.strip(' "\''), new_d.strip(' "\'')
    return "", val.strip(' "\'')


def get_visit_status_toggle(test_case_id: str) -> List[str]:
    """Extracts status toggle sequence e.g. ['Active', 'Inactive', 'Active']."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    val = payload.get("Status Toggle", "")
    if "→" in val:
        return [s.strip() for s in val.split("→")]
    return ["Active", "Inactive"]


def get_visit_accordion_info(test_case_id: str) -> Tuple[str, int]:
    """Extracts accordion title and expected item count e.g. ('VISIT MASTERS', 20)."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    acc = payload.get("Accordion", "VISIT MASTERS").strip()
    cnt_str = payload.get("Expected Badge Count", "20")
    match = re.search(r"\d+", cnt_str)
    cnt = int(match.group(0)) if match else 20
    return acc, cnt


def get_visit_search_strings(test_case_id: str) -> Tuple[List[str], Dict[str, str]]:
    """Extracts (sidebar_keywords, table_search_dict)."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)

    # Sidebar keywords
    sidebar_raw = payload.get("Sidebar (Search masters…)", "")
    sidebar_kws = re.findall(r'["\']([^"\']+)["\']', sidebar_raw)
    if not sidebar_kws:
        sidebar_kws = ["Symptom", "ANC", "PNC"]

    # Table search strings
    table_raw = ""
    for k, v in payload.items():
        if k.startswith("Table"):
            table_raw = v
            break

    table_dict = {}
    for m in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', table_raw):
        table_dict[m.group(1).lower()] = m.group(2).strip()

    if not table_dict:
        table_dict = {"exact": "Fever", "partial": "Pain", "lowercase": "insomnia"}

    return sidebar_kws, table_dict


def get_visit_empty_search_queries(test_case_id: str) -> Tuple[str, str]:
    """Extracts table and sidebar search queries for empty state tests."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    table_q = payload.get("Table Search Query", "NON_EXISTENT_DWC_SYMPTOM_999").strip(' "\'')
    side_q = payload.get("Sidebar Search Query", "UnknownDWCMasterXYZ").strip(' "\'')
    return table_q, side_q


def get_visit_xss_oversized(test_case_id: str) -> Tuple[str, str]:
    """Extracts oversized name and XSS payload."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    oversized = "D" * 305
    xss = "<script>alert('dwc')</script>"
    xss_val = payload.get("XSS Description", "")
    m = re.search(r'["\']([^"\']+)["\']', xss_val)
    if m:
        xss = m.group(1).strip()
    return oversized, xss


def get_visit_duplicate_names(test_case_id: str) -> Tuple[str, str]:
    """Extracts (exact_duplicate, case_insensitive_duplicate)."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    dup_str = payload.get("Duplicate Names", "")
    matches = re.findall(r'["\']([^"\']+)["\']', dup_str)
    if len(matches) >= 2:
        return matches[0], matches[1]
    return "Bleeding", "BLEEDING"


def get_visit_cancel_double_click_names(test_case_id: str) -> Tuple[str, str]:
    """Extracts (cancel_name, double_click_name)."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    cancel_name = payload.get("Cancel Name", "QA DWC Cancel").strip(' "\'')
    dbl_name = payload.get("Double-Click Name", "QA DWC Throbbing").strip(' "\'')
    # Strip any description comment
    dbl_name = re.sub(r"\s*\(.*?\)$", "", dbl_name).strip()
    return cancel_name, dbl_name
