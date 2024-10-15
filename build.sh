#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "========================"
echo "Starting PyInstaller build script"
echo "========================"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "[INFO] Python is already installed."
else
    echo "[ERROR] Python is not installed on this system."
    echo "[ERROR] Please install Python from https://www.python.org/downloads/ and try again."
    exit 1
fi

# Check if pip is installed
if command -v pip3 &>/dev/null; then
    echo "[INFO] Pip is already installed."
else
    echo "[ERROR] Pip is not installed on this system."
    echo "[ERROR] Please install Pip and try again."
    exit 1
fi

echo "[INFO] Installing required libraries from requirements.txt."

# Install required libraries from requirements.txt
if [[ -f "requirements.txt" ]]; then
    echo "[INFO] Installing dependencies from requirements.txt..."
    python3 -m pip install -r requirements.txt
    echo "[SUCCESS] Dependencies installed successfully."
else
    echo "[ERROR] requirements.txt file not found. Please make sure it exists in the current directory."
    exit 1
fi

# Get the path to customtkinter using pip and log the result
customtkinter_path=$(python3 -m pip show customtkinter | grep Location | awk '{print $2}')/customtkinter
echo "[INFO] customtkinter path: $customtkinter_path"

# Set user_path relative to the folder the script is run in (i.e., the MultiTest folder) and log it
user_path=$(dirname "$(realpath "$0")")
echo "[INFO] User path (relative to script): $user_path"

# Set icon path and log it
icon_path="$user_path/assets/icon.ico"
echo "[INFO] Icon path: $icon_path"

# Set main.py path and log it
main_script="$user_path/main.py"
echo "[INFO] Main script path: $main_script"

# Create a 'build' directory if it doesn't exist and cd into it
build_path="$user_path/build"
mkdir -p "$build_path"
echo "[INFO] Created build directory: $build_path"

cd "$build_path"
echo "[INFO] Changed directory to: $build_path"

# Log pyinstaller command before execution
echo "[INFO] Running PyInstaller with the following command:"
echo "pyinstaller --noconfirm --onefile --windowed --icon \"$icon_path\" --add-data \"$customtkinter_path:customtkinter/\" \"$main_script\""

# Run PyInstaller command with dynamically retrieved paths
pyinstaller --noconfirm --onefile --windowed --hidden-import='PIL._tkinter_finder' --icon "$icon_path" --add-data "$customtkinter_path:customtkinter/" "$main_script"

# Check if PyInstaller succeeded
if [[ $? -eq 0 ]]; then
    echo "========================"
    echo "[SUCCESS] PyInstaller build completed successfully."
    echo "========================"

    # Move the compiled executable from the build folder to the MultiTest folder and rename it to MultiTest
    if [[ -f "dist/main" ]]; then
        mv -f "dist/main" "$user_path/MultiTest"
        echo "[INFO] Moved and renamed executable to: $user_path/MultiTest"
    else
        echo "[ERROR] Compiled main not found."
    fi
else
    echo "========================"
    echo "[ERROR] PyInstaller build failed. Check the above output for details."
    echo "========================"
fi

read -p "Press any key ..."
