# QA Evidence Collector

A Windows desktop application for QA/SDET professionals to capture, annotate, organize, and document manual test execution evidence — and automatically generate a formatted Word (.docx) report.

## Features

### Core
- Floating, always-on-top toolbar that sits over any application
- One-click / global hotkey (Ctrl+Shift+S) screenshot capture per test step
- Per-step note entry with thumbnail preview
- View, edit, reorder, and delete steps before generating the report
- Edit Test Case ID and Test Objective anytime during the session
- Automatic DOCX report generation with embedded screenshots and notes
- Session auto-save — resumes where you left off if the app closes unexpectedly
- Configurable output folder and hotkey via Settings dialog
- Packaged as a standalone Windows `.exe` — no Python required

### Image Annotation (V1.1)
- **Arrow tool** — click and drag to draw directional arrows pointing at UI elements
- **Text tool** — click anywhere to place text labels; auto-contrast background (black/white) based on image brightness; double-click to edit; draggable
- **Highlight tool** — drag to draw semi-transparent coloured rectangles; 8-handle resize
- **Blur tool** — drag to pixelate/blur regions containing sensitive data; 8-handle resize
- **Colour picker** — single colour selector applies to Arrow and Highlight tools; persists across steps
- **Undo / Clear** — step-by-step undo or clear all annotations at once
- **Zoom controls** — Ctrl+scroll wheel zoom, Fit and 100% buttons
- **Test Result** — select Pass or Fail before generating the report; shown in colour on the report title page

## Download

Grab the latest `QAEvidenceCollector.exe` from the [`dist/`](dist/) folder or the [Releases](../../releases) page and double-click to run. No installation required.

## Workflow

1. Launch `QAEvidenceCollector.exe`
2. Click **New Session** — enter a Test Case ID and Test Objective
3. Perform your test step in the application under test
4. Click **Capture Step** or press **Ctrl+Shift+S** — screenshot is taken
5. **Annotation Editor opens** — draw arrows, add text, highlight areas, blur sensitive data, then click **Done**
6. Enter a note for the step and click **Save**
7. Repeat steps 3–6 for each test step
8. Click **View Steps** to review, reorder, edit notes, or delete steps
9. Click **Generate Report** — select **Pass** or **Fail**, then a formatted `.docx` report is saved and can be opened immediately

## Report Output

Each session produces a `.docx` file in a folder named after the Test Case ID:

```
TC-001\
├── step_001_143022.png
├── step_002_143158.png
└── TC-001_01.docx
```

The report includes:
- **Title page** with Test Case ID, Test Objective, Test Result (green PASSED / red FAILED), date/time, and total steps
- **Per-step pages** with step number, note, and full annotated screenshot

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
│   │   ├── toolbar.py              # Floating always-on-top toolbar
│   │   ├── annotation_editor.py    # Image annotation canvas and tools
│   │   ├── new_session_dialog.py   # New session form
│   │   ├── note_dialog.py          # Per-step note entry
│   │   ├── step_list_view.py       # Step gallery with edit/reorder/delete
│   │   ├── test_result_dialog.py   # Pass / Fail selector dialog
│   │   └── settings_dialog.py      # Settings UI
│   ├── core/             # Business logic
│   │   ├── session_manager.py      # Session state and step management
│   │   ├── step.py                 # Step data model
│   │   └── hotkey_manager.py       # Global hotkey listener
│   ├── services/         # External integrations
│   │   ├── screenshot_service.py   # Screen capture using mss
│   │   ├── report_service.py       # DOCX generation using python-docx
│   │   └── storage_service.py      # Session auto-save/load (JSON)
│   ├── config/
│   │   └── settings.py             # App settings persistence
│   └── resources/icons/            # SVG icons
├── docs/                 # Project documentation
├── qa_evidence_collector.spec      # PyInstaller build spec
├── requirements.txt
└── pyproject.toml
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| GUI | PySide6 (Qt for Python) |
| Annotation canvas | QGraphicsScene / QGraphicsView |
| Screenshot | mss |
| Report | python-docx |
| Image processing | Pillow |
| Global hotkeys | pynput |
| Packaging | PyInstaller |

## Version History

### V1.1 — Image Annotation
| Sprint | Deliverable |
|--------|-------------|
| S1 | Annotation editor window — dark modern UI |
| S2 | Arrow tool |
| S3 | Text tool — draggable, word-wrap, auto-contrast background |
| S4 | Highlight tool — drag to draw, 8-handle resize, zoom controls |
| S5 | Blur / pixelate tool — drag to select, 8-handle resize |
| S6 | Undo / Clear functionality |
| S7 | Save annotated image, wired into step flow and report |
| S8 | Colour picker — single colour for Arrow and Highlight tools |
| S9 | Test Result Pass/Fail — dialog before report, shown in report |
| S10 | Polish, testing, rebuild `.exe` |

### V1.0 — Core
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

## Roadmap

| Version | Feature |
|---------|---------|
| V1.2 | PDF export option in addition to DOCX |
| V2.0 | Jira / TestRail integration |
| V2.1 | Cloud sync for session backup |
| V2.2 | macOS / Linux builds |
| V3.0 | Team / shared workspace mode |
