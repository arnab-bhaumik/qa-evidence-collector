# QA Evidence Collector — Project Proposal

## 1. Executive Summary

QA Evidence Collector is a Windows desktop application built for QA / SDET professionals to capture, organize, and document manual test execution evidence quickly and consistently. Manual testers routinely need to capture screenshots at each step of a test case, annotate them, and compile them into a shareable report (typically a Word document) for bug reports, test execution records, or audit/compliance purposes. Today this is usually done manually — taking screenshots one by one, renaming files, pasting them into Word, and formatting everything by hand. This is slow, repetitive, and error-prone.

QA Evidence Collector solves this by providing a lightweight floating toolbar that sits on top of any application, lets the tester capture and tag screenshots step-by-step during a test run, and then automatically generates a clean, professional DOCX report with all steps, screenshots, and notes in order.

This project also serves as a portfolio piece demonstrating desktop application development, automation tooling, and practical QA-engineering problem solving — relevant to SDET / QA Automation roles.

## 2. Business Problem

- Manual testers waste significant time on repetitive screenshot capture and report formatting during test execution.
- Evidence (screenshots) gets disorganized — files end up unsorted, unlabeled, or lost across folders.
- Report formatting is inconsistent across testers/teams, making test evidence harder to review.
- Existing screenshot tools are general-purpose; none are tailored to the "step 1 → step 2 → step 3 → generate report" workflow that testers actually follow.

## 3. Project Objective

Build a desktop application that allows a tester to:
1. Start a test session.
2. Capture a screenshot for each test step with one click/hotkey.
3. Add a short note/description per step.
4. Automatically generate a well-formatted Word (.docx) report containing all steps, screenshots, and notes at the end of the session.

The goal is to reduce evidence-collection and report-writing time from many minutes per test case to a few seconds per step.

## 4. Scope (Version 1)

### In Scope
- Floating, always-on-top toolbar UI
- Start / pause / stop test session
- Per-step screenshot capture (full screen and/or active window)
- Per-step text note/description entry
- Step reordering / deletion before report generation
- Auto-numbering of steps
- DOCX report generation with embedded screenshots, step numbers, notes, and timestamps
- Local session save/load (in case the app is closed mid-session)
- Basic settings (screenshot save location, report template, hotkeys)
- Packaging as a standalone Windows executable (no Python install required for end users)

### Out of Scope (Version 1)
- Cloud sync / multi-user collaboration
- Video/screen recording
- Integration with test management tools (Jira, TestRail, etc.) — planned for future roadmap
- Mac/Linux builds (Windows-first; cross-platform feasibility considered later since PySide6 supports it)
- Image annotation tools (arrows, highlights, blur) — candidate for V1.1

## 5. Complete User Workflow

1. User launches QA Evidence Collector.
2. A small floating toolbar appears, always on top of other windows.
3. User clicks **New Session**, optionally enters a test case name/ID.
4. User performs the manual test step in their application under test.
5. User clicks **Capture Step** (or presses a global hotkey).
6. The app takes a screenshot, adds it as a new step, and opens a small note field for the user to describe the step.
7. User repeats steps 4–6 for each test step.
8. At any point, user can view the step list, reorder steps, delete a bad capture, or re-capture.
9. When testing is complete, user clicks **Generate Report**.
10. The app compiles all steps (screenshot + step number + note + timestamp) into a formatted DOCX file and saves it to the configured output folder.
11. User can open the report directly from the app or from the output folder.

## 6. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | The app shall display a floating, always-on-top toolbar. |
| FR-2 | The user shall be able to start a new evidence-collection session with a name/ID. |
| FR-3 | The user shall be able to capture a screenshot (full screen or active window) via button click or global hotkey. |
| FR-4 | Each captured screenshot shall become a "step" with an auto-incremented step number. |
| FR-5 | The user shall be able to attach/edit a text note for each step. |
| FR-6 | The user shall be able to view a list/thumbnail gallery of all captured steps in the current session. |
| FR-7 | The user shall be able to delete or reorder steps before generating the report. |
| FR-8 | The user shall be able to generate a DOCX report compiling all steps in order. |
| FR-9 | The report shall include: report title/test case name, generation date, and for each step — step number, screenshot, note, and timestamp. |
| FR-10 | The app shall allow configuration of the screenshot/report output folder. |
| FR-11 | The app shall persist an in-progress session to disk so it isn't lost if the app closes unexpectedly. |
| FR-12 | The app shall be distributable as a single Windows executable via PyInstaller. |

## 7. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.11+ | Core application logic |
| GUI Framework | PySide6 (Qt for Python) | Floating toolbar, windows, dialogs |
| Screenshot Capture | `mss` | Fast, cross-platform screen capture |
| Report Generation | `python-docx` | Generating formatted Word documents |
| Image Handling | `Pillow` | Image processing/resizing before embedding |
| Global Hotkeys | `keyboard` or `pynput` | Capture screenshots without focusing the app |
| Data/Session Storage | JSON (local file) | Lightweight session persistence |
| Packaging | PyInstaller | Building a standalone .exe |
| Version Control | Git + GitHub | Source control, portfolio visibility |
| AI-assisted Development | Claude Code | Implementation, debugging, refactoring |

## 8. Suggested Folder Structure

```
qa-evidence-collector/
│
├── docs/
│   ├── 01_PROJECT_PROPOSAL.md
│   ├── 02_SOFTWARE_REQUIREMENTS_SPECIFICATION.md
│   ├── 03_SYSTEM_ARCHITECTURE.md
│   ├── 04_GITHUB_COPILOT_GUIDE.md
│   └── 05_DEVELOPER_GUIDE.md
│
├── src/
│   └── qa_evidence_collector/
│       ├── __init__.py
│       ├── main.py                  # Application entry point
│       ├── ui/
│       │   ├── toolbar.py           # Floating toolbar widget
│       │   ├── startup_window.py    # New session / open session screen
│       │   ├── step_list_view.py    # Step gallery/list UI
│       │   ├── note_dialog.py       # Note entry dialog per step
│       │   └── settings_dialog.py   # Settings UI
│       │
│       ├── core/
│       │   ├── session_manager.py   # Session state, step ordering
│       │   ├── step.py              # Step data model
│       │   └── hotkey_manager.py    # Global hotkey listener
│       │
│       ├── services/
│       │   ├── screenshot_service.py  # Capture logic using mss
│       │   ├── report_service.py      # DOCX generation using python-docx
│       │   └── storage_service.py     # Save/load session JSON
│       │
│       ├── config/
│       │   └── settings.py          # App settings load/save
│       │
│       └── resources/
│           ├── icons/
│           └── templates/
│               └── report_template.docx
│
├── tests/
│   ├── test_screenshot_service.py
│   ├── test_report_service.py
│   └── test_session_manager.py
│
├── build/                           # PyInstaller build artifacts (gitignored)
├── dist/                            # Packaged executable (gitignored)
│
├── .gitignore
├── requirements.txt
├── README.md
└── pyproject.toml
```

## 9. Coding Principles

- **Separation of concerns**: UI (`ui/`), business logic (`core/`), and external integrations (`services/`) are kept in distinct layers.
- **Single Responsibility**: each module/class does one job (e.g., `screenshot_service.py` only handles capture, `report_service.py` only handles DOCX generation).
- **Testability**: core logic (session management, report generation) is written independently of the UI so it can be unit tested without launching the GUI.
- **Configuration over hardcoding**: paths, hotkeys, and template settings live in `config/settings.py`, not scattered through the code.
- **Incremental development**: build and commit one module per sprint, validate it works, then move to the next.
- **Consistent naming and typing**: use type hints throughout; follow PEP 8.

## 10. Working Functions (Core Modules Overview)

- **`session_manager.py`** — Creates a new session, holds the ordered list of `Step` objects, handles add/remove/reorder, and triggers autosave.
- **`screenshot_service.py`** — Captures the full screen or active window using `mss`, returns an image object/file path to be attached to a step.
- **`report_service.py`** — Takes a completed session (list of steps with screenshots + notes) and generates a formatted DOCX file: title page, per-step heading, embedded image, note text, and timestamp.
- **`storage_service.py`** — Serializes/deserializes session state to/from a local JSON file so in-progress sessions survive an app restart.
- **`hotkey_manager.py`** — Registers a global hotkey (e.g., `Ctrl+Shift+S`) so the user can capture a step without switching window focus to the toolbar.
- **`toolbar.py`** — The always-on-top floating widget with buttons for capture, view steps, settings, and generate report.

## 11. Future Roadmap

- **V1.1**: Image annotation (arrows, text, highlight, blur sensitive data).
- **V1.2**: Multiple report templates (PDF export option in addition to DOCX).
- **V2.0**: Integration with Jira/TestRail to attach generated reports directly to test cases or bug tickets.
- **V2.1**: Cloud sync for session backup across machines.
- **V2.2**: macOS/Linux builds.
- **V3.0**: Team/shared workspace mode for collaborative test evidence collection.

## 12. Resume Value

This project demonstrates:
- Desktop application development in Python (PySide6/Qt)
- Practical understanding of QA/test execution workflows
- File I/O, image processing, and document generation
- Application packaging and distribution (PyInstaller)
- Clean software architecture and incremental, version-controlled development
- Direct relevance to SDET / QA Automation Engineer roles, showing initiative in building tooling that solves a real testing pain point

## 13. Suggested Development Plan (Sprints)

| Sprint | Deliverable |
|--------|-------------|
| 1 | Project scaffolding, folder structure, dependency setup, basic startup window |
| 2 | Floating toolbar UI |
| 3 | Session manager + step data model |
| 4 | Screenshot capture service (`mss`) |
| 5 | DOCX report generation (`python-docx`) |
| 6 | Settings dialog + global hotkey support |
| 7 | Session persistence (save/load JSON) |
| 8 | Packaging with PyInstaller + final polish/testing |

Sprint 1 — Project Scaffolding & Startup Window

Goal: Set up the project foundation and confirm the environment works end to end.


Create the full folder structure as defined in section 8.
Create requirements.txt with all dependencies from section 7.
Create pyproject.toml and .gitignore.
Create main.py as the application entry point.
Create a minimal startup_window.py (PySide6) that opens a blank window titled "QA Evidence Collector".
Create README.md with project description and setup instructions.
Deliverable: Running main.py opens a blank PySide6 window with no errors.


Sprint 2 — Floating Toolbar

Goal: Build the always-on-top floating toolbar that becomes the main interaction point during a test session.


Create toolbar.py in ui/ as a frameless, always-on-top PySide6 widget.
Add toolbar buttons: New Session, Capture Step, View Steps, Generate Report, Settings.
Make the toolbar draggable and keep it on top of other application windows.
Wire button clicks to placeholder functions/print statements (no real logic yet — that comes in later sprints).
Deliverable: Launching the app shows the floating toolbar on top of other windows, and each button responds to a click (even if just logging to console for now).