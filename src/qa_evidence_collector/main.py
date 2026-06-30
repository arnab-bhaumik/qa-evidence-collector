import sys

from PySide6.QtWidgets import QApplication

from qa_evidence_collector.ui.toolbar import FloatingToolbar


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("QA Evidence Collector")
    app.setOrganizationName("QATools")

    toolbar = FloatingToolbar()
    toolbar.move(100, 100)
    toolbar.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
