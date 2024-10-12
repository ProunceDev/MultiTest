import os, pywinstyles, customtkinter as ctk
from functools import partial
from settings import SettingsManager
from instance_manager import InstanceManager, CreateInstanceWindow, DeleteConfirmationWindow, InstanceConfigManager
from PIL import Image
from datetime import datetime


current_dir = os.path.dirname(os.path.abspath(__file__))
# Initialize the main app window
class MinetestLauncherApp(ctk.CTk):
	def __init__(self):
		super().__init__()

		# Initialize settings and instances
		self.settings = SettingsManager(os.path.join(current_dir, "config/settings.json"))
		self.instances = InstanceManager(os.path.join(current_dir, "instances"))
		self.instance_cards = {}
		self.exit_code = 0
		# Initialize window
		self.geometry("800x600")
		theme = self.settings.get_setting("theme", "Night-Dark")
		scale = self.settings.get_setting("scale", "100%")
		self.new_scaling_float = int(scale.replace("%", "")) / 100
		color, light = theme.split("-")
		self.color = color.lower().replace('blue', 'dark-blue').replace('purple', os.path.join(current_dir, "assets/purple.json")).replace('night', os.path.join(current_dir, "assets/night.json"))
		self.light = light
		ctk.set_appearance_mode(self.light)
		ctk.set_default_color_theme(self.color)
		ctk.set_widget_scaling(self.new_scaling_float)
		self.title("MultiTest Launcher")
		self.bind("<Configure>", self.on_resize)
		# Start setting up GUI
		self.main_frame = ctk.CTkFrame(master=self, corner_radius=0)
		self.main_frame.pack(padx=0, pady=0, expand=True, fill="both")
		self.tabview = ctk.CTkTabview(master=self.main_frame, corner_radius=10)
		self.tabview.pack(padx=10, pady=10, expand=True, fill="both")

		self.tabview.add("Manage Instances")
		self.manage_instances = ctk.CTkScrollableFrame(self.tabview.tab("Manage Instances"))
		self.manage_instances.pack(padx=5, pady=5, expand=True, fill="both")

		self.tabview.add("Launcher Settings")
		self.launcher_settings = ctk.CTkScrollableFrame(self.tabview.tab("Launcher Settings"))
		self.launcher_settings.pack(padx=5, pady=5, expand=True, fill="both")
		ctk.CTkLabel(self.launcher_settings, text="Theme:", anchor="w").grid(row=0, column=0, padx=10, pady=(10, 10))
		self.theme = ctk.StringVar(self)
		self.theme.set(self.settings.get_setting("theme", "Night-Dark"))
		ctk.CTkOptionMenu(self.launcher_settings, variable=self.theme, values=["Blue-Light", "Green-Light", "Purple-Light", "Night-Light", "Blue-Dark", "Green-Dark", "Purple-Dark", "Night-Dark"], command=self.change_appearance_mode_event).grid(row=0, column=1, padx=10, pady=(10, 10))
		ctk.CTkLabel(self.launcher_settings, text="Scale:", anchor="w").grid(row=1, column=0, padx=10, pady=(10, 10))
		self.scale = ctk.StringVar(self)
		self.scale.set(self.settings.get_setting("scale", "100%"))
		ctk.CTkOptionMenu(self.launcher_settings, variable=self.scale, values=["60%", "80%", "100%", "120%", "140%"], command=self.change_scaling_event).grid(row=1, column=1, padx=10, pady=(10, 10))
		self.initialized = True
		
		pywinstyles.apply_style(self, "dark")
		self.after(100, lambda: pywinstyles.apply_style(self, "dark"))

	def change_appearance_mode_event(self, new_appearance_mode: str):
		self.settings.set_setting('theme', new_appearance_mode)
		self.exit_code = 1
		self.destroy()

	
	def change_scaling_event(self, new_scaling: str):
		self.settings.set_setting('scale', new_scaling)
		self.new_scaling_float = int(new_scaling.replace("%", "")) / 100
		ctk.set_widget_scaling(self.new_scaling_float)

	def on_resize(self, event):
		new_width = event.width
		new_height = event.height
		self.settings.set_setting("window_geometry", f"{new_width}x{new_height}")
		self.load_instances()
		
	def load_instances(self):
		if not hasattr(self, 'initialized'):
			return
		instances = self.instances.list_instances()
		available_width = self.manage_instances.winfo_width()
		instance_width = 160 * self.new_scaling_float
		max_columns = max(1, available_width // instance_width)
		
		row, col = 0, 0
		for instance in instances:
			self.create_or_update_instance_frame(instance, row, col)
			col += 1
			if col >= max_columns:
				col = 0
				row += 1

		# Add the "Add instance" button at the end
		self.create_or_update_new_instance_button(row, col)
	
	def create_or_update_instance_frame(self, instance_name, row, col):
		if instance_name not in self.instance_cards:
			# Create frame for each instance
			frame = ctk.CTkFrame(self.manage_instances, fg_color=self.adjust_colors(), corner_radius=10)
			frame.grid(row=row, column=col, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
			
			# Instance image
			logo_path = os.path.join(self.instances.get_instance_install_path(self.instances.get_instance_path(instance_name)), "textures", "base", "pack",  "logo.png")
			try:
				img = ctk.CTkImage(dark_image=Image.open(logo_path), size=(75, 75))
			except:
				img = ctk.CTkImage(dark_image=Image.open(os.path.join(current_dir, "assets/default_logo.png")), size=(75, 75))
			label = ctk.CTkLabel(frame, image=img, text="")
			label.pack(pady=5)

			# Instance name with smaller font
			settings = self.instances.get_instance_settings(self.instances.get_instance_path(instance_name))
			name_label = ctk.CTkLabel(frame, text=settings.get("display_name", instance_name), font=("Arial", 14))
			name_label.pack(pady=5)

			# Buttons: Edit, Launch, Delete
			button_frame = ctk.CTkFrame(frame, corner_radius=5, fg_color="transparent")
			button_frame.pack(pady=5)

			edit_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_dir, "assets/edit_icon.png")), size=(20, 20))
			launch_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_dir, "assets/launch_icon.png")), size=(20, 20))
			delete_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_dir, "assets/delete_icon.png")), size=(20, 20))

			ctk.CTkButton(button_frame, image=edit_icon, text="", width=25, height=25, command=lambda: self.edit_instance(instance_name)).grid(row=0, column=0, padx=5)
			ctk.CTkButton(button_frame, image=launch_icon, text="", width=25, height=25, command=lambda: self.launch_instance(instance_name)).grid(row=0, column=1, padx=5)
			ctk.CTkButton(button_frame, image=delete_icon, text="", width=25, height=25, command=lambda: self.confirm_delete_instance(instance_name)).grid(row=0, column=2, padx=5)

			self.instance_cards[instance_name] = frame
		else:
			self.instance_cards[instance_name].grid(row=row, column=col, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

	def create_or_update_new_instance_button(self, row, col):
		if "new_instance" not in self.instance_cards:
			# Create a base frame for "new instance"
			frame = ctk.CTkFrame(self.manage_instances, fg_color=self.adjust_colors(), corner_radius=10)
			frame.grid(row=row, column=col, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

			# Add image and button for adding a new instance
			plus_icon = ctk.CTkImage(dark_image=Image.open(os.path.join(current_dir, "assets/plus_icon.png")), size=(75, 75))
			plus_label = ctk.CTkLabel(frame, image=plus_icon, text="")
			plus_label.pack(pady=5)

			button_frame = ctk.CTkFrame(frame, corner_radius=5, fg_color="transparent")
			button_frame.pack(pady=15, side="bottom")

			ctk.CTkButton(button_frame, text="Add instance", compound="top", command=self.create_new_instance).grid(row=0, column=0, columnspan=3, padx=5)

			self.instance_cards["new_instance"] = frame
		else:
			self.instance_cards["new_instance"].grid(row=row, column=col, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

	def adjust_colors(self):
		# Adjust colors for frames
		colors = self.manage_instances.cget('fg_color')
		return [f"gray{max(0, int(c.replace('gray', '')) - 4)}" if 'gray' in c else f"#{''.join(f'{max(0, int(c[i:i+2], 16) - 4):02x}' for i in (1, 3, 5))}" for c in colors]
	
	def edit_instance(self, instance_name):
		modal = InstanceConfigManager(self, instance_name)
		modal.grab_set()
		self.center_window(modal)
		modal.wait_window()

	def launch_instance(self, instance_name):
		self.instances.launch_instance(instance_name, self)

	def confirm_delete_instance(self, instance_name):
		path = self.instances.get_instance_path(instance_name)
		display_name = self.instances.get_instance_settings(path)["display_name"]
		confirmation_window = DeleteConfirmationWindow(self, display_name, lambda: self.delete_instance(path, instance_name))
		confirmation_window.grab_set()
		self.center_window(confirmation_window)
		confirmation_window.wait_window()

	def delete_instance(self, path, instance_name):
		self.instances.delete_instance(path)
		self.instances.load_instances()
		self.load_instances()
		self.instance_cards[instance_name].destroy()
	
	def center_window(self, window):
		# Get the dimensions of the parent window
		parent_width = self.winfo_width()
		parent_height = self.winfo_height()
		parent_x = self.winfo_x()
		parent_y = self.winfo_y()

		# Get the dimensions of the Toplevel window
		window_width, window_height = window.size.split("x")

		window_width = int(window_width) * self.new_scaling_float
		window_height = int(window_height) * self.new_scaling_float
		# Calculate the position for centering
		x = parent_x + (parent_width // 2) - (int(window_width) // 2)
		y = parent_y + (parent_height // 2) - (int(window_height) // 2)

		# Set the geometry of the Toplevel window
		window.geometry(f"{int(window_width)}x{int(window_height)}+{x}+{y}")

	def create_new_instance(self):
		modal = CreateInstanceWindow(self)
		modal.grab_set()
		self.center_window(modal)
		modal.wait_window()
		if modal.output:
			self.instances.create_instance(self, modal.output[0] + "_" + modal.output[1]["name"] + "_" + datetime.now().strftime("%H_%M_%S"), {"display_name": modal.output[0], "source_link": modal.output[1]["link"], "version_string": modal.output[1]["name"]})
			self.load_instances()

	def show(self):
		self.deiconify()

	def hide(self):
		self.withdraw()

# Main loop for the app
if __name__ == "__main__":
	while True:
		app = MinetestLauncherApp()
		app.mainloop()
		if app.exit_code == 0:
			exit()
