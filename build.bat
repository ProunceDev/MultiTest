@echo off
setlocal enabledelayedexpansion

echo ================================
echo Starting PyInstaller build script
echo ================================


REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed on this system.
    echo [ERROR] Please install Python from https://www.python.org/downloads/ and try again.
	pause
    exit /b 1
) else (
    echo [INFO] Python is already installed.
)

echo [INFO] Installing required libraries from requirements.txt.
REM Install required libraries from requirements.txt
if exist "requirements.txt" (
    echo [INFO] Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies from requirements.txt.
		pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed successfully.
) else (
    echo [ERROR] requirements.txt file not found. Please make sure it exists in the current directory.
	pause
    exit /b 1
)

REM Get the path to customtkinter using pip and log the result
for /f "tokens=2" %%i in ('pip show customtkinter ^| findstr Location') do set customtkinter_path=%%i\customtkinter
echo [INFO] customtkinter path: !customtkinter_path!

REM Set user_path relative to the folder the .bat script is run in (i.e., the MultiTest folder) and log it
set user_path=%~dp0
echo [INFO] User path (relative to script): !user_path!

REM Set icon path and log it
set icon_path=%user_path%assets\icon.ico
echo [INFO] Icon path: !icon_path!

REM Set main.py path and log it
set main_script=%user_path%main.py
echo [INFO] Main script path: !main_script!

REM Create a 'build' directory if it doesn't exist and cd into it
set build_path=%user_path%build
if not exist "!build_path!" (
    mkdir "!build_path!"
    echo [INFO] Created build directory: !build_path!
)

cd /d "!build_path!"
echo [INFO] Changed directory to: !build_path!

REM Log pyinstaller command before execution
echo [INFO] Running PyInstaller with the following command:
echo pyinstaller --noconfirm --onefile --windowed --icon "!icon_path!" --add-data "!customtkinter_path!;customtkinter/" "!main_script!"

REM Run PyInstaller command with dynamically retrieved paths
pyinstaller --noconfirm --onefile --windowed --icon "%icon_path%" --add-data "%customtkinter_path%;customtkinter/" "%main_script%"

REM Check if PyInstaller succeeded
if %ERRORLEVEL% equ 0 (
    echo ================================
    echo [SUCCESS] PyInstaller build completed successfully.
    echo ================================

    REM Move the compiled main.exe from the build folder to the MultiTest folder and rename it to MultiTest.exe
    if exist "!build_path!\dist\main.exe" (
        move /y "!build_path!\dist\main.exe" "!user_path!\MultiTest.exe"
        echo [INFO] Moved and renamed executable to: !user_path!\MultiTest.exe
    ) else (
        echo [ERROR] Compiled main.exe not found.
    )
) else (
    echo ================================
    echo [ERROR] PyInstaller build failed. Check the above output for details.
    echo ================================
)

pause
