import threading
import time
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import font
import json
import asyncio
import websockets
import os
from math import sqrt, atan, tan, radians

def int_or_none(value):
    try:
        return int(value)
    except ValueError:
        return 0

def float_or_none(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

class CameraUpdaterWidget(tk.Frame):
    def __init__(self, parent, text_color, frame_color, message_sender=None, terminal_adder=None,  *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_file = "camera-settings.json"
        self.message_sender = message_sender
        self.terminal_adder = terminal_adder

        # Set the background color to match the rest of the app


        self.configure(bg=frame_color)

        # Create input fields for camera values
        self.create_input_field("Height:", "height", frame_color, text_color)
        self.create_input_field("Horizontal Resolution:", "horizontal_resolution_pixels", frame_color, text_color)
        self.create_input_field("Vertical Resolution:", "vertical_resolution_pixels", frame_color, text_color)
        self.create_input_field("Processing Scale:", "processing_scale", frame_color, text_color)
        self.create_input_field("Tilt Angle (radians):", "tilt_angle_radians", frame_color, text_color)
        self.create_input_field("Horizontal FOV (radians):", "horizontal_field_of_view_radians", frame_color, text_color)
        self.create_input_field("Vertical FOV (radians):", "vertical_field_of_view_radians", frame_color, text_color)

        # Add a separator
        separator = tk.Frame(self, width=2, bg='black')
        separator.pack(fill='x', pady=10)

        # Create input fields for aspect ratio and diagonal FOV
        self.create_input_field("Aspect Ratio (Horizontal):", "aspect_ratio_horizontal", frame_color, text_color)
        self.create_input_field("Aspect Ratio (Vertical):", "aspect_ratio_vertical", frame_color, text_color)
        self.create_input_field("Diagonal FOV (degrees):", "diagonal_fov", frame_color, text_color)

        separator = tk.Frame(self, width=2, bg='black')
        separator.pack(fill='x', pady=10)

        self.create_input_field("Additional Flags:", "additional_flags", frame_color, text_color)

        buttons_frame = tk.Frame(self, bg=frame_color)
        buttons_frame.pack(fill=tk.X, pady=10)
        # Add a button to send the values
        self.send_button = ttk.Button(buttons_frame, text="Send Values", command=self.send_values, style="Dark.TButton")
        self.send_button.pack(pady=10, padx=10, side=tk.LEFT, fill=tk.X, expand=True)

        self.info = ttk.Button(buttons_frame, text="Get Info", command=self.get_info, style="Dark.TButton")
        self.info.pack(pady=10, padx=10, side=tk.LEFT, fill=tk.X, expand=True)

        self.hw = ttk.Button(buttons_frame, text="Get Hardware Info", command=self.get_hardware, style="Dark.TButton")
        self.hw.pack(pady=10, padx=10, side=tk.LEFT, fill=tk.X, expand=True)

        # Load parameters from file
        self.load_parameters()

    def get_info(self):
        message = "info"
        self.send_message(message)

    def get_hardware(self):
        message = "info -h=True"
        self.send_message(message)

    def create_input_field(self, label_text, var_name, bg_color, fg_color):
        frame = tk.Frame(self)
        frame.pack(pady=5, padx=10, fill=tk.X)
        frame.configure(bg=bg_color)

        label = ttk.Label(frame, text=label_text, background=bg_color, foreground=fg_color)
        label.pack(side=tk.LEFT, padx=5)

        entry = ttk.Entry(frame, style="Dark.TEntry")
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        setattr(self, var_name, entry)

    def get_values(self):
        try:
            dict = {}
            var_names = [["height", self.height, float],
                         ["horizontal_resolution_pixels", self.horizontal_resolution_pixels, int],
                         ["vertical_resolution_pixels", self.vertical_resolution_pixels, int],
                         ["tilt_angle_radians", self.tilt_angle_radians, float],
                         ["horizontal_field_of_view_radians", self.horizontal_field_of_view_radians, float],
                         ["vertical_field_of_view_radians", self.vertical_field_of_view_radians, float],
                         ["aspect_ratio_horizontal", self.aspect_ratio_horizontal, float],
                         ["aspect_ratio_vertical", self.aspect_ratio_vertical, float],
                         ["diagonal_fov", self.diagonal_fov, float],
                         ["processing_scale", self.processing_scale, int],
                         ["additional_flags", self.additional_flags, str]]

            for var_name, element, type in var_names:
                try:
                    dict[var_name] = type(element.get())
                except ValueError:
                    pass
            return dict

        except ValueError as e:
            self.terminal_adder(f"Error: {e}\n")
        except KeyError as e:
            self.terminal_adder(tk.END, f"Error: {e}\n")

    def set_values(self, values):
        self.height.insert(0, values.get("height", ""))
        self.horizontal_resolution_pixels.insert(0, values.get("horizontal_resolution_pixels", ""))
        self.vertical_resolution_pixels.insert(0, values.get("vertical_resolution_pixels", ""))
        self.tilt_angle_radians.insert(0, values.get("tilt_angle_radians", ""))
        self.horizontal_field_of_view_radians.insert(0, values.get("horizontal_field_of_view_radians", ""))
        self.vertical_field_of_view_radians.insert(0, values.get("vertical_field_of_view_radians", ""))
        self.aspect_ratio_horizontal.insert(0, values.get("aspect_ratio_horizontal", ""))
        self.aspect_ratio_vertical.insert(0, values.get("aspect_ratio_vertical", ""))
        self.diagonal_fov.insert(0, values.get("diagonal_fov", ""))
        self.additional_flags.insert(0, values.get("additional_flags", "")[1:-1])
        self.processing_scale.insert(0, values.get("processing_scale", ""))

    def save_parameters(self):
        values = self.get_values()
        with open(self.config_file, 'w') as file:
            json.dump(values, file, indent=4)

    def load_parameters(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                values = json.load(file)
                self.set_values(values)

    def calculate_fov(self, aspect_ratio_horizontal, aspect_ratio_vertical, diagonal_fov):
        Da = sqrt(aspect_ratio_horizontal**2 + aspect_ratio_vertical**2)
        Df = radians(diagonal_fov)
        Hf = atan(tan(Df/2) * (aspect_ratio_horizontal/Da)) * 2
        Vf = atan(tan(Df/2) * (aspect_ratio_vertical/Da)) * 2
        return Hf, Vf

    def send_values(self):
        values = self.get_values()
        try:
            Hf, Vf = self.calculate_fov(values["aspect_ratio_horizontal"], values["aspect_ratio_vertical"], values["diagonal_fov"])
            values["horizontal_field_of_view_radians"] = Hf
            values["vertical_field_of_view_radians"] = Vf
            self.horizontal_field_of_view_radians.delete(0, tk.END)
            self.horizontal_field_of_view_radians.insert(0, str(Hf))
            self.vertical_field_of_view_radians.delete(0, tk.END)
            self.vertical_field_of_view_radians.insert(0, str(Vf))
        except:
            pass

        message = "scp -values=" + json.dumps(values)
        self.save_parameters()
        try:
            self.send_message(message)
        except Exception as e:
            self.terminal_adder(f"Error when sending message: {e}\n")

    def send_message(self, message):
        while not self.message_sender(message):
            time.sleep(0.1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.save_image = False
        self.current_pil_image = None
        self.command = None
        self.active_color = 0
        self.title("Image Viewer")
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.raspberry_pi_ip = "10.42.0.118"
        self.port = 50000
        self.mode = "apriltag_image"

        dark_background_color = "#999999"
        light_text_color = "#CCCCCC"
        dark_frame_color = "#444444"
        slider_trough_color = "#555555"
        fps_label_color = "#111111"

        # Create main frames for layout
        self.left_panel = CameraUpdaterWidget(self, message_sender=self.change_command, terminal_adder=self.insert_text,
                                              text_color=light_text_color, frame_color=dark_frame_color, width=300)
        self.frame_left = tk.Frame(self)
        self.frame_right = tk.Frame(self, width=150)
        self.frame_separator = tk.Frame(self, width=2, bg='black')  # Aesthetic vertical bar
        self.left_frame_separator = tk.Frame(self, width=2, bg='black')  # Aesthetic horizontal bar

        # Configure the grid layout
        self.grid_columnconfigure(0, weight=2)  # Left frame has less weight, shrinks first
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=0)
        self.grid_columnconfigure(4, weight=1)  # Right frame has less weight, shrinks first


        # Place the frames using grid
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_frame_separator.grid(row=0, column=1, sticky="ew")
        self.frame_left.grid(row=0, column=2, sticky="nsew")
        self.frame_separator.grid(row=0, column=3, sticky="ew")
        self.frame_right.grid(row=0, column=4, sticky="nsew")

        # Make the main window's row 0 expandable
        self.grid_rowconfigure(0, weight=1)

        # Further configuration for the right frame to ensure it behaves as desired

        #self.frame_right.grid_propagate(False)  # Prevents the frame from shrinking beyond its widgets' sizes

        # Image and FPS label in the left frame
        self.image_label = tk.Label(self.frame_left)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Adjustments for the FPS label to overlay on the image
        self.fps_label = tk.Label(self.frame_left, text="FPS: 0", bg='black', fg='white', font=("Helvetica", 12))
        # This will place the FPS label at the bottom-right corner of the left frame
        self.fps_label.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor="se")

        # Create a container frame for the buttons inside the right frame
        buttons_frame = tk.Frame(self.frame_right)
        buttons_frame.pack(side=tk.TOP, fill=tk.X)  # Adjust padding as needed
        right_frame_sep = tk.Frame(self.frame_right, width=2, bg='black')
        right_frame_sep.pack()

        ip_port_frame = tk.Frame(self.frame_right)
        ip_port_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        ip_label = tk.Label(ip_port_frame, text="IP Address:")
        ip_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.ip_entry = ttk.Entry(ip_port_frame)
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.ip_entry.insert(0, self.raspberry_pi_ip)

        port_label = tk.Label(ip_port_frame, text="Port:")
        port_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.port_entry = ttk.Entry(ip_port_frame)
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.port_entry.insert(0, str(self.port))

        self.update_ip_button = ttk.Button(ip_port_frame, text="Update IP and Port", command=self.update_ip)
        self.update_ip_button.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        color_button_frame = tk.Frame(self.frame_right)
        color_button_frame.pack(side=tk.TOP, fill=tk.X)

        self.mode_var = tk.StringVar()
        self.mode_combobox = ttk.Combobox(color_button_frame, textvariable=self.mode_var)
        self.mode_combobox['values'] = ['AprilTag', 'Processed', 'Raw']
        self.mode_combobox.current(0)  # Default to AprilTag mode
        self.mode_var = tk.StringVar()
        self.mode_combobox = ttk.Combobox(color_button_frame, textvariable=self.mode_var)
        self.mode_combobox['values'] = ['AprilTag', 'Processed', 'Raw', 'Headless Piece Location',
                                        "Headless AprilTag Detection"]
        self.mode_combobox.current(0)  # Default to AprilTag mode
        self.mode_combobox.pack(side=tk.BOTTOM, pady=5, padx=5, fill=tk.X, expand=True)
        self.mode_combobox.bind("<<ComboboxSelected>>", self.on_mode_select)

        # Initialize and pack the Load Parameters button inside the buttons frame
        self.load_params_button = ttk.Button(color_button_frame, text="Load", command=self.load_parameters)
        self.load_params_button.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5, padx=5)  # Adjust padding as needed

        # Initialize and pack the Save Parameters button next to the Load Parameters button
        self.save_params_button = ttk.Button(color_button_frame, text="Save", command=self.save_parameters)
        self.save_params_button.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5, padx=5)

        # Buttons for adding and deleting colors
        self.add_color_button = ttk.Button(color_button_frame, text="Add Color", command=self.add_color)
        self.add_color_button.pack(side=tk.LEFT, pady=5, padx=5, fill=tk.X, expand=True)

        self.delete_color_button = ttk.Button(color_button_frame, text="Delete Color", command=self.delete_color)
        self.delete_color_button.pack(side=tk.LEFT, pady=5, padx=5, fill=tk.X, expand=True)

        self.color_var = tk.StringVar()
        self.color_combobox = ttk.Combobox(color_button_frame, textvariable=self.color_var, width=20)
        self.color_combobox['values'] = ['Color 1']  # Initial dummy value
        self.color_combobox.current(0)
        self.color_combobox.pack(pady=5, padx=5, fill=tk.X, expand=True)
        self.color_combobox.bind("<<ComboboxSelected>>", self.on_color_select)

        # Add IP and Port input fields

        # Sliders and toggles in the right frame with increased width (length parameter)
        def add_label_above_scale(parent, scale, label_text):
            label = tk.Label(parent, text=label_text)
            label.pack(pady=(10, 0))  # Add padding above the label
            label.configure(bg=dark_frame_color, fg=light_text_color)
            scale.pack(fill=tk.X, expand=False, padx=5)

        # Sliders and toggles in the right frame with increased width (length parameter)
        self.red_slider = ttk.Scale(self.frame_right, from_=0, to=255, orient='horizontal', command=self.slider_update)
        self.green_slider = ttk.Scale(self.frame_right, from_=0, to=255, orient='horizontal',
                                      command=self.slider_update)
        self.blue_slider = ttk.Scale(self.frame_right, from_=0, to=255, orient='horizontal', command=self.slider_update)
        self.difference_slider = ttk.Scale(self.frame_right, from_=0, to=40, orient='horizontal',
                                           command=self.slider_update)
        self.blur_slider = ttk.Scale(self.frame_right, from_=0, to=40, orient='horizontal', command=self.slider_update)
        self.save_image_toggle = ttk.Checkbutton(self.frame_right, text="Save Image", onvalue=True, offvalue=False,
                                                 command=self.save_image_toggle_func)

        # Add labels above each slider
        add_label_above_scale(self.frame_right, self.red_slider, "Red")
        add_label_above_scale(self.frame_right, self.green_slider, "Green")
        add_label_above_scale(self.frame_right, self.blue_slider, "Blue")
        add_label_above_scale(self.frame_right, self.difference_slider, "Difference")
        add_label_above_scale(self.frame_right, self.blur_slider, "Blur")

        self.text_box = tk.Text(self.frame_right, height=10, width=10, wrap='word')

        # Pack sliders and toggles in the right frame
        self.red_slider.pack(fill=tk.X, padx=5)
        self.green_slider.pack(fill=tk.X, padx=5)
        self.blue_slider.pack(fill=tk.X, padx=5)
        self.difference_slider.pack(fill=tk.X, padx=5)
        self.blur_slider.pack(fill=tk.X, padx=5)\

        # Create a frame for the color display
        color_display_frame = tk.Frame(self.frame_right, bg=dark_frame_color)
        color_display_frame.pack(pady=10, padx=5, fill=tk.X)

        # Create a label to display the current color
        self.color_display_label = tk.Label(color_display_frame, text="Current Color", bg=dark_frame_color,
                                            fg=light_text_color)
        self.color_display_label.pack(side=tk.LEFT, padx=5)

        # Create a canvas to show the current color
        self.color_display_canvas = tk.Canvas(color_display_frame, width=50, height=20, bg=dark_frame_color,
                                              highlightthickness=0)
        self.color_display_canvas.pack(side=tk.LEFT, padx=5)

        self.save_image_toggle.pack()
        self.text_box.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.text_box.bind("<<Modified>>", lambda event: self.scroll_to_bottom())
        self.text_box.bind("<KeyRelease>", lambda event: self.scroll_to_bottom())
        custom_font = font.Font(family="courier", size=12)
        self.text_box.configure(font=custom_font)

        self.image_label.bind("<Button-1>", self.on_image_click)

        try:
            with open('params.json', 'r') as f:
                self.color_list = json.load(f)
                red_val = self.color_list[0]["red"]
                green_val = self.color_list[0]["green"]
                blue_val = self.color_list[0]["blue"]
                blur_val = self.color_list[0]["blur"]
                difference_val = self.color_list[0]["difference"]
        except:
            self.insert_text("params.json not found. Using default values.")
            red_val = 0
            green_val = 0
            blue_val = 0
            blur_val = 0
            difference_val = 50
            self.color_list = [
                {"red": red_val, "green": green_val, "blue": blue_val, "difference": difference_val, "blur": blur_val}]
            with open('params.json', 'w') as f:
                json.dump(self.color_list, f, indent=4)

        self.red_slider.set(red_val)
        self.green_slider.set(green_val)
        self.blue_slider.set(blue_val)
        self.difference_slider.set(difference_val)
        self.blur_slider.set(blur_val)



        # Then, apply these colors to the main window and widgets
        self.configure(bg=dark_background_color)  # Main window background

        # Frames
        self.frame_left.configure(bg=dark_frame_color)
        self.frame_right.configure(bg=dark_frame_color)
        self.left_panel.configure(bg=dark_frame_color)
        buttons_frame.configure(bg=dark_frame_color)
        color_button_frame.configure(bg=dark_frame_color)
        self.frame_separator.configure(bg=dark_background_color)  # Separator might remain the same or adjust as needed
        ip_port_frame.configure(bg=dark_frame_color)
        # Labels
        self.image_label.configure(
            bg=dark_frame_color)  # Assuming you want the image background to be dark when no image is displayed
        self.fps_label.configure(bg=fps_label_color, fg=light_text_color)

        # Sliders - You'll need to create a custom style for sliders to change the trough color
        style = ttk.Style()
        style.theme_use('alt')  # 'clam' theme allows for more customization
        style.configure("Horizontal.TScale", background=dark_frame_color, troughcolor=slider_trough_color,
                        sliderlength=10, sliderwidth=10, borderwidth=3, sliderrelief='groove')

        # Apply the custom style to each ttk.Scale widget
        self.red_slider.configure(style="Horizontal.TScale")
        self.green_slider.configure(style="Horizontal.TScale")
        self.blue_slider.configure(style="Horizontal.TScale")
        self.difference_slider.configure(style="Horizontal.TScale")
        self.blur_slider.configure(style="Horizontal.TScale")

        # Toggle buttons - Custom style for Checkbuttons
        style.configure("Custom.TCheckbutton", background=dark_frame_color, foreground=light_text_color,
                        selectcolor=dark_frame_color, borderwidth=0)
        self.save_image_toggle.configure(style="Custom.TCheckbutton")

        style.configure("Dark.TButton", foreground=light_text_color, background=dark_frame_color, borderwidth=1,
                        focusthickness=0, focuscolor='none')
        style.map("Dark.TButton",
                  foreground=[("pressed", dark_frame_color), ("active", light_text_color)],
                  background=[("pressed", "!disabled", light_text_color), ("active", dark_frame_color)],
                  relief=[("pressed", "sunken"), ("!pressed", "raised")])

        style.configure("Dark.TCombobox", fieldbackground=dark_frame_color, background=dark_background_color,
                        foreground=light_text_color, arrowcolor=light_text_color)
        style.map("Dark.TCombobox",
                  fieldbackground=[("active", dark_frame_color)],
                  background=[("active", dark_background_color)],
                  foreground=[("active", light_text_color)],
                  selectbackground=[("active", dark_frame_color)],
                  selectforeground=[("active", light_text_color)])

        style.configure("Dark.TEntry", fieldbackground=dark_frame_color, background=dark_background_color,
                        foreground=light_text_color, insertcolor=light_text_color)
        style.map("Dark.TEntry",
                  fieldbackground=[("active", dark_frame_color)],
                  background=[("active", dark_background_color)],
                  foreground=[("active", light_text_color)])

        # Apply the custom styles to the buttons and combobox
        self.load_params_button.configure(style="Dark.TButton")
        self.save_params_button.configure(style="Dark.TButton")
        self.add_color_button.configure(style="Dark.TButton")
        self.delete_color_button.configure(style="Dark.TButton")
        self.color_combobox.configure(style="Dark.TCombobox")
        self.mode_combobox.configure(style="Dark.TCombobox")
        self.text_box.configure(bg=dark_frame_color, fg=light_text_color, insertbackground=light_text_color)
        self.ip_entry.configure(style="Dark.TEntry")
        self.port_entry.configure(style="Dark.TEntry")
        self.update_ip_button.configure(style="Dark.TButton")
        ip_label.configure(fg=light_text_color, bg=dark_frame_color)
        port_label.configure(fg=light_text_color, bg=dark_frame_color)

        # Step 2: Create functions to change the style on hover
        def on_enter(event):
            event.widget.configure(
                style="Hover.TCheckbutton")  # Assuming Hover.TCheckbutton is a style you defined for hover

        def on_leave(event):
            event.widget.configure(style="Custom.TCheckbutton")  # Revert to the original style

        # Define a hover style
        style.map("Hover.TCheckbutton",
                  background=[("active", "#555555")],  # Custom color when hovered
                  foreground=[("active", "#FFFFFF")])

        # Step 3: Bind the hover functions to the toggle buttons
        self.save_image_toggle.bind("<Enter>", on_enter)
        self.save_image_toggle.bind("<Leave>", on_leave)

        self.load_all_colors_from_json()

    def change_command(self, new_command):
        if self.command is None:
            self.command = new_command
            return True
        return False


    def update_ip(self):
        self.raspberry_pi_ip = self.ip_entry.get()
        self.port = int(self.port_entry.get())
        self.insert_text(f"Updated IP and Port to {self.raspberry_pi_ip}:{self.port}\n")

    def display_image(self, pil_image):
        # Get the dimensions of the frame
        frame_width = self.frame_left.winfo_width() - 2
        frame_height = self.frame_left.winfo_height()

        # Calculate the aspect ratio of the image and the frame
        image_aspect = pil_image.width / pil_image.height
        frame_aspect = frame_width / frame_height

        # Determine how to scale based on the relative aspect ratios
        if image_aspect > frame_aspect:
            # Image is wider than the frame, scale based on frame's width
            new_width = max(frame_width, 20)
            new_height = max(int(frame_width / image_aspect), 20)
        else:
            # Image is taller than the frame, scale based on frame's height
            new_height = max(frame_height, 20)
            new_width = max(int(frame_height * image_aspect), 20)

        # Resize the image to fill the frame while maintaining aspect ratio
        resized_image = pil_image.resize((new_width, new_height))
        photo_image = ImageTk.PhotoImage(resized_image)

        # Display the image
        self.image_label.configure(image=photo_image)
        self.image_label.image = photo_image  # Keep a reference to avoid garbage collection  # Keep a reference to avoid garbage collection

    def change_image(self, new_image_array, fps=0.0):
        if isinstance(new_image_array, np.ndarray):
            new_pil_image = Image.fromarray(new_image_array)
            self.display_image(new_pil_image)
            self.current_pil_image = new_pil_image
            if self.save_image:
                new_pil_image.save("image.jpg")
        else:
            self.insert_text(new_image_array + "\n")
        self.fps_label.configure(text=f"FPS: {fps:.4f}")

    def scroll_to_bottom(self):
        self.text_box.see(tk.END)

    def insert_text(self, text):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, text)
        self.text_box.config(state=tk.DISABLED)
        self.scroll_to_bottom()

    def slider_update(self, value=None):
        # Assemble the slider values into a string
        red_value = self.red_slider.get()
        green_value = self.green_slider.get()
        blue_value = self.blue_slider.get()
        difference_value = self.difference_slider.get()
        blur_value = self.blur_slider.get()
        color_hex = f"#{int(red_value):02x}{int(green_value):02x}{int(blue_value):02x}"
        self.color_display_canvas.configure(bg=color_hex)

        val_dict = {
            "red": red_value,
            "green": green_value,
            "blue": blue_value,
            "difference": difference_value,
            "blur": blur_value,
        }
        self.color_list[min(self.active_color, len(self.color_list))] = val_dict

        with open('params.json', 'w') as f:
            json.dump(self.color_list, f, indent=4)

        temp = self.color_list.copy()
        temp.append(self.active_color)

        self.command = f"color -values={json.dumps(temp)}"

    def save_image_toggle_func(self):
        self.save_image = not self.save_image

    def on_mode_select(self, event):
        selected_mode = self.mode_var.get()
        if selected_mode == 'AprilTag':
            self.mode = "apriltag_image"
        elif selected_mode == 'Processed':
            self.mode = "processed_image"
        elif selected_mode == 'Raw':
            self.mode = "raw_image"
        elif selected_mode == 'Headless Piece Location':
            self.mode = "find_piece"
        elif selected_mode == 'Headless AprilTag Detection':
            self.mode = "fa"

    def on_image_click(self, event):
        if self.current_pil_image is None:
            self.insert_text("No image loaded.\n")
            return

        # Get the dimensions of the displayed image
        display_width = self.image_label.winfo_width()
        display_height = self.image_label.winfo_height()

        # Get the dimensions of the original image
        original_width, original_height = self.current_pil_image.size

        # Calculate the aspect ratio of the displayed image and the original image
        width_ratio = original_width / display_width
        height_ratio = original_height / display_height

        # Determine the scaling factor based on the aspect ratio
        if width_ratio > height_ratio:
            scale_factor = width_ratio
        else:
            scale_factor = height_ratio

        # Calculate the coordinates in the original image
        original_x = int(event.x * scale_factor)
        original_y = int(event.y * scale_factor)

        # Ensure the coordinates are within the bounds of the original image
        original_x = min(max(original_x, 0), original_width - 1)
        original_y = min(max(original_y, 0), original_height - 1)

        # Get the pixel color at the calculated coordinates
        pixel = self.current_pil_image.getpixel((original_x, original_y))

        # Update the sliders with the pixel color values
        self.red_slider.set(pixel[0])
        self.green_slider.set(pixel[1])
        self.blue_slider.set(pixel[2])

    def load_parameters(self):
        # If there is no presets folder, create one
        if not os.path.exists("Presets"):
            os.makedirs("Presets")

        # Open file dialog to select a parameter file
        filepath = filedialog.askopenfilename(title="Select a Parameter File",
                                              filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
                                              initialdir="./Presets/")

        if not filepath:
            return  # User cancelled the dialog

        try:
            with open(filepath, 'r') as f:
                self.color_list = json.load(f)

            self.red_slider.set(self.color_list[self.active_color]["red"])
            self.green_slider.set(self.color_list[self.active_color]["green"])
            self.blue_slider.set(self.color_list[self.active_color]["blue"])
            self.difference_slider.set(self.color_list[self.active_color]["difference"])
            self.blur_slider.set(self.color_list[self.active_color]["blur"])

            self.slider_update()
        except Exception as e:
            self.insert_text(f"Error loading parameters: {e}\n")

    def save_parameters(self):
        # Open save file dialog to let the user name and choose where to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                                 initialdir="./Presets/")

        # Check if the user canceled the save operation
        if not file_path:
            return  # User cancelled the dialog

        # Gather current slider values
        values = {
            "red": self.red_slider.get(),
            "green": self.green_slider.get(),
            "blue": self.blue_slider.get(),
            "blur": self.blur_slider.get(),
            "difference": self.difference_slider.get(),
        }
        self.color_list[self.active_color] = values

        # Write values to the file
        try:
            with open(file_path, 'w') as file:
                json.dump(self.color_list, file, indent=4)
            self.insert_text(f"Parameters saved to {file_path}\n")
        except Exception as e:
            self.insert_text(f"Error saving parameters: {e}\n")

    def add_color(self):
        # Add a new color configuration
        new_color_name = f"Color {len(self.color_list) + 1}"
        self.color_list.append(self.color_list[self.active_color].copy())
        self.update_combobox()
        self.color_combobox.current(len(self.color_list) - 1)

    def delete_color(self):
        # Delete the selected color configuration
        current_index = self.color_combobox.current()
        if current_index >= 0 and len(self.color_list) > 1:
            del self.color_list[current_index]
            self.update_combobox()
            self.color_combobox.current(len(self.color_list) - 1)

    def load_all_colors_from_json(self):
        try:
            with open('params.json', 'r') as f:
                self.color_list = json.load(f)
                # Update the combobox values based on loaded colors
                self.update_combobox()
        except FileNotFoundError:
            self.insert_text("params.json not found. Loading default color.\n")
            self.color_list = [{"red": 0, "green": 0, "blue": 0, "difference": 50, "blur": 0}]
            self.update_combobox()

    def update_combobox(self):
        # Update the values in the combobox
        values = [f"Color {i + 1}" for i in range(len(self.color_list))]
        self.color_combobox['values'] = values
        if values:
            self.color_combobox.current(0)
        else:
            self.color_var.set('')

    def on_color_select(self, event):
        # Update UI based on selected color configuration
        self.red_slider.configure(command="")
        self.green_slider.configure(command="")
        self.blue_slider.configure(command="")
        self.difference_slider.configure(command="")
        self.blur_slider.configure(command="")

        current_index = self.color_combobox.current()
        self.active_color = min(current_index, len(self.color_list))
        if current_index >= 0:
            selected_config = self.color_list[self.active_color]
            self.red_slider.set(selected_config["red"])
            self.green_slider.set(selected_config["green"])
            self.blue_slider.set(selected_config["blue"])
            self.difference_slider.set(selected_config["difference"])
            self.blur_slider.set(selected_config["blur"])

            self.command = f"sc -new_color={current_index}"

        self.red_slider.configure(command=self.slider_update)
        self.green_slider.configure(command=self.slider_update)
        self.blue_slider.configure(command=self.slider_update)
        self.difference_slider.configure(command=self.slider_update)
        self.blur_slider.configure(command=self.slider_update)

    async def websocket_client(self):
        try:
            async with websockets.connect(f"ws://{self.raspberry_pi_ip}:{self.port}", ping_timeout=None,
                                          ping_interval=None) as websocket:
                self.insert_text(f"Connected to {self.raspberry_pi_ip}:{self.port}\n")
                current_ip = self.raspberry_pi_ip
                current_port = self.port

                await websocket.send("info")
                info_response = await websocket.recv()
                try:
                    info_data = json.loads(info_response)
                    camera_width = info_data.get("horizontal_resolution_pixels", 640)
                    camera_height = info_data.get("vertical_resolution_pixels", 480)
                    processing_scale = info_data.get("processing_scale", 4)
                    self.insert_text(f"Camera resolution: {camera_width}x{camera_height}\n")
                except json.JSONDecodeError:
                    self.insert_text("Failed to decode camera info response.\n")
                    camera_width = 640
                    camera_height = 480
                    processing_scale = 4
                while True:
                    if current_ip != self.raspberry_pi_ip or current_port != self.port:
                        self.insert_text("IP or port changed. Restarting websocket connection...\n")
                        break

                    if self.command is not None:
                        await websocket.send(self.command)
                        self.command = None
                        continue
                    else:
                        await websocket.send(self.mode)

                    start = time.time()
                    response = await websocket.recv()
                    try:
                        response = np.frombuffer(response, dtype=np.uint8)
                        response = np.asarray(response).reshape((camera_height // processing_scale,
                                                                 camera_width // processing_scale, 3))
                    except Exception as e:
                        if 'str' not in str(e):
                            if "cannot reshape array of size" in str(e):
                                self.command = "info"
                            self.insert_text(f"Failed to decode image: {e}\n")
                        elif "cam_name" in response:
                            # We recieved an info call. Set the camera height and processing scale.
                            info_data = json.loads(response)
                            camera_width = info_data.get("horizontal_resolution_pixels", 640)
                            camera_height = info_data.get("vertical_resolution_pixels", 480)
                            processing_scale = info_data.get("processing_scale", 4)
                        pass
                    # Update the image on the label
                    self.change_image(response, 1 / (time.time() - start))

        except asyncio.CancelledError:
            self.insert_text("Websocket task was cancelled. Cleaning up...\n")
        except websockets.exceptions.ConnectionClosedError as e:
            self.insert_text(f"Websocket connection closed unexpectedly: {e}\n")
        except Exception as e:
            if "Errno 10054" in str(e):
                self.insert_text("Connection closed by the server.\n")
            elif "Errno 10061" in str(e):
                self.insert_text("Connection refused. Is the server running?\n")
            elif "Errno 10049" in str(e):
                self.insert_text("The requested address is not valid in this context. Is the IP address correct?\n")
            elif "Errno 111" in str(e):
                self.insert_text("Connection refused. Is the server running?\n")
            else:
                self.insert_text(f"An unexpected error occurred: {e}\n")

    def start_asyncio_event_loop(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        while True:
            asyncio.get_event_loop().run_until_complete(self.websocket_client())


if __name__ == "__main__":
    app = App()
    asyncio_thread = threading.Thread(target=app.start_asyncio_event_loop)
    asyncio_thread.start()
    app.mainloop()
