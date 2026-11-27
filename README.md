# Rasayu Clinical Management Portal - Automation Testing Framework

Enterprise-grade, human-engineered UI test automation framework built with **Python**, **Playwright**, and **pytest** for the **Rasayu Clinical Management Portal** (`http://54.169.232.62/admin/`).

---

## 🏛️ Architecture & Directory Structure

The framework is organized into decoupled, modular packages adhering strictly to **PEP-8 naming standards**, **Zero Hardcoding**, and full portability across local workstations and CI/CD environments.

```
rasayu-automation-testing/
│
├── .github/
│   └── workflows/
│       └── ci.yml                            # GitHub Actions CI workflow (Headless execution & artifact uploads)
│
├── shared_tools/                             # Universal, 100% Generic Automation Core
│   ├── auth/                                 # Multi-role authentication & generic login page object
│   ├── base/                                 # BasePage with resilient Playwright actions & keyboard shortcuts
│   ├── components/                           # Reusable UI components (Admin navigation, clinic switcher, tables)
│   ├── data_engine/                          # Dynamic Excel test data reader & Pydantic data models
│   ├── popup/                                # Toast alerts, modal dialogs, and native summary popup
│   ├── reporter/                             # Enterprise HTML reporter with Coreco branding & KPI summary cards
│   └── utils/                                # Logging, environment configuration, & screenshot lifecycle management
│
├── test_data/                                # Excel Test Datasets (Single Source of Truth)
│   ├── Rasayu_Test_Cases (3).xlsx            # Standardized manual test case definitions
│   └── Rasayu_Test_Data (3).xlsx             # Dynamic data sheets for all modules, clinics, and CRUD flows
│
├── transaction_management/                   # Clinical Transaction & Patient Care Modules
│   └── baseline_module/                      # Baseline Visit Case Report Form (CRF) CRUD (43 tests)
│       ├── pages/                            # Decoupled Page Objects (Common, Disease, Hetu Sevan, Physician RAC)
│       ├── tests/                            # Pytest suites: create/, read/, update/, delete/ (Positive & Negative)
│       ├── baseline_data.py                  # Module data adapter reading 'createbaseline' & 'updatebaseline'
│       └── README.md                         # Transaction baseline module documentation
│
├── master_management/                        # Master Data Management Modules (CRUD across Clinics)
│   ├── conftest.py                           # Master management clinic switcher & admin navigation fixtures
│   │
│   ├── rac_clinic_masters/                   # Rasayu Ayurved Clinic (RAC) Masters (105 tests)
│   │   ├── conftest.py                       # RAC clinic-specific fixtures & setup
│   │   ├── baseline_module/                  # RAC Baseline Masters CRUD (76 tests)
│   │   │   ├── pages/                        # MasterBasePage, MasterCreatePage, Read/Update/Delete pages
│   │   │   ├── tests/                        # create/, read/, update/, delete/ test suites
│   │   │   ├── rac_baseline_data.py          # Data adapter reading 'master-rac-createbaseline' / update
│   │   │   └── README.md
│   │   ├── visit_module/                     # RAC Visit Masters CRUD (29 tests)
│   │   │   ├── pages/                        # VisitMasterPage
│   │   │   ├── tests/                        # create/, read/, update/, delete/ test suites
│   │   │   ├── rac_visit_data.py             # Data adapter reading 'master-rac-createvisit' / update
│   │   │   └── README.md
│   │   └── OnExam_module/                    # Scaffolding for RAC On Examination masters
│   │
│   └── dwc_clinic_masters/                   # Doctor Wellness Clinic (DWC) Masters (141 tests)
│       ├── conftest.py                       # DWC clinic-specific fixtures & setup
│       ├── baseline_module/                  # DWC Baseline Masters CRUD (112 tests)
│       │   ├── pages/                        # DwcMasterBasePage, DwcCreatePage, DwcUpdatePage, DwcDeletePage
│       │   ├── tests/                        # create/, update/, delete/ test suites
│       │   ├── dwc_baseline_data.py          # Data adapter reading 'master-dwc-createbaseline' / update
│       │   └── README.md
│       ├── visit_module/                     # DWC Visit Masters CRUD (29 tests)
│       │   ├── pages/                        # DwcVisitMasterPage
│       │   ├── tests/                        # create/, read/, update/, delete/ test suites
│       │   ├── dwc_visit_data.py             # Data adapter reading 'master-dwc-createvisit' / update
│       │   └── README.md
│       └── OnExam_module/                    # Scaffolding for DWC On Examination masters
│
├── conftest.py                               # Root pytest fixtures, session hooks, screenshot hooks
├── pytest.ini                                # Pytest configuration, markers, testpaths, and logging rules
├── requirements.txt                          # Python dependencies
├── .env.example                              # Template for environment variables (NO secrets in Git)
└── .gitignore                                # Git ignore rules (.env, screenshots/, reports/, pycache)
```

---

## ⚡ Core Engineering Principles

1. **Zero Hardcoded Data**:
   - Authentication credentials strictly reside in local `.env` (never committed to version control).
   - All test payloads, patient identifiers, clinical options, dropdown targets, and boundary values are dynamically read from Excel (`test_data/Rasayu_Test_Data (3).xlsx`) through dedicated module data adapters.
2. **Headless Execution by Default**:
   - `pytest` runs in headless mode by default for high-speed local and CI/CD execution.
   - Use `--headed` flag whenever visual interaction or step-by-step debugging is required.
3. **Automated Evidence & Screenshot Lifecycle**:
   - Full-page screenshots are automatically captured upon completion of every test case.
   - Standardized naming convention based on official Test Case IDs (e.g. `TC-BASE-CREATE-POS-01.png`, `TC-MASTER-BASE-RAC-02.png`).
   - Saved to the `screenshots/` directory and embedded directly into the HTML test report.
   - **Vanish on Session Start**: The `screenshots/` directory is automatically wiped clean when starting a new test run.
   - **100-File FIFO Retention**: Retains at most 100 screenshots; older files are automatically purged based on modification time.
4. **Execution Summary & Report Popup**:
   - Generates an enterprise-branded HTML report (`reports/pytest-report.html`) complete with pass/fail KPIs, duration metrics, and embedded screenshots.
   - Displays a native desktop summary popup upon test completion allowing one-click launching of the HTML report (gracefully suppresses without error on headless Linux/Docker environments without a display server).
5. **Decoupled Architecture**:
   - `shared_tools/` contains zero medical terms or module-specific logic, allowing seamless scaling to any future clinic, module, or transaction workflow.

---

## 📊 Test Inventory & Coverage (289 Automated Test Cases)

| Clinic / Domain | Module | CRUD Operation | Tests | Scope & Key Features Covered |
| :--- | :--- | :---: | :---: | :--- |
| **Transaction Management** | Baseline Visit CRF | Full CRUD | **43** | Demographics, Allergies, Diagnosis, Comorbidities, Family History, Medicines & Chemo, Chief Complaints, Vitals & ECOG, TNM Staging, Surgical/Radiation History, Hetu Sevan, Physician Opinion, Form Submission + 17 Boundary/Negative validations. |
| **RAC Clinic Masters** | Baseline Module | Full CRUD | **76** | Marital Status, Consanguineous, Allergy Types, Disease Group/Type/Stage/Grading, Ayurvedic Nidan, Avastha, Avayava/Srotas/Dosha/Dhatu Vikriti, Therapy Response, Lineage, Obstetric History, Medicine Forms/Brands/Units, Chemo Regimens + 28 Negative cases. |
| **RAC Clinic Masters** | Visit Module | Full CRUD | **29** | Follow-up visit clinical masters: Symptoms Type, Treatment Tolerability, Disease Progression, Adverse Drug Reactions, Compliance, Examination Findings + 12 Negative cases. |
| **DWC Clinic Masters** | Baseline Module | Full CRUD | **112** | Doctor Wellness Clinic baseline master categories: Wellness Demographics, Lifestyle Habits, Prakriti/Vikriti, Metabolic Profiles, Preventive Protocols, Dietetics, Therapies + 21 Negative cases. |
| **DWC Clinic Masters** | Visit Module | Full CRUD | **29** | Doctor Wellness Clinic follow-up visit masters: Vital Signs, Wellness Score, Routine Adherence, Dietary Logs, Session Feedback + 12 Negative cases. |
| **Total Automated Suite** | | | **289** | **100% Automated Enterprise Test Catalog (0 Errors)** |

---

## 🌿 Git Branching Strategy & Remote Repositories

The project repository ([himanshu-prakash-test/rasayu-automation-testing](https://github.com/himanshu-prakash-test/rasayu-automation-testing)) features dedicated feature branches for isolated review and zero-conflict integration:

| Branch Name | Clinic & Module | Test Scope | Remote Status |
| :--- | :--- | :---: | :--- |
| **`main`** | **Production Core** | **289 Tests** | ✅ Up-to-date with `origin/main` |
| **`rac/baseline`** | RAC Clinic — Baseline Module | 76 Tests | ✅ Pushed (`origin/rac/baseline`) |
| **`rac/visit`** | RAC Clinic — Visit Module | 29 Tests | ✅ Pushed (`origin/rac/visit`) |
| **`dwc/baseline`** | DWC Clinic — Baseline Module | 112 Tests | ✅ Pushed (`origin/dwc/baseline`) |
| **`dwc/visit`** | DWC Clinic — Visit Module | 29 Tests | ✅ Pushed (`origin/dwc/visit`) |
| **`feat/transaction-baseline-crud`** | Transaction Management — Baseline CRF | 43 Tests | ✅ Pushed & Merged |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Google Chrome or Chromium browser

### 2. Environment Setup
```powershell
# Clone the repository
git clone https://github.com/himanshu-prakash-test/rasayu-automation-testing.git
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

## 💻 Test Execution Commands

### 1. Run the Entire Automation Suite (289 Tests)
```powershell
# Run all tests in headless mode (default)
pytest

# Run all tests with visible browser window
pytest --headed

# Dry-run / test collection check without executing
pytest --collect-only -q
```

### 2. Run by Clinic
```powershell
# Run all RAC Clinic Master tests (105 tests)
pytest master_management/rac_clinic_masters/

# Run all DWC Clinic Master tests (141 tests)
pytest master_management/dwc_clinic_masters/

# Run all Transaction Management tests (43 tests)
pytest transaction_management/
```

### 3. Run by Module
```powershell
# Run RAC Baseline Module (76 tests)
pytest master_management/rac_clinic_masters/baseline_module/

# Run RAC Visit Module (29 tests)
pytest master_management/rac_clinic_masters/visit_module/

# Run DWC Baseline Module (112 tests)
pytest master_management/dwc_clinic_masters/baseline_module/

# Run DWC Visit Module (29 tests)
pytest master_management/dwc_clinic_masters/visit_module/
```

### 4. Run by CRUD Operation
```powershell
# Run ONLY Create test suites across the framework
pytest -k "create"

# Run ONLY Read / Inspection test suites
pytest -k "read"

# Run ONLY Update / Modification test suites
pytest -k "upd or update"

# Run ONLY Delete / Deactivation test suites
pytest -k "del or delete"
```

### 5. Run by Test Category (Positive vs Negative)
```powershell
# Run only Positive test scenarios
pytest -k "pos"

# Run only Negative / Boundary validation scenarios
pytest -k "neg"
```

### 6. Run a Single Specific Test Case by ID
```powershell
# Example: Run RAC Master Baseline Create Positive Test Case 02
pytest -k "TC-MASTER-BASE-RAC-02"

# Example: Run Transaction Baseline Create Positive Test Case 01
pytest -k "test_tc_base_create_pos_01"
```

---

## 📈 Reports & Test Artifacts

After execution, the following artifacts are generated automatically in the project root:

- **HTML Report**: `reports/pytest-report.html` (Complete with KPI cards, summary charts, stack traces, and embedded screenshots).
- **JUnit XML Report**: `reports/junit.xml` (For CI/CD test result parsing).
- **Screenshots**: `screenshots/*.png` (Full-page captures for all executed test cases).
- **Summary Popup**: Automatically appears on Windows/macOS desktop upon completion of test runs.
