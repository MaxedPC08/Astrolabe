from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage
import asyncio
import websockets
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np


SAVE_IMAGE = False
PROCESS_IMAGE = False
RASPBERRY_PI_IP = "10.42.0.118" # Ah! You have my IP address! I'm doomed! Jk this is just the local one.

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_pil_image = None
        self.new_vals = None
        self.title("Image Viewer")
        self.geometry("1200x600")

        # Create main frames for layout
        self.frame_left = tk.Frame(self)
        self.frame_right = tk.Frame(self)
        self.frame_separator = tk.Frame(self, width=2, bg='black')  # Aesthetic vertical bar

        # Pack the main frames to the left and right, separator in between
        # Adjust the packing of the main frames
        self.frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_separator.pack(side=tk.LEFT, fill=tk.Y)  # Pack the separator frame
        self.frame_right.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        # Image and FPS label in the left frame
        self.image_label = tk.Label(self.frame_left)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Adjustments for the FPS label to overlay on the image
        self.fps_label = tk.Label(self.frame_left, text="FPS: 0", bg='black', fg='white', font=("Helvetica", 12))
        # This will place the FPS label at the bottom-right corner of the left frame
        self.fps_label.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor="se")

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
        self.brightness_slider = tk.Scale(self.frame_right, from_=0, to=250, orient='horizontal', label='Brightness',
                                          command=self.slider_update, length=300)
        self.contrast_slider = tk.Scale(self.frame_right, from_=0, to=20, orient='horizontal', label='Contrast',
                                        command=self.slider_update, length=300)
        self.save_image_toggle = ttk.Checkbutton(self.frame_right, text="Save Image", onvalue=True, offvalue=False,
                                                 command=self.save_image_toggle_func)
        self.process_image_toggle = ttk.Checkbutton(self.frame_right, text="Process Image", onvalue=True,
                                                    offvalue=False, command=self.process_image_toggle_func)

        # Pack sliders and toggles in the right frame
        self.red_slider.pack()
        self.green_slider.pack()
        self.blue_slider.pack()
        self.difference_slider.pack()
        self.blur_slider.pack()
        self.brightness_slider.pack()
        self.contrast_slider.pack()
        self.save_image_toggle.pack()
        self.process_image_toggle.pack()

        self.image_label.bind("<Button-1>", self.on_image_click)

        # Load initial slider values from the params.txt file
        try:
            with open('params.txt', 'r') as f:
                lines = f.readlines()
                red_val = int(lines[0].split(": ")[1])
                green_val = int(lines[1].split(": ")[1])
                blue_val = int(lines[2].split(": ")[1])
                blur_val = int(lines[3].split(": ")[1])
                difference_val = int(lines[4].split(": ")[1])
                brightness_val = int(lines[5].split(": ")[1])
                contrast_val = int(lines[6].split(": ")[1])
        except FileNotFoundError:
            print("params.txt not found. Using default values.")
            red_val = 0
            green_val = 0
            blue_val = 0
            blur_val = 0
            difference_val = 50
            brightness_val = 40
            contrast_val = 50

        self.red_slider.set(red_val)
        self.green_slider.set(green_val)
        self.blue_slider.set(blue_val)
        self.difference_slider.set(difference_val)
        self.blur_slider.set(blur_val)
        self.brightness_slider.set(brightness_val)
        self.contrast_slider.set(contrast_val)

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
        self.frame_separator.configure(bg=dark_background_color)  # Separator might remain the same or adjust as needed

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
        self.brightness_slider.configure(bg=dark_frame_color, fg=light_text_color, troughcolor=slider_trough_color,
                                        highlightbackground=dark_frame_color, activebackground=light_text_color)
        self.contrast_slider.configure(bg=dark_frame_color, fg=light_text_color, troughcolor=slider_trough_color,
                                        highlightbackground=dark_frame_color, activebackground=light_text_color)

        # Toggle buttons - Custom style for Checkbuttons
        style.configure("Custom.TCheckbutton", background=dark_frame_color, foreground=light_text_color,
                        selectcolor=dark_frame_color, borderwidth=0)
        self.save_image_toggle.configure(style="Custom.TCheckbutton")
        self.process_image_toggle.configure(style="Custom.TCheckbutton")

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

        self.process_image_toggle.bind("<Enter>", on_enter)
        self.process_image_toggle.bind("<Leave>", on_leave)

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
        new_pil_image = Image.fromarray(new_image_array)
        self.display_image(new_pil_image)
        self.fps_label.configure(text=f"FPS: {fps:.4f}")
        self.current_pil_image = new_pil_image
        if SAVE_IMAGE:
            new_pil_image.save("image.jpg")

    def slider_update(self, value):
        # Assemble the slider values into a string
        red_value = self.red_slider.get()
        green_value = self.green_slider.get()
        blue_value = self.blue_slider.get()
        difference_value = self.difference_slider.get()
        blur_value = self.blur_slider.get()
        brightness_value = self.brightness_slider.get()
        contrast_value = self.contrast_slider.get()

        values = f"{red_value},{green_value},{blue_value},{difference_value},{blur_value},{brightness_value},{contrast_value}"
        print(f"Sending values: {values}")

        #Save files to the local params.txt file
        with open('params.txt', 'w') as f:
            f.write(f"Red: {red_value}\n")
            f.write(f"Green: {green_value}\n")
            f.write(f"Blue: {blue_value}\n")
            f.write(f"Blur: {blur_value}\n")
            f.write(f"Difference: {difference_value}\n")
            f.write(f"Brightness: {brightness_value}\n")
            f.write(f"Contrast: {contrast_value}\n")


        self.new_vals = values

    def save_image_toggle_func(self):
        global SAVE_IMAGE
        SAVE_IMAGE = not SAVE_IMAGE
        print(f"Save image toggle: {SAVE_IMAGE}")

    def process_image_toggle_func(self):
        global PROCESS_IMAGE
        PROCESS_IMAGE = not PROCESS_IMAGE
        print(f"Process image toggle: {PROCESS_IMAGE}")


    def on_image_click(self, event):
        if self.current_pil_image is None:
            print("No image loaded.")
            return

        display_width, display_height = 800, 600
        original_width, original_height = self.current_pil_image.size  # Use the stored PIL Image object

        width_ratio = original_width / display_width
        height_ratio = original_height / display_height

        original_x = int(event.x * width_ratio)
        original_y = int(event.y * height_ratio)

        pixel = self.current_pil_image.getpixel((original_x, original_y))

        self.red_slider.set(pixel[0])
        self.green_slider.set(pixel[1])
        self.blue_slider.set(pixel[2])

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

    def update_image(self, image):
        q_image = QImage(image.data.tobytes(), image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(q_image))



"""async def websocket_client():
    async with websockets.connect(f"ws://{RASPBERRY_PI_IP}:8765") as websocket:
        if PROCESS_IMAGE:
            message = "processed"
        else:
            message = "raw"
        await websocket.send(message)

        while True:  # Keep receiving and displaying new images
            start = time.time()
            response = await websocket.recv()
            response = np.asarray(np.frombuffer(response, dtype=np.uint8)).reshape((480 // 4, 640 // 4, 3))
            print(f"Received response")
            # Update the image on the label
            app.change_image(response, 1/(time.time() - start))

            print(f"Set IMG and received response at {1/(time.time() - start):.2f} fps")"""


async def websocket_client():
    try:
        timeout = 10 # Set your desired timeout period here (in seconds)
        while True:
            async with websockets.connect(f"ws://{RASPBERRY_PI_IP}:8765", ping_timeout=None, ping_interval=None) as websocket:
                if app.new_vals is not None:
                    await websocket.send(f"values {app.new_vals}")
                    app.new_vals = None
                    continue
                if PROCESS_IMAGE:
                    message = "processed"
                else:
                    message = "raw"
                await websocket.send(message)

                start = time.time()
                response = await websocket.recv()
                response = np.asarray(np.frombuffer(response, dtype=np.uint8)).reshape((480 // 4, 640 // 4, 3))
                # Update the image on the label
                app.change_image(response, 1 / (time.time() - start))

    except asyncio.CancelledError:
        print("Websocket task was cancelled. Cleaning up...")
        # Perform any necessary cleanup here
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Websocket connection closed unexpectedly: {e}")
        # Handle connection closed error here
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle any other exceptions here

def start_asyncio_event_loop():
    asyncio.set_event_loop(asyncio.new_event_loop())
    while True:
        asyncio.get_event_loop().run_until_complete(websocket_client())

if __name__ == "__main__":
    app = App()
    asyncio_thread = threading.Thread(target=start_asyncio_event_loop)
    asyncio_thread.start()
    # Start running asyncio tasks periodically from Tkinter's event loop
    app.mainloop()
