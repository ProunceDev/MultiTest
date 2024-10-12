# **MultiTest**  
*A comprehensive Minetest launcher with global configs, instance management, and enhanced mod support.*

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

 *Other OSes*

 - MultiTest currently only supports windows, but if you are willing to work with me we could bring MultiTest to your platform.

## **TODO:**

- Refactor `settings.py` to use the `configparser` library for configuration management.
- Split `instance_manager.py` into multiple smaller files, with each file handling a specific class.
- Add ContentDB support to allow adding mods directly from the mod configuration menu.
- Find someone on linux willing to help out with adding support for basic Ubuntu and maybe a couple other OSes.