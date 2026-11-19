import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import openpyxl

from utils.env_config import config
from test_data.data_models import TestDataRecord, TestCaseRecord

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent


def _find_excel_file(base_name: str) -> Path:
    """
    Dynamically searches for an Excel workbook by base name,
    supporting standard names and numbered copies across project roots.
    """
    candidate_dirs = [
        CURRENT_DIR,
        ROOT_DIR / "shared-tools" / "test_data",
        ROOT_DIR,
    ]

    for c_dir in candidate_dirs:
        if not c_dir.exists():
            continue
        exact = c_dir / f"{base_name}.xlsx"
        if exact.exists():
            return exact
        numbered = c_dir / f"{base_name} (1).xlsx"
        if numbered.exists():
            return numbered
        for f in c_dir.glob(f"{base_name}*.xlsx"):
            if not f.name.startswith("~$"):
                return f

    return CURRENT_DIR / f"{base_name}.xlsx"


DATA_EXCEL_PATH = _find_excel_file("Rasayu_Test_Data")
CASES_EXCEL_PATH = _find_excel_file("Rasayu_Test_Cases")


def parse_payload(payload: str) -> Dict[str, str]:
    """
    Universal test data payload parser.
    Splits pipe-separated tokens ('Key: Value | Key2: Value2') into a dictionary.
    Generically handles:
      - Environment placeholders ([FROM_ENV:...]) and dynamic credentials
      - Nested parenthesized attributes: 'Parent (K1: V1, K2: V2)' -> K1, K2
      - Clean values by stripping boundary notes/comments in parentheses
      - Date ranges: 'DD/MM/YYYY to DD/MM/YYYY' -> 'Start Date' and 'End Date'
      - Arrow transformations: 'Category -> Value'
    """
    result: Dict[str, str] = {}
    if not payload:
        return result

    # Dynamic environment credential resolution
    if "env" in payload.lower() and ("credential" in payload.lower() or "admin" in payload.lower()):
        result["Username"] = config.admin_username
        result["Password"] = config.admin_password

    resolved = (
        payload
        .replace("[FROM_ENV:ADMIN_USERNAME]", config.admin_username)
        .replace("[FROM_ENV:ADMIN_PASSWORD]", config.admin_password)
        .replace("admin_rac@rasayu.com", config.admin_username)
        .replace("SecureRac@2026!", config.admin_password)
    )

    parts = resolved.split("|")
    for part in parts:
        if ":" in part:
            k, v = part.split(":", 1)
            k = k.strip()
            v = v.strip()
            result[k] = v

            # 1. Nested key-value pairs inside parentheses, e.g. "Item Name (Key1: Val1, Key2: Val2)"
            paren_match = re.search(r"([^(]+)\s*\((.+)\)", v)
            if paren_match:
                prefix_name = paren_match.group(1).strip()
                result[f"{k} Name"] = prefix_name
                inner = paren_match.group(2)
                nested = re.findall(r"([\w\s\(\)\-\/]+?):\s*([^,;()]+)", inner)
                for nk, nv in nested:
                    nk = nk.strip()
                    nv = nv.strip()
                    if nk:
                        result[nk] = nv
            else:
                # Direct nested pairs if no leading prefix
                nested = re.findall(r"([\w\s\(\)\-\/]+?):\s*([^,;()]+)", v)
                for nk, nv in nested:
                    nk = nk.strip()
                    nv = nv.strip()
                    if nk and nk not in result:
                        result[nk] = nv

            # 2. Date ranges: '01/01/2025 to 05/02/2025'
            date_range = re.search(r"(\d{2}/\d{2}/\d{4})\s+to\s+(\d{2}/\d{2}/\d{4})", v)
            if date_range:
                result["Start Date"] = date_range.group(1)
                result["End Date"] = date_range.group(2)

            # 3. Clean value by stripping parenthetical commentary e.g. "2030 (Future calendar year boundary)"
            clean_sub = re.sub(r"\s*\([^)]*\)", "", v).strip()
            if clean_sub and clean_sub != v:
                result[f"{k} Clean"] = clean_sub

            # 4. Arrow syntax: e.g. 'Food Allergy -> Gluten & Wheat (Mild hives)'
            if "->" in v:
                arrow_parts = [p.strip() for p in v.split("->") if p.strip()]
                if len(arrow_parts) > 1:
                    result[f"{k} Category"] = arrow_parts[0]
                    # Clean trailing parenthetical comments from arrow target
                    arrow_val = re.sub(r"\s*\([^)]*\)", "", arrow_parts[1]).strip()
                    result[f"{k} Tag"] = arrow_val.split("&")[0].strip() if "&" in arrow_val else arrow_val

            # 5. File name extraction if present
            file_match = re.search(r"([\w\.-]+\.(?:exe|zip|txt|pdf|sh|bin|csv|xlsx))", v)
            if file_match:
                result[f"{k} Clean"] = file_match.group(1).strip()
        elif part.strip():
            result[part.strip()] = part.strip()

    return result


def get_all_sheet_names(file_name: str = "Rasayu_Test_Data") -> List[str]:
    """Returns a list of all sheet names available in the specified Excel file."""
    excel_file = _find_excel_file(file_name)
    if not excel_file.exists():
        raise FileNotFoundError(f"Excel file '{file_name}' not found at: {excel_file}")
    wb = openpyxl.load_workbook(excel_file, read_only=True)
    return wb.sheetnames


def get_test_data(sheet_name: str, file_name: str = "Rasayu_Test_Data") -> List[TestDataRecord]:
    """
    Loads all test data rows from the specified sheet in the given Excel workbook.
    `sheet_name` is strictly required to prevent coupling between different clinical modules.
    """
    excel_file = _find_excel_file(file_name)
    if not excel_file.exists():
        raise FileNotFoundError(f"Test data file not found at: {excel_file}")

    wb = openpyxl.load_workbook(excel_file, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ValueError(
            f"Sheet '{sheet_name}' not found in {excel_file}. Available sheets: {wb.sheetnames}"
        )

    ws = wb[sheet_name]
    header = [cell.value for cell in ws[1]]
    records: List[TestDataRecord] = []

    # Map header column indices dynamically
    col_map = {str(name).strip(): idx for idx, name in enumerate(header) if name}

    tc_id_col = col_map.get("Test Case ID", 0)
    test_type_col = col_map.get("Test Type", 1)
    module_col = (
        col_map.get("Clinical Module / Feature")
        or col_map.get("Module / Feature")
        or col_map.get("Module", 2)
    )
    scenario_col = col_map.get("Test Scenario", 3)
    payload_col = (
        col_map.get("Specific Test Data Payload / Input Values")
        if "Specific Test Data Payload / Input Values" in col_map
        else col_map.get("Specific Test Data Payload / Input Value", 4)
    )
    outcome_col = col_map.get("Expected Validation Outcome", 5)

    for row_idx in range(2, ws.max_row + 1):
        row = ws[row_idx]
        tc_id = str(row[tc_id_col].value or "").strip()
        if not tc_id or tc_id.lower() == "test case id":
            continue

        raw_payload = str(row[payload_col].value or "").strip() if payload_col < len(row) else ""
        parsed = parse_payload(raw_payload)

        record = TestDataRecord(
            test_case_id=tc_id,
            test_type=str(row[test_type_col].value or "").strip(),
            clinical_module=str(row[module_col].value or "").strip(),
            test_scenario=str(row[scenario_col].value or "").strip(),
            raw_payload=raw_payload,
            expected_outcome=str(row[outcome_col].value or "").strip(),
            parsed_payload=parsed,
        )
        records.append(record)

    return records


def get_test_data_by_id(
    test_case_id: str,
    sheet_name: Optional[str] = None,
    file_name: str = "Rasayu_Test_Data"
) -> TestDataRecord:
    """
    Finds a single test data entry by Test Case ID.
    If `sheet_name` is provided, searches that sheet first.
    If not found (or if `sheet_name` is None), searches across all other sheets in the workbook.
    """
    excel_file = _find_excel_file(file_name)
    wb = openpyxl.load_workbook(excel_file, read_only=True)

    sheets_to_search = [sheet_name] if sheet_name and sheet_name in wb.sheetnames else []
    for s in wb.sheetnames:
        if s not in sheets_to_search:
            sheets_to_search.append(s)

    for s_name in sheets_to_search:
        try:
            records = get_test_data(sheet_name=s_name, file_name=file_name)
            for r in records:
                if r.test_case_id.lower() == test_case_id.lower():
                    return r
        except Exception:
            continue

    raise KeyError(f"Test case '{test_case_id}' not found in any sheet of {excel_file.name}.")


def get_test_cases(sheet_name: str, file_name: str = "Rasayu_Test_Cases") -> List[TestCaseRecord]:
    """
    Loads all test case definitions from the specified sheet in the given Excel workbook.
    """
    excel_file = _find_excel_file(file_name)
    if not excel_file.exists():
        raise FileNotFoundError(f"Test cases file not found at: {excel_file}")

    wb = openpyxl.load_workbook(excel_file, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ValueError(
            f"Sheet '{sheet_name}' not found in {excel_file}. Available sheets: {wb.sheetnames}"
        )

    ws = wb[sheet_name]
    records: List[TestCaseRecord] = []

    for row_idx in range(2, ws.max_row + 1):
        row = ws[row_idx]
        tc_id = str(row[0].value or "").strip()
        if not tc_id or tc_id.lower() == "test case id":
            continue

        records.append(
            TestCaseRecord(
                test_case_id=tc_id,
                scenario=str(row[1].value or "").strip(),
                precondition=str(row[2].value or "").strip(),
                test_steps=str(row[3].value or "").strip(),
                expected_result=str(row[4].value or "").strip(),
                automation_status=str(row[5].value or "").strip(),
                test_status=str(row[6].value or "").strip() if len(row) > 6 else None,
                remarks=str(row[7].value or "").strip() if len(row) > 7 else None,
            )
        )

    return records
