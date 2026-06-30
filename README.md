# QA Evidence Collector

A Windows desktop application for QA/SDET professionals to capture, organize, and document manual test execution evidence — and automatically generate a formatted Word (.docx) report.

## Features (planned)

- Floating, always-on-top toolbar
- One-click / hotkey screenshot capture per test step
- Per-step notes and auto-numbering
- Automatic DOCX report generation
- Local session save/load

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (cmd):** `.venv\Scripts\activate.bat`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python -m qa_evidence_collector.main
```

Or from the `src/` directory:

```bash
cd src
python -m qa_evidence_collector.main
```

## Project Structure

```
qa-evidence-collector/
├── src/qa_evidence_collector/
│   ├── ui/          # PySide6 windows and dialogs
│   ├── core/        # Session management, data models
│   ├── services/    # Screenshot, report, and storage services
│   ├── config/      # Settings management
│   └── resources/   # Icons and report templates
├── tests/           # Unit tests
├── docs/            # Project documentation
├── requirements.txt
└── pyproject.toml
```

## Tech Stack

- **Python 3.11+**
- **PySide6** — GUI framework
- **mss** — Screenshot capture
- **python-docx** — DOCX report generation
- **Pillow** — Image processing
- **pynput** — Global hotkeys
- **PyInstaller** — Packaging to .exe
