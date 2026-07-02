# QA Evidence Collector

A Windows desktop application for QA/SDET professionals to capture, organize, and document manual test execution evidence — and automatically generate a formatted Word (.docx) report.

## Features

- Floating, always-on-top toolbar that sits over any application
- One-click / global hotkey (Ctrl+Shift+S) screenshot capture per test step
- Per-step note entry with thumbnail preview
- View, edit, reorder, and delete steps before generating the report
- Edit Test Case ID and Test Objective anytime during the session
- Automatic DOCX report generation with embedded screenshots and notes
- Session auto-save — resumes where you left off if the app closes unexpectedly
- Configurable output folder and hotkey via Settings dialog
- Packaged as a standalone Windows `.exe` — no Python required

## Download

Grab the latest `QAEvidenceCollector.exe` from the [`dist/`](dist/) folder or the [Releases](../../releases) page and double-click to run.

## Workflow

1. Launch `QAEvidenceCollector.exe`
2. Click **New Session** — enter a Test Case ID and Test Objective
3. Perform your test step in the application under test
4. Click **Capture Step** or press **Ctrl+Shift+S** — a screenshot is taken and a note dialog appears
5. Repeat steps 3–4 for each test step
6. Click **View Steps** to review, reorder, edit notes, or delete steps
7. Click **Generate Report** — a formatted `.docx` file is saved and can be opened immediately

## Setup (for development)

### Prerequisites
- Python 3.11+
- Windows 10/11

### 1. Clone the repository

```bash
git clone https://github.com/arnab-bhaumik/qa-evidence-collector.git
cd qa-evidence-collector
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the application

```powershell
cd src
python -m qa_evidence_collector.main
```

## Build the executable

From the project root with the venv activated:

```powershell
python -m PyInstaller qa_evidence_collector.spec --clean --noconfirm
```

Output: `dist\QAEvidenceCollector.exe`

## Project Structure

```
qa-evidence-collector/
├── src/qa_evidence_collector/
│   ├── ui/               # PySide6 windows and dialogs
│   │   ├── toolbar.py            # Floating always-on-top toolbar
│   │   ├── new_session_dialog.py # New session form
│   │   ├── note_dialog.py        # Per-step note entry
│   │   ├── step_list_view.py     # Step gallery with edit/reorder/delete
│   │   └── settings_dialog.py    # Settings UI
│   ├── core/             # Business logic
│   │   ├── session_manager.py    # Session state and step management
│   │   ├── step.py               # Step data model
│   │   └── hotkey_manager.py     # Global hotkey listener
│   ├── services/         # External integrations
│   │   ├── screenshot_service.py # Screen capture using mss
│   │   ├── report_service.py     # DOCX generation using python-docx
│   │   └── storage_service.py    # Session auto-save/load (JSON)
│   ├── config/
│   │   └── settings.py           # App settings persistence
│   └── resources/icons/          # SVG icons
├── tests/                # Unit tests
├── docs/                 # Project documentation
├── qa_evidence_collector.spec    # PyInstaller build spec
├── build_exe.ps1                 # Build helper script
├── requirements.txt
└── pyproject.toml
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| GUI | PySide6 (Qt for Python) |
| Screenshot | mss |
| Report | python-docx |
| Image processing | Pillow |
| Global hotkeys | pynput |
| Packaging | PyInstaller |

## Sprints Completed

| Sprint | Deliverable |
|--------|-------------|
| 1 | Project scaffolding, folder structure, startup window |
| 2 | Floating always-on-top toolbar UI |
| 3 | Session manager + step data model |
| 4 | Screenshot capture service + note dialog + view steps |
| 5 | DOCX report generation |
| 6 | Settings dialog + global hotkey support |
| 7 | Session persistence (auto-save / resume) |
| 8 | PyInstaller packaging → standalone `.exe` |
