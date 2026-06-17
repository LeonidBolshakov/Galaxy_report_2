# Galaxy Report

Desktop utility for preparing financial values for a monthly partner report to
the Galaktika corporation.

The application accepts the amount paid by customers and payments to the
corporation. VAT is calculated from the VAT percentage. The corporation transfer
percentage and VAT percentage are defined by program constants, but can be
adjusted in the interface for the current session.

## Features

- PyQt6 desktop interface based on a Qt Creator `.ui` file.
- Automatic calculation of:
  - customer amount without VAT;
  - corporation amount without VAT;
  - corporation amount including VAT;
  - total amount paid to the corporation;
  - remaining amount;
  - overpayment.
- Dynamic payment input rows: after entering a payment amount, the next payment
  field is created automatically.
- Input can be completed with `Tab`, `Enter`, or mouse focus change; `Enter`
  moves focus like `Tab`.
- Clicking any output field copies the result text to the clipboard.
- Copied output fields are highlighted.
- Output fields resize with the form, making long result strings easier to
  inspect before copying.
- Reference values — VAT percentage and corporation transfer percentage — can be
  changed only for the current session after explicit confirmation.
- Automated pytest coverage for calculations, formatting, UI behavior, dynamic
  payments, clipboard copy, and reference-value safeguards.

## Usage

1. Enter the amount paid by customers.
2. Enter payments to the corporation one by one.
3. After a payment amount is entered, the next payment field appears.
4. After all payments are entered, transfer the calculated results to the
   monthly corporation report.
5. Click any output field to copy the result text to the clipboard for insertion
   into the monthly corporation report.
6. If needed, adjust the corporation transfer percentage or VAT percentage for
   the current session.

## Business Rules

- All monetary values are rounded to kopecks.
- VAT percentage and corporation transfer percentage are defined by constants.
- Remaining amount and overpayment are mutually exclusive: when overpayment is
  positive, remaining amount is set to zero, and vice versa.
- Reference values are restored from constants after restarting the application.

## Screenshots

Initial form:

![Initial form](docs/images/galaxy-report-empty.png)

[Open initial form screenshot](docs/images/galaxy-report-empty.png)

Filled form with dynamic payment rows and copied output highlighting:

![Filled form](docs/images/galaxy-report-filled.png)

[Open filled form screenshot](docs/images/galaxy-report-filled.png)

Reference value confirmation:

![Reference value confirmation](docs/images/galaxy-report-reference-warning.png)

[Open reference value confirmation screenshot](docs/images/galaxy-report-reference-warning.png)

## Technology

- Python 3.14
- PyQt6
- num2words
- pytest
- PyInstaller

## Project Structure

```text
Galaxy_report_2/
├── _internal/report.ui      # Qt Creator interface
├── constants.py             # Application constants
├── functions.py             # Formatting, parsing, clipboard helpers
├── main.py                  # Application entry point
├── report.py                # Main window and business workflow
├── validatedlineedit.py     # Validated input widget
├── test_functions.py        # Tests for helper functions
├── test_report.py           # UI/workflow tests
├── docs/images/             # README screenshots
├── build_pyinstaller.bat    # PyInstaller build helper
├── requirements.txt         # Project dependencies
└── Galaxy_report.spec       # PyInstaller build spec
```

## Additional Documentation

- [Build exe](docs/build.md)
- [Project architecture](docs/architecture.md)

## Installation

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe main.py
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest .
```

Current verified result: `17 passed`.

## Build

```powershell
.\build_pyinstaller.bat
```

The executable is created in:

```text
dist\galaxy_report\galaxy_report.exe
```
