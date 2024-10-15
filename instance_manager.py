import os, configparser, urllib.request, zipfile, threading, shutil, subprocess, re, customtkinter as ctk
from tkinter import StringVar, messagebox

class CreateInstanceWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_dir):
        super().__init__(parent)
        self.geometry("400x400")
        self.size = ("400x400")
        self.title("New Instance - MultiTest")
        self.output = None
        self.current_dir = current_dir
        
        ctk.set_appearance_mode(parent.light)
        ctk.set_default_color_theme(parent.color)
        ctk.set_widget_scaling(parent.new_scaling_float)

        # Layout management
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0,1,2,3), weight=1)

        # Instance Name Field
        self.name_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.name_frame.grid(row=0, column=0, columnspan = 2, padx=0, pady=0, sticky="nsew")
        self.name_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, )
        self.name_frame.grid_rowconfigure(1, weight=1)
        self.name_label = ctk.CTkLabel(self.name_frame, text="Instance Name:")
        self.name_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.name_entry = ctk.CTkEntry(self.name_frame, width=100)
        self.name_entry.grid(row=0, column=1, columnspan = 2, padx=10, pady=10, sticky="nsew")

        # Versions Section
        self.versions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.versions_frame.grid(row=1, column=0, rowspan = 2, padx=0, pady=0, sticky="nsew")
        self.versions_frame.grid_columnconfigure(1, weight=1, )
        self.versions_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.versions_label = ctk.CTkLabel(self.versions_frame, text="Versions:")
        self.versions_label.grid(row=0, column=0, padx=20, pady=10, sticky="e")

        # Listbox for versions
        self.version_listbox = ctk.CTkScrollableFrame(self, width=200, height=150)
        self.version_listbox.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        # Filter checkboxes
        self.filter_official_var = StringVar(value="Official")
        self.filter_other_var = StringVar(value="")

        self.filter_frame = ctk.CTkFrame(self.versions_frame, fg_color="transparent")
        self.filter_frame.grid(row=3, column=0, padx=15, pady=0, sticky="e")

        
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filter")
        self.filter_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.filter_official = ctk.CTkCheckBox(self.filter_frame, text="Official", onvalue="Official", offvalue="", variable=self.filter_official_var, command=self.apply_filters)
        self.filter_official.grid(row=1, column=0, padx=5, pady=15, sticky="e")
        
        self.filter_other = ctk.CTkCheckBox(self.filter_frame, text="Other", onvalue="Other", offvalue="", variable=self.filter_other_var, command=self.apply_filters)
        self.filter_other.grid(row=2, column=0, padx=5, pady=15, sticky="e")

        # Buttons
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=4, column=0, columnspan = 2, padx=0, pady=0, sticky="nsew")
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1, )
        self.buttons_frame.grid_rowconfigure(1, weight=1)
        
        self.cancel_button = ctk.CTkButton(self.buttons_frame, text="Cancel", command=self.destroy)
        self.cancel_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.ok_button = ctk.CTkButton(self.buttons_frame, text="Create", command=self.create_instance)
        self.ok_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Load versions
        self.version_data = []
        
        # Linux compatability
        if os.name == 'nt':
            self.load_versions(os.path.join(current_dir, 'config/versions.txt'))

            self.after(201, lambda :self.iconbitmap(os.path.join(current_dir, "assets/icon.ico")))
        else:
            self.load_versions(os.path.join(current_dir, 'config/versions_linux.txt'))

    def load_versions(self, filepath):
        """Load versions from a file and display them."""
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                self.version_data = [
                    {"name": line.split(",")[0].strip(), 
                    "link": line.split(",")[1].strip(), 
                    "category": line.split(",")[2].strip()} 
                    for line in lines
                ]
            self.apply_filters()
        except FileNotFoundError:
            label = ctk.CTkLabel(self.version_listbox, text="No versions found.")
            label.pack(padx=5, pady=5, anchor="w")

    def apply_filters(self):
        """Filter the versions based on the selected categories."""
        for widget in self.version_listbox.winfo_children():
            widget.destroy()

        filtered_versions = [
            version for version in self.version_data 
            if (self.filter_official_var.get() == "Official" and version["category"] == "Official") or
            (self.filter_other_var.get() == "Other" and version["category"] == "Other")
        ]
        
        if filtered_versions:
            self.version_var = StringVar(value=filtered_versions[0]["name"])
            for version in filtered_versions:
                radio = ctk.CTkRadioButton(
                    self.version_listbox, text=version["name"], variable=self.version_var, value=version["name"]
                )
                radio.pack(padx=5, pady=5, anchor="w")
        else:
            label = ctk.CTkLabel(self.version_listbox, text="No versions found.")
            label.pack(padx=5, pady=5, anchor="w")

    def create_instance(self):
        """Create a new instance with the selected details."""
        instance_name = self.name_entry.get()
        if not instance_name:
            messagebox.showerror("Error", "Please enter an instance name.")
            return
        
        selected_version = self.version_var.get()
        for version in self.version_data:
            if version["name"] == selected_version:
                self.output = [instance_name, version]
        self.destroy()

class InstanceManager:
    def __init__(self, instances_folder, current_dir) -> None:
        """
        Initialize the InstanceManager with the folder where instances are stored.
        """
        self.instances_folder = instances_folder
        self.instances = {}
        self.current_dir = current_dir
        self.load_instances()

    def load_instances(self) -> None:
        """
        Loads all instances by scanning the instances folder. Updates the instances in memory.
        """
        self.instances.clear()
        for folder_name in os.listdir(self.instances_folder):
            folder_path = os.path.join(self.instances_folder, folder_name)
            if os.path.isdir(folder_path) and self.is_valid_instance(folder_path):
                instance_name = self.get_instance_name(folder_path)
                self.instances[instance_name] = folder_path

    def is_valid_instance(self, instance_path) -> bool:
        """
        Checks if a given folder is a valid instance by verifying the presence of instance.cfg.
        """
        return os.path.isfile(os.path.join(instance_path, "instance.cfg"))

    def get_instance_name(self, instance_path) -> str:
        """
        Retrieves the instance name from the instance.cfg file.
        """
        settings = self.get_instance_settings(instance_path)
        return settings.get("name", os.path.basename(instance_path))

    def get_instance_settings(self, instance_path) -> dict:
        """
        Returns the settings from the instance.cfg file as a dictionary.
        If the file does not exist, returns default settings.
        """
        config_path = os.path.join(instance_path, "instance.cfg")
        config = configparser.ConfigParser()

        if os.path.exists(config_path):
            config.read(config_path)
            return {key: value for key, value in config["DEFAULT"].items()}
        else:
            # Return default settings if instance.cfg does not exist
            return {"name": os.path.basename(instance_path)}

    def set_instance_settings(self, instance_path, settings) -> None:
        """
        Updates and saves the given settings to the instance.cfg file.
        """
        config = configparser.ConfigParser()
        config["DEFAULT"] = settings

        config_path = os.path.join(instance_path, "instance.cfg")
        with open(config_path, "w") as configfile:
            config.write(configfile)

    def get_instance_path(self, instance_name) -> str:
        """
        Returns the file path for a given instance name.
        """
        return self.instances.get(instance_name)
    
    def get_instance_install_path(self, instance_path):
        # Iterate over the files and folders in the instance directory
        for entry in os.listdir(instance_path):
            entry_path = os.path.join(instance_path, entry)
            
            # Check if it's a directory (folder)
            if os.path.isdir(entry_path) and entry != 'instance.cfg':
                return entry_path

        return None  # If no folder is found
    
    def launch_instance(self, instance_name, current_dir):
        instance_path = self.get_instance_path(instance_name)
        settings = self.get_instance_settings(instance_path)
        install_path = self.get_instance_install_path(instance_path)

        # Ensure the global config is created for Minetest if required
        if settings.get("global_config", "1") == "1":
            with open(os.path.join(current_dir, "config", "global_minetest.conf"), 'a') as file:
                pass

        # Prepare the command to launch Minetest
        config_path = os.path.join(current_dir, "config", "global_minetest.conf")
        minetest_executable = os.path.join(install_path, "bin", "minetest")

        if os.name == 'nt':
            # Windows
            command = f'"{minetest_executable}".exe --config "{config_path}"' if settings.get("global_config", "1") == "1" else f'"{minetest_executable}"'
            subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Linux
            command = f'"{minetest_executable}" --config "{config_path}"' if settings.get("global_config", "1") == "1" else f'"{minetest_executable}"'
            subprocess.Popen(command, shell=True)  # No need for creationflags on Linux

    def list_instances(self) -> dict:
        """
        Returns a dict of all instances.

        self.instances used to be a list but im too lazy to remove this now
        """
        return self.instances

    def create_instance(self, parent, instance_name, settings) -> str:
        """
        Creates a new instance folder, initializes it with settings, and returns the folder path.
        """
        instance_path = os.path.join(self.instances_folder, instance_name)

        if not os.path.exists(instance_path):
            os.makedirs(instance_path)  # Create the folder
            self.set_instance_settings(instance_path, settings)  # Initialize with settings
            url = settings["source_link"]
            version = settings["version_string"]
            modal = DownloadModal(parent, url, version, instance_path)
            modal.grab_set()  # Make the new window modal
            parent.center_window(modal)
            modal.wait_window()
            self.load_instances()  # Reload to update the internal list
            return instance_path
        else:
            raise FileExistsError(f"Instance '{instance_name}' already exists.")
        
    def parse_conf_file(self, file_path, title_key="title", author_key="author"):
        """
        Parses a config file (either texture_pack.conf or mod.conf) and returns the title and author.
        The keys for title and author can be customized (for example, mod.conf uses "name" instead of "title").
        """
        title = None
        author = None
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith(title_key):
                        title = line.split('=')[1].strip()
                    elif line.startswith(author_key):
                        author = line.split('=')[1].strip()
        except:
            pass  # If the file doesn't exist, we return None values
        return title, author
    
    
    def get_texture_packs_info(self, instance_name):
        """
        Reads only the immediate subfolders in base_dir, checks for the presence of
        texture_pack.conf, and returns a dictionary where the keys are the
        folder names and the values are (title, author) tuples.
        """
        texture_packs = {}
        base_dir = os.path.join(self.get_instance_install_path(self.get_instance_path(instance_name)), "textures")
        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)

            if os.path.isdir(folder_path):
                conf_file_path = os.path.join(folder_path, 'texture_pack.conf')

                if os.path.isfile(conf_file_path):
                    # Parse the texture_pack.conf if it exists
                    title, author = self.parse_conf_file(conf_file_path)
                    texture_packs[folder] = {"title": title, "author": author}
                else:
                    # If no texture_pack.conf, add folder name with author as None
                    texture_packs[folder] = {"title": folder, "author": "N/A"}

        return texture_packs

    def get_mods_info(self, instance_name):
        """
        Reads only the immediate subfolders in mods_dir, checks for the presence of
        mod.conf, and returns a dictionary where the keys are the
        folder names and the values are (title, author) tuples.
        """
        mods_info = {}
        mods_dir = os.path.join(self.get_instance_install_path(self.get_instance_path(instance_name)), "mods")
        for folder in os.listdir(mods_dir):
            folder_path = os.path.join(mods_dir, folder)

            if os.path.isdir(folder_path):
                conf_file_path = os.path.join(folder_path, 'mod.conf')

                if os.path.isfile(conf_file_path):
                    # Parse the mod.conf if it exists
                    title, author = self.parse_conf_file(conf_file_path, title_key="name", author_key="author")
                    mods_info[folder] = {"title": title, "author": author}
                else:
                    # If no mod.conf, add folder name with author as None
                    mods_info[folder] = {"title": folder, "author": None}

        return mods_info
        
    def delete_instance(self, instance_path) -> bool:
        if self.is_valid_instance(instance_path):
            shutil.rmtree(instance_path)
            return True
        else:
            print("Warning: attempted to delete invalid instance")
            return False

class DownloadModal(ctk.CTkToplevel):
    def __init__(self, parent, url, version, destination_folder):
        super().__init__(parent)
        self.url = url
        self.version = version
        self.destination_folder = destination_folder
        self.zip_file_path = f"{version}.zip"
        self.parent = parent
        if os.name == 'nt':
            self.after(201, lambda :self.iconbitmap(os.path.join(parent.instances.current_dir, "assets/icon.ico")))
        self.geometry("400x100")
        self.title(f"Installing {self.version}")
        self.size = "400x100"
        self.resizable(False, False)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text=f"Installing {self.version}: Preparing...", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        # Button
        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=self.cancel_download)
        self.cancel_button.pack(pady=10)

        # Start the download in a separate thread
        threading.Thread(target=self.start_download, daemon=True).start()

    def start_download(self):
        try:
            self.status_label.configure(text=f"Installing {self.version}: Downloading")
            urllib.request.urlretrieve(self.url, self.zip_file_path, self.update_progress)

            self.status_label.configure(text=f"Installing {self.version}: Extracting")
            self.extract_zip()
            self.status_label.configure(text=f"Installed {self.version} successfully.")

            if os.name == "posix":
                self.compile_mt()  # Call the compile method for Linux
                self.status_label.configure(text=f"You may have to build manually.")
            
            self.cancel_button.configure(text="Close")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")

    def compile_mt(self):
        try:
            # Define the install and compile commands combined into one string
            install_command = (
                'sudo apt install -y g++ make libc6-dev cmake libpng-dev libjpeg-dev '
                'libxi-dev libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev '
                'libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev '
                'libgmp-dev libjsoncpp-dev libzstd-dev libluajit-5.1-dev gettext '
                'libbz2-dev && '
                f'cd "{self.parent.instances.get_instance_install_path(self.destination_folder)}" && '
                'cmake . -DRUN_IN_PLACE=TRUE && make -j$(nproc) && read -p "Press any key ..."'
            )

            # Open a new gnome-terminal and run the combined command
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', install_command])

            # Update status label to indicate the command is being executed
            self.status_label.configure(text=f"Installing {self.version}: Running installation in new terminal")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")


    def update_progress(self, block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            # Show download progress in MB on the status label
            downloaded_mb = downloaded / (1024 * 1024)
            total_size_mb = total_size / (1024 * 1024)
            self.status_label.configure(
                text=f"Installing {self.version}: Downloading {downloaded_mb:.2f} MB / {total_size_mb:.2f} MB"
            )

    def extract_zip(self):
        with zipfile.ZipFile(self.zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.destination_folder)
        os.remove(self.zip_file_path)

    def cancel_download(self):
        self.destroy()

class DeleteConfirmationWindow(ctk.CTkToplevel):
    def __init__(self, parent, instance_name, on_confirm):
        super().__init__(parent)
        self.title("Confirm Delete")
        self.geometry("300x150")
        self.size = "300x150"
        self.resizable(False, False)
        self.instance_name = instance_name
        self.on_confirm = on_confirm

        # Set layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Label asking for confirmation
        self.label = ctk.CTkLabel(self, text=f"Are you sure you want to delete \n'{instance_name.strip()}'?")
        self.label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Confirmation buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.yes_button = ctk.CTkButton(self.button_frame, text="Yes", command=self.confirm_delete)
        self.yes_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.no_button = ctk.CTkButton(self.button_frame, text="No", command=self.cancel)
        self.no_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        # Linux Compatability
        if os.name == 'nt':
            self.after(201, lambda :self.iconbitmap(os.path.join(parent.instances.current_dir, "assets/icon.ico")))

    def confirm_delete(self):
        """Calls the provided on_confirm callback and closes the window."""
        self.on_confirm()
        self.destroy()

    def cancel(self):
        """Closes the confirmation window without doing anything."""
        self.destroy()

class InstanceConfigManager(ctk.CTkToplevel):
    def __init__(self, parent, instance_name):
        super().__init__(parent)

        self.title("Instance Manager")
        self.geometry("400x500")
        self.size = ("400x500")
        self.resizable(False, False)
        
        self.parent = parent
        # Dictionary to store selected mods
        self.instance_name = instance_name
        self.selected_mods = {}
        self.selected_textures = {}
        # Add the Tabview for categories
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.mods_tab = self.tabview.add("Mods")
        self.texture_packs_tab = self.tabview.add("Texture Packs")
        self.settings_tab = self.tabview.add("Settings")

        # Initialize mod loader and settings panels
        self.init_mods(self.mods_tab)
        self.init_texture_packs(self.texture_packs_tab)
        self.init_settings(self.settings_tab)

        # Linux Compatability
        if os.name == "nt":
            self.after(201, lambda :self.iconbitmap(os.path.join(parent.instances.current_dir, "assets/icon.ico")))


    def init_mods(self, tab):
        # Mods UI
        mods_label = ctk.CTkLabel(tab, text="Mods", font=("Arial", 20))
        mods_label.pack(pady=10)
        colors = self.cget('fg_color')
        color =  [f"gray{max(0, int(c.replace('gray', '')) - 4)}" if 'gray' in c else f"#{''.join(f'{max(0, int(c[i:i+2], 16) - 4):02x}' for i in (1, 3, 5))}" for c in colors]
    
        # Listbox-like implementation using ScrollableFrame for mods list
        self.mod_frame = ctk.CTkScrollableFrame(tab, width=600, height=300, fg_color=color)
        self.mod_frame.pack(pady=10, padx=10)


        # Populate mod list with checkboxes for selection
        mods_info = self.parent.instances.get_mods_info(self.instance_name)
        for folder_name, info in mods_info.items():
            title = info["title"]
            author = info["author"]
            self.add_mod_to_frame(title, author)  # Use title and author

        # Control buttons (Add, Remove, Enable, Disable)
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=10)

        open_folder = ctk.CTkButton(button_frame, text="Open Folder", command=lambda: self.open_folder(os.path.join(self.parent.instances.get_instance_install_path(self.parent.instances.get_instance_path(self.instance_name)), "mods")))

        open_folder.grid(row=0, column=0, padx=5)

        
    def init_texture_packs(self, tab):
        # Mods UI
        textures_label = ctk.CTkLabel(tab, text="Texture Packs", font=("Arial", 20))
        textures_label.pack(pady=10)
        colors = self.cget('fg_color')
        color =  [f"gray{max(0, int(c.replace('gray', '')) - 4)}" if 'gray' in c else f"#{''.join(f'{max(0, int(c[i:i+2], 16) - 4):02x}' for i in (1, 3, 5))}" for c in colors]
    
        # Listbox-like implementation using ScrollableFrame for mods list
        self.texture_frame = ctk.CTkScrollableFrame(tab, width=600, height=300, fg_color=color)
        self.texture_frame.pack(pady=10, padx=10)

        # Dummy mods data
        texture_packs_info = self.parent.instances.get_texture_packs_info(self.instance_name)
        for folder_name, info in texture_packs_info.items():
            title = info["title"]
            author = info["author"]
            self.add_texture_pack_to_frame(title, author)  # Use title and author

        # Control buttons (Add, Remove, Enable, Disable)
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=10)

        open_folder = ctk.CTkButton(button_frame, text="Open Folder", command=lambda: self.open_folder(os.path.join(self.parent.instances.get_instance_install_path(self.parent.instances.get_instance_path(self.instance_name)), "textures")))
        open_folder.grid(row=0, column=2, padx=5)

    def open_folder(self, folder_path):
        if os.name == "nt":
            os.startfile(folder_path)
        else:
            subprocess.Popen(["xdg-open", folder_path])

    def init_settings(self, tab):
        # Settings UI
        instance_path = self.parent.instances.get_instance_path(self.instance_name)
        settings = self.parent.instances.get_instance_settings(instance_path)
        settings_label = ctk.CTkLabel(tab, text="Settings", font=("Arial", 20))
        settings_label.pack(pady=10)

        # Create a frame for the global config setting
        config_frame = ctk.CTkFrame(tab)
        config_frame.pack(pady=10, padx=10)

        # Add the "Use Global Config" check slider (CTkSwitch)
        self.use_global_config_switch = ctk.CTkSwitch(config_frame, text="Use Global Config", command=self.toggle_global_config)
        self.use_global_config_switch.grid(row=0, column=0, padx=10)


        if settings.get("global_config", "1") == "1":
            self.use_global_config_switch.select()
        else:
            self.use_global_config_switch.deselect()

    def toggle_global_config(self):
        """
        Callback function that is triggered when the 'Use Global Config' switch is toggled.
        """
        instance_path = self.parent.instances.get_instance_path(self.instance_name)
        settings = self.parent.instances.get_instance_settings(instance_path)
        settings["global_config"] = self.use_global_config_switch.get()
        self.parent.instances.set_instance_settings(instance_path, settings)


    # Helper function to add mods to the scrollable frame with checkboxes
    def add_mod_to_frame(self, name, author):
        mod_row_frame = ctk.CTkFrame(self.mod_frame)
        mod_row_frame.pack(fill="x", pady=5, padx = 5)

        # Checkbox to allow selecting mods
        selected_var = ctk.BooleanVar()
        mod_checkbox = ctk.CTkLabel(mod_row_frame, text=f"{name}")
        mod_checkbox.pack(side="left", pady=5, padx = 5)

        mod_author = ctk.CTkLabel(mod_row_frame, text=f"Author: {author}")
        mod_author.pack(side="right", pady=5, padx = 5)
        # Store the checkbox's variable in self.selected_mods dict
        self.selected_mods[name] = selected_var

    def add_texture_pack_to_frame(self, name, author):
        texture_row_frame = ctk.CTkFrame(self.texture_frame)
        texture_row_frame.pack(fill="x", pady=5, padx = 5)

        # Checkbox to allow selecting mods
        selected_var = ctk.BooleanVar()
        texture_mod_checkbox = ctk.CTkLabel(texture_row_frame, text=f"{name}")
        texture_mod_checkbox.pack(side="left", pady=5, padx = 5)

        texture_author = ctk.CTkLabel(texture_row_frame, text=f"Author: {author}")
        texture_author.pack(side="right", pady=5, padx = 5)
        # Store the checkbox's variable in self.selected_mods dict
        self.selected_textures[name] = selected_var