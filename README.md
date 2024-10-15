# **MultiTest**  
*A comprehensive Minetest launcher with global configs, instance management, and enhanced mod support.*

## **Preview:**

![Icon](https://github.com/ProunceDev/MultiTest/blob/main/assets/icon.png?raw=true)
![Main screen](https://github.com/ProunceDev/MultiTest/blob/main/doc/preview.png?raw=true)
![Create instance](https://github.com/ProunceDev/MultiTest/blob/main/doc/create_instance.png?raw=true)
![Manage instance](https://github.com/ProunceDev/MultiTest/blob/main/doc/manage_instance.png?raw=true)

## **Features:**

- **Global Configurations**: Manage settings across multiple instances from a single global configuration file.
- **Instance Management**: Easily create, modify, and manage multiple Minetest instances.
- **User-Friendly Interface**: Clean and intuitive UI for managing all aspects of your Minetest experience.

## **Use:**
 *Windows*

 - Download this repo either using `git clone https://github.com/ProunceDev/MultiTest.git` or the green `Code` button on the website.
 - Install [Python](https://www.python.org/downloads/).
 - [Open the downloaded folder in command prompt](https://www.wikihow.com/Open-a-Folder-in-Cmd).
 - First run `pip install -r requirements.txt`.
 - Then run `python main.py`.
 - Enjoy!

 *Ubuntu/Debian*

 - Download this repo either using `git clone https://github.com/ProunceDev/MultiTest.git` or the green `Code` button on the website.
 - Install [Python](https://www.python.org/downloads/).
 - Open the downloaded folder in your terminal.
 - First run `pip install -r requirements.txt`.
 - Then run `python main.py`.
 - Enjoy!

 *Other OSes*

 - MultiTest currently only supports Windows and Ubuntu/Debian, but if you are willing to work with me, we could bring MultiTest to your platform.

## **Compile:**

If you want to compile MultiTest into a standalone executable, follow these steps:

1. **Install Dependencies**:
    - Ensure you have [Python](https://www.python.org/downloads/) installed.
    - Open a command prompt in the **MultiTest** folder and run the following command to install all the necessary libraries: `pip install -r requirements.txt`

2. **Compile Using `build.bat`**:
    - In the **MultiTest** folder, double-click or run the `build.bat` script in the command prompt.
    - The script will:
        - Create a `build` folder to store temporary files.
        - Compile the `main.py` file into an executable using `PyInstaller`.
        - Move the final executable (`MultiTest.exe`) back to the main **MultiTest** folder.
    - After compilation, the `MultiTest.exe` will be ready for use in the main folder.

3. **Compile Using `build.sh` Ubuntu/Debian**:
    - In the **MultiTest** folder, double-click or run the `build.sh` script in the terminal.
    - The script will:
        - Create a `build` folder to store temporary files.
        - Compile the `main.py` file into an executable using `PyInstaller`.
        - Move the final executable (`MultiTest`) back to the main **MultiTest** folder.
    - After compilation, the `MultiTest` will be ready for use in the main folder.

3. **Run the Compiled Executable**:
    - Once the compilation is complete, you can simply run `MultiTest.exe` ( 'MultiTest' on Ubuntu/Debian ) without needing to install Python or any dependencies.

## **TODO:**

- Refactor `settings.py` to use the `configparser` library for configuration management.
- Split `instance_manager.py` into multiple smaller files, with each file handling a specific class.
- Add ContentDB support to allow adding mods directly from the mod configuration menu.
