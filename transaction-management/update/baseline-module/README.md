# Transaction Management - Baseline Visit Module

Automation test suite for the **Baseline Visit Case Report Form (CRF)** of the **Rasayu Clinical Management Portal** (`/admin/crf/patient/`).

---

## 1. Module Overview & Structure

This module encapsulates all Page Objects, test cases, and test data handlers for creating and updating baseline clinical patient records.

```
baseline-module/
├── __init__.py               # Python package initialization
├── README.md                 # Module documentation
├── baseline_data.py          # Module-specific test data adapter (reads 'createbaseline' sheet)
├── pages/                    # Page Objects (Playwright encapsulation)
│   ├── __init__.py
│   ├── baseline_page.py      # Unified coordinator Page Object
│   ├── patient_search.py     # Patient directory search & demographic header validation
│   └── subtabs.py            # Clinical sub-tabs: Demographics, Diagnosis, History,
│                             # Vitals & Staging, Hetu Sevan, Advisory & RAC Opinion
└── tests/                    # Automated pytest test suites
    ├── __init__.py
    ├── test_baseline_positive.py  # 23 Positive test cases (TC-BASE-POS-01 to POS-23)
    └── test_baseline_negative.py  # 14 Negative & boundary test cases (TC-BASE-NEG-01 to NEG-14)
```

---

## 2. Test Coverage Matrix (37 / 37 Automated Test Cases)

### Positive Test Cases (`test_baseline_positive.py`)
| Test Case ID | Scenario | Sub-Tab / Feature |
|---|---|---|
| `TC-BASE-POS-01` | Admin Login with Valid Credentials | Authentication (`.env`) |
| `TC-BASE-POS-02` | Patient Directory Search & Filtering | Patient Directory |
| `TC-BASE-POS-03` | Open Patient Profile & Verify Demographics | Demographic Header |
| `TC-BASE-POS-04` | Baseline Module Access & Sub-Tab Navigation | Baseline Workspace |
| `TC-BASE-POS-05` | Record Personal Details & Allergy Multi-Tags | Demographics |
| `TC-BASE-POS-06` | Add Valid Allopathy Diagnosis Row | Allopathy Diagnosis |
| `TC-BASE-POS-07` | Ayurvedic Diagnosis & Classical Parameters | Ayurvedic Diagnosis |
| `TC-BASE-POS-08` | Past Medical History & Comorbidity Logging | Medical History |
| `TC-BASE-POS-09` | Family Medical History Entry | Family History |
| `TC-BASE-POS-10` | Current Medicines & Chemotherapy Regimen | Medicines History |
| `TC-BASE-POS-11` | Disease at Baseline - Chief Complaints | Chief Complaints |
| `TC-BASE-POS-12` | Baseline Vitals & ECOG Performance Status | Vitals & Staging |
| `TC-BASE-POS-13` | Cancer Staging & TNM Classification | TNM Staging |
| `TC-BASE-POS-14` | Surgical & Histopathology History | Surgical History |
| `TC-BASE-POS-15` | Radiation Therapy Regimen Entry | Radiation Oncology |
| `TC-BASE-POS-16` | Baseline Lab Investigations Entry | Lab Investigations |
| `TC-BASE-POS-17` | Hetu Sevan (Aharaja & Viharaja Factors) | Hetu Sevan |
| `TC-BASE-POS-18` | Hetu Sevan (Manasika Factors) | Manasika Hetu |
| `TC-BASE-POS-19` | Physician Clinical Assessment & Prognosis | Clinical Prognosis |
| `TC-BASE-POS-20` | RAC Advisory Board Protocol & Sign-Off | RAC Protocol |
| `TC-BASE-POS-21` | Physician Opinion Row Operations | Physician Opinion |
| `TC-BASE-POS-22` | RAC Management Record Operations | Management Approach |
| `TC-BASE-POS-23` | Save Baseline Form Execution | Save Form Trigger |

### Negative & Boundary Test Cases (`test_baseline_negative.py`)
| Test Case ID | Scenario | Boundary / Validation Check |
|---|---|---|
| `TC-BASE-NEG-01` | Invalid Login Authentication | Bad credentials alert |
| `TC-BASE-NEG-02` | Input Sanitization & XSS Prevention | Script injection into text fields |
| `TC-BASE-NEG-03` | Future Year Entry Validation | Future calendar year boundary |
| `TC-BASE-NEG-04` | Missing Mandatory Ayurvedic Parameters | Empty Nidan & Dosha |
| `TC-BASE-NEG-05` | Incomplete Family History Submission | Empty Relation & Condition |
| `TC-BASE-NEG-06` | Chronological Date Inconsistency | End date precedes Start date |
| `TC-BASE-NEG-07` | Out-of-Range ECOG Performance Status | ECOG score out of 0–5 scale |
| `TC-BASE-NEG-08` | Negative Value in Vitals / Dosage | Negative blood pressure & weight |
| `TC-BASE-NEG-09` | Radiation Therapy Zero Fraction | Zero fraction boundary |
| `TC-BASE-NEG-10` | Unauthorized RAC Finalization | Non-privileged user state |
| `TC-BASE-NEG-11` | Unsupported File Type Upload | Disallowed file extension (`.exe`) |
| `TC-BASE-NEG-12` | Premature Baseline Finalization | Incomplete mandatory sections |
| `TC-BASE-NEG-13` | Blank Physician Opinion Fields | Empty doctor opinion submission |
| `TC-BASE-NEG-14` | Save Baseline with Missing Mandatory Fields | Missing mandatory blocks validation |

---

## 3. Key Design Principles

1. **Zero Hardcoded Data**:
   - All test inputs, options, patient identifiers, and boundary conditions are dynamically loaded from `shared-tools/test_data/Rasayu_Test_Data.xlsx` through `baseline_data.py`.
   - Credentials strictly reside in `.env` (never committed to version control).
2. **Dynamic Screenshot Evidence**:
   - Every test case captures a full-page validation screenshot upon completion.
   - Screenshots are named by official Test Case ID (e.g. `screenshots/TC-BASE-POS-01.png`).
   - The screenshot folder automatically vanishes/cleans before each new test run.
   - Folder has an automatic 100-file ceiling (FIFO deletion of older files).
3. **Decoupled Architecture**:
   - `shared-tools` contains zero baseline-specific code, making it reusable across `master-management/RAC`, `master-management/DWC`, and future transaction modules.
4. **Server & CI/CD Portability**:
   - Runs in headless mode by default.
   - Supports `--headed` flag for visible debugging.
   - Tkinter popup gracefully suppresses on headless Linux servers without `$DISPLAY`.

---

## 4. Execution Commands

```powershell
# Run all baseline tests (headless by default)
pytest transaction-management/update/baseline-module/

# Run with visible browser window (headed mode)
pytest transaction-management/update/baseline-module/ --headed

# Run only positive test cases
pytest transaction-management/update/baseline-module/tests/test_baseline_positive.py

# Run only negative test cases
pytest transaction-management/update/baseline-module/tests/test_baseline_negative.py

# Run a single specific test case
pytest transaction-management/update/baseline-module/ -k "TC-BASE-POS-01"
```
