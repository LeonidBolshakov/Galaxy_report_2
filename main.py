import sys

from PyQt6.QtWidgets import QApplication

from report import Report


def main() -> int:
    app = QApplication(sys.argv)
    window = Report()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
