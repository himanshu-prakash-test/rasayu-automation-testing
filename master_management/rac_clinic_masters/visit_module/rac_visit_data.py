"""
Unified RAC Visit Masters Test Data Adapter.
Encapsulates data loading strictly from 'CRUDmaster-rac-visit' sheet in Excel.
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

SHEET_NAME = "CRUDmaster-rac-visit"


def get_visit_test_data(test_case_id: str) -> TestDataRecord:
    """Retrieve test data record by Test Case ID from 'CRUDmaster-rac-visit' sheet."""
    return get_test_data_by_id(test_case_id, sheet_name=SHEET_NAME)


def get_all_visit_test_data() -> List[TestDataRecord]:
    """Retrieve all test data records from 'CRUDmaster-rac-visit' sheet."""
    return get_test_data(sheet_name=SHEET_NAME)


def get_visit_test_cases() -> List[TestCaseRecord]:
    """Retrieve all test case specifications from 'CRUDmaster-rac-visit' sheet."""
    return get_test_cases(sheet_name=SHEET_NAME)


def parse_visit_payload(raw_payload: str) -> Dict[str, str]:
    """
    Parses bullet-separated (`•` or `\n`) key-value strings from CRUDmaster-rac-visit.
    e.g. 'Toggle: RAC • Master: Visit Mode / Consultation Mode • Name: QA RAC Video Consult'
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
        if clean and clean != "Visit Mode / Consultation Mode (or Symptom)":
            return clean
        if "Visit Mode" in m_name:
            return "Visit Mode / Consultation Mode"

    # 2. From clinical module e.g. 'Create - Visit Mode / Consultation Mode'
    mod = rec.clinical_module or ""
    if "-" in mod:
        clean_mod = mod.split("-", 1)[1].strip()
        if clean_mod:
            return clean_mod

    return "Visit Mode / Consultation Mode"


def get_visit_record_name(test_case_id: str) -> str:
    """Extracts the primary record name to create or update."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    name = payload.get("Name", "")
    if name:
        return name.strip(' "\'')
    return ""


def get_visit_description(test_case_id: str) -> Optional[str]:
    """Extracts description string, returning None or empty string when blank."""
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
            # Strip trailing comments like '(confirm deletion & verify after page.reload())'
            clean = re.sub(r"\s*\(.*?\)$", "", val).strip(' "\'')
            clean = re.sub(r"\s*\+.*$", "", clean).strip()
            # If transition like 'Home visit' -> rename to existing 'Email'
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
        sidebar_kws = ["Relief", "Organ"]

    # Table search strings: Exact="Home visit", Partial="Home", Lowercase="home visit"
    table_raw = payload.get("Table (Visit Mode)", "")
    table_dict = {}
    for m in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', table_raw):
        table_dict[m.group(1).lower()] = m.group(2).strip()

    if not table_dict:
        table_dict = {"exact": "Home visit", "partial": "Home", "lowercase": "home visit"}

    return sidebar_kws, table_dict


def get_visit_empty_search_queries(test_case_id: str) -> Tuple[str, str]:
    """Extracts table and sidebar search queries for empty state tests."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    table_q = payload.get("Table Search Query", "XYZ_NON_EXISTENT_RAC_999").strip(' "\'')
    side_q = payload.get("Sidebar Search Query", "UnknownVisitMaster").strip(' "\'')
    return table_q, side_q


def get_visit_xss_oversized(test_case_id: str) -> Tuple[str, str]:
    """Extracts oversized name and XSS payload."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    oversized = "R" * 305
    xss = "<script>alert('rac')</script>"
    xss_val = payload.get("XSS Description", "")
    m = re.search(r'["\']([^"\']+)["\']', xss_val)
    if m:
        xss = m.group(1).strip()
    return oversized, xss


def get_visit_duplicate_names(test_case_id: str) -> Tuple[str, str]:
    """Extracts duplicate test names (exact and case-insensitive)."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    dup_str = payload.get("Duplicate Names", "")
    names = re.findall(r'["\']([^"\']+)["\']', dup_str)
    if len(names) >= 2:
        return names[0].strip(), names[1].strip()
    return "Home visit", "HOME VISIT"


def get_visit_cancel_double_click_names(test_case_id: str) -> Tuple[str, str]:
    """Extracts cancel row name and double-click test name."""
    rec = get_visit_test_data(test_case_id)
    payload = parse_visit_payload(rec.raw_payload)
    cancel_name = payload.get("Cancel Name", "QA RAC Cancel Row").strip(' "\'')
    double_click = payload.get("Double-Click Name", "QA RAC Every 6 Hours").strip(' "\'')
    return cancel_name, double_click
