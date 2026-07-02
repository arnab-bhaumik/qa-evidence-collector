# Build script for QA Evidence Collector
# Run from project root with venv activated:
#   .venv\Scripts\Activate.ps1
#   .\build_exe.ps1

Write-Host "Building QA Evidence Collector..." -ForegroundColor Cyan

python -m PyInstaller qa_evidence_collector.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable: dist\QAEvidenceCollector.exe" -ForegroundColor Green
} else {
    Write-Host "Build failed." -ForegroundColor Red
}
