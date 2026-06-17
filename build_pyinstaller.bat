@echo off
setlocal

cd /d "%~dp0"

set "PYTHON=.venv\Scripts\python.exe"
set "SPEC_FILE=Galaxy_report.spec"
set "APP_EXE=%CD%\dist\galaxy_report\galaxy_report.exe"

if not exist "%PYTHON%" (
    echo Virtual environment was not found: %PYTHON%
    echo Create it and install dependencies first.
    echo.
    pause
    exit /b 1
)

if not exist "%SPEC_FILE%" (
    echo Spec file was not found: %SPEC_FILE%
    echo.
    pause
    exit /b 1
)

"%PYTHON%" -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed in the virtual environment.
    echo Install it with:
    echo     "%PYTHON%" -m pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo Building application with PyInstaller...
"%PYTHON%" -m PyInstaller --clean --noconfirm "%SPEC_FILE%"
if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Build completed: %APP_EXE%
echo.
echo Run the application from the dist folder, not from the build folder.
pause
