import asyncio
import websockets
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import font
from PIL import Image, ImageTk
import numpy as np
import os
import json
import struct


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.save_image = False
        self.current_pil_image = None
        self.command = None
        self.active_color = 0
        self.title("Image Viewer")
        self.geometry("1200x600")
        self.raspberry_pi_ip = "10.42.0.118"
        self.port = 50000
        self.mode = "apriltag_image"

        # Create main frames for layout
        self.frame_left = tk.Frame(self)
        self.frame_right = tk.Frame(self, width=300)
        self.frame_separator = tk.Frame(self, width=2, bg='black')  # Aesthetic vertical bar

        # Configure the grid layout
        self.grid_columnconfigure(0, weight=1)  # Left frame has less weight, shrinks first
        self.grid_columnconfigure(1, weight=0)  # Separator, fixed width, does not resize
        self.grid_columnconfigure(2, weight=2)  # Right frame has more weight, shrinks last and expands first

        # Place the frames using grid
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_separator.grid(row=0, column=1, sticky="ns")
        self.frame_right.grid(row=0, column=2, sticky="nsew")

        # Make the main window's row 0 expandable
        self.grid_rowconfigure(0, weight=1)

        # Further configuration for the right frame to ensure it behaves as desired
        self.frame_right.grid_propagate(False)  # Prevents the frame from shrinking beyond its widgets' sizes


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
        self.color_combobox = ttk.Combobox(color_button_frame, textvariable=self.color_var)
        self.color_combobox['values'] = ['Color 1']  # Initial dummy value
        self.color_combobox.current(0)
        self.color_combobox.pack(pady=5, padx=5, fill=tk.X, expand=True)
        self.color_combobox.bind("<<ComboboxSelected>>", self.on_color_select)



        # Add IP and Port input fields

        # Sliders and toggles in the right frame with increased width (length parameter)
        self.red_slider = tk.Scale(self.frame_right, from_=0, to=255, orient='horizontal', label='Red',
                                   command=self.slider_update, length=300)
        self.green_slider = tk.Scale(self.frame_right, from_=0, to=255, orient='horizontal', label='Green',
                                     command=self.slider_update, length=300)
        self.blue_slider = tk.Scale(self.frame_right, from_=0, to=255, orient='horizontal', label='Blue',
                                    command=self.slider_update, length=300)
        self.difference_slider = tk.Scale(self.frame_right, from_=0, to=40, orient='horizontal', label='Difference',
                                          command=self.slider_update, length=300)
        self.blur_slider = tk.Scale(self.frame_right, from_=0, to=40, orient='horizontal', label='Blur',
                                    command=self.slider_update, length=300)
        self.save_image_toggle = ttk.Checkbutton(self.frame_right, text="Save Image", onvalue=True, offvalue=False,
                                                 command=self.save_image_toggle_func)

        self.text_box = tk.Text(self.frame_right, height=10, width=30)


        # Pack sliders and toggles in the right frame
        self.red_slider.pack()
        self.green_slider.pack()
        self.blue_slider.pack()
        self.difference_slider.pack()
        self.blur_slider.pack()
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
            self.color_list = [{"red": red_val, "green": green_val, "blue": blue_val, "difference": difference_val, "blur": blur_val}]
            with open('params.json', 'w') as f:
                json.dump(self.color_list, f, indent=4)

        self.red_slider.set(red_val)
        self.green_slider.set(green_val)
        self.blue_slider.set(blue_val)
        self.difference_slider.set(difference_val)
        self.blur_slider.set(blur_val)

        # First, define the colors for the dark mode
        dark_background_color = "#333333"
        light_text_color = "#CCCCCC"
        dark_frame_color = "#444444"
        slider_trough_color = "#555555"
        fps_label_color = "#111111"

        # Then, apply these colors to the main window and widgets
        self.configure(bg=dark_background_color)  # Main window background

        # Frames
        self.frame_left.configure(bg=dark_frame_color)
        self.frame_right.configure(bg=dark_frame_color)
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
        style.theme_use('clam')  # 'clam' theme allows for more customization
        style.configure("Horizontal.TScale", background=dark_frame_color, troughcolor=slider_trough_color,
                        sliderrelief="flat", sliderlength=30, sliderwidth=10, borderwidth=0)

        # Apply the custom style to each slider
        self.red_slider.configure(bg=dark_frame_color, fg=light_text_color, troughcolor=slider_trough_color,
                                  highlightbackground=dark_frame_color, activebackground=light_text_color)
        self.green_slider.configure(bg=dark_frame_color, fg=light_text_color, troughcolor=slider_trough_color,
                                    highlightbackground=dark_frame_color, activebackground=light_text_color)
        self.blue_slider.configure(bg=dark_frame_color, fg=light_text_color, troughcolor=slider_trough_color,
                                      highlightbackground=dark_frame_color, activebackground=light_text_color)
        self.difference_slider.configure(bg=dark_frame_color, fg=light_text_color, troughcolor=slider_trough_color,
                                        highlightbackground=dark_frame_color, activebackground=light_text_color)
        self.blur_slider.configure(bg=dark_frame_color, fg=light_text_color, troughcolor=slider_trough_color,
                                    highlightbackground=dark_frame_color, activebackground=light_text_color)

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
                        foreground=light_text_color)
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

    def update_ip(self):
        self.raspberry_pi_ip = self.ip_entry.get()
        self.port = int(self.port_entry.get())
        self.insert_text(f"Updated IP and Port to {self.raspberry_pi_ip}:{self.port}\n")

    def display_image(self, pil_image):
        # Get the dimensions of the frame
        frame_width = self.frame_left.winfo_width()-2
        frame_height = self.frame_left.winfo_height()

        # Calculate the aspect ratio of the image and the frame
        image_aspect = pil_image.width / pil_image.height
        frame_aspect = frame_width / frame_height

        # Determine how to scale based on the relative aspect ratios
        if image_aspect > frame_aspect:
            # Image is wider than the frame, scale based on frame's width
            new_width = frame_width
            new_height = int(frame_width / image_aspect)
        else:
            # Image is taller than the frame, scale based on frame's height
            new_height = frame_height
            new_width = int(frame_height * image_aspect)

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


        self.command = f"sp -values={json.dumps(temp)}"

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
            self.mode = "apriltag_headless"

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
        if current_index >= 0:
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
        values = [f"Color {i+1}" for i in range(len(self.color_list))]
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
                    await websocket.send(self.mode)

                    start = time.time()
                    response = await websocket.recv()
                    try:
                        response = np.frombuffer(response, dtype=np.uint8)
                        response = np.asarray(response).reshape((camera_height//processing_scale,
                                                                 camera_width//processing_scale, 3))
                    except Exception as e:
                        if 'str' not in str(e):
                            self.insert_text(f"Failed to decode image: {e}\n")
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
                raise e
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
