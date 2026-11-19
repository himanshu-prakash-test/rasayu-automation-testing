# Rasayu Clinical Management Portal - Automation Testing Framework

Enterprise-grade, human-engineered UI test automation framework built with **Python**, **Playwright**, and **pytest** for the **Rasayu Clinical Management Portal** (`http://54.169.232.62/admin/`).

---

## Architecture & Directory Structure

The framework is organized into modular directories ensuring strict separation of concerns, zero hardcoding, and complete portability across local machines and CI/CD servers.

```
rasayu-automation-testing/
│
├── shared-tools/                     # 100% Generic & Reusable Automation Utilities
│   ├── auth/                         # Authentication & generic login page object
│   ├── base/                         # Base page with resilient Playwright interactions
│   ├── components/                   # Universal UI components (Admin navigation, tables)
│   ├── popup/                        # Toast alerts, modals, and confirmation dialogues
│   ├── reporter/                     # Enterprise HTML reporter with Coreco branding & KPI cards
│   ├── test_data/                    # Universal Excel test data reader & pydantic data models
│   │   ├── Rasayu_Test_Cases.xlsx
│   │   └── Rasayu_Test_Data.xlsx
│   └── utils/                        # Logging, environment configuration, & screenshot management
│
├── master-management/                # Master Data Management Modules
│   ├── RAC/                          # Rasayu Cancer Clinic Masters
│   │   ├── create/
│   │   └── update/
│   └── DWC/                          # Doctor Wellness Clinic Masters
│       ├── create/
│       └── update/
│
├── transaction-management/           # Clinical Transaction & Patient Care Modules
│   ├── create/                       # New Transaction creation
│   └── update/                       # Transaction updates & clinical follow-ups
│       └── baseline-module/          # Baseline Visit Case Report Form (CRF) Module
│           ├── pages/                # Page objects (sub-tabs, patient directory, clinical forms)
│           ├── tests/                # 37 Automated pytest test suites (23 Positive + 14 Negative)
│           ├── baseline_data.py      # Module data adapter reading 'createbaseline' sheet
│           └── README.md             # Baseline module documentation
│
├── conftest.py                       # Root pytest fixtures, session hooks, screenshot hooks
├── pytest.ini                        # Pytest configuration and execution markers
├── requirements.txt                  # Python dependencies
├── .env.example                      # Template for environment variables (NO credentials in Git)
└── .gitignore                        # Git ignore rules (.env, screenshots, reports, pycache)
```

---

## Core Engineering Features

1. **Zero Hardcoded Data**:
   - Credentials strictly reside in local `.env` (never committed to version control).
   - All test payloads, patient identifiers, clinical options, and boundary values are dynamically read from Excel (`Rasayu_Test_Data.xlsx`) via generic helper models.
2. **Headless Execution by Default**:
   - `pytest` runs in headless mode by default for server and CI/CD efficiency.
   - Use `--headed` flag when visual interaction or debugging is desired.
3. **Automated Evidence & Screenshot Lifecycle**:
   - Automatically takes a full-page screenshot upon completion of every test case.
   - Named strictly by official Test Case ID (e.g. `TC-BASE-POS-01.png`).
   - Saved to the `screenshots/` directory and attached directly to the HTML test report.
   - **Vanish on Session Start**: The `screenshots/` directory is automatically wiped clean when starting a new automation test run.
   - **100-File FIFO Limit**: Retains at most 100 screenshots; older files are automatically purged based on modification time.
4. **Execution Summary & Report Popup**:
   - Generates an enterprise HTML report with KPIs, pie charts, and embedded screenshots.
   - Automatically shows a native UI summary popup at test completion allowing the user to view or launch the HTML report (gracefully suppresses without error on headless Linux/Docker environments without a display server).
5. **Decoupled Common Architecture**:
   - `shared-tools/` contains zero medical terms or module-specific logic, allowing seamless scaling to any future clinic or transaction module.

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Google Chrome or Chromium browser

### 2. Environment Setup
```powershell
# Clone the repository
git clone <repository-url>
cd rasayu-automation-testing

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your portal credentials:
```powershell
cp .env.example .env
```
Edit `.env`:
```ini
BASE_URL=http://54.169.232.62/admin/
ADMIN_USERNAME=ADMIN
ADMIN_PASSWORD=YourSecurePasswordHere
HEADLESS=true
DEFAULT_CLINIC=RAC
```

---

## Test Execution Commands

```powershell
# 1. Run all tests across the framework (Headless by default)
pytest

# 2. Run all tests in Headed mode (opens visible browser)
pytest --headed

# 3. Run only the Baseline Visit Module
pytest transaction-management/update/baseline-module/

# 4. Run Baseline Positive test suite (23 tests)
pytest transaction-management/update/baseline-module/tests/test_baseline_positive.py

# 5. Run Baseline Negative test suite (14 tests)
pytest transaction-management/update/baseline-module/tests/test_baseline_negative.py

# 6. Run a single specific test case by ID
pytest transaction-management/update/baseline-module/ -k "TC-BASE-POS-01"

# 7. Collect tests without executing
pytest --collect-only
```

---

## Test Coverage Matrix for Baseline Visit

| Category | File | Count | Scope |
|---|---|---|---|
| **Positive Tests** | `test_baseline_positive.py` | 23 | Authentication, Patient Directory search, Demographics, Allergies, Allopathy & Ayurvedic Diagnosis, Comorbidities, Family History, Medicines & Chemo, Chief Complaints, Vitals & ECOG, TNM Staging, Surgical & Radiation History, Lab Tests, Hetu Sevan, Clinical Prognosis, RAC Protocol, Physician Opinion, Form Submission. |
| **Negative Tests** | `test_baseline_negative.py` | 14 | Invalid login authentication, XSS script injection, future year validation, missing mandatory Ayurvedic parameters, incomplete family history, chronological date inversions, out-of-range ECOG status, negative vitals/dosage, zero fraction radiation, unauthorized RAC finalization, unsupported file upload (`.exe`), premature finalization, blank doctor opinions, mandatory fields validation. |
| **Total** | | **37** | **100% Automated Coverage** |

---

## Reporting & Artifacts

- **HTML Report**: Generated automatically at `pytest-report.html` and inside `reports/`.
- **Validation Screenshots**: Stored in `screenshots/<TEST_CASE_ID>.png`.
- **Log Files**: Execution logs saved under `reports/test_run.log`.
