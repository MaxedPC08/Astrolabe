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
        self.geometry("1000x1200")

        self.image_label = tk.Label(self, width=640, height=480)
        self.fps_label = tk.Label(self, width=50, height=20, text="FPS: 0")

        self.image_label.bind("<Button-1>", self.on_image_click)

        # Define sliders
        self.red_slider = tk.Scale(self, from_=0, to=255, orient='horizontal', label='Red', command=self.slider_update)
        self.green_slider = tk.Scale(self, from_=0, to=255, orient='horizontal', label='Green',
                                     command=self.slider_update)
        self.blue_slider = tk.Scale(self, from_=0, to=255, orient='horizontal', label='Blue', command=self.slider_update)
        self.difference_slider = tk.Scale(self, from_=0, to=40, orient='horizontal', label='Difference',
                                          command=self.slider_update)
        self.blur_slider = tk.Scale(self, from_=0, to=40, orient='horizontal', label='Blur', command=self.slider_update)

        self.brightness_slider = tk.Scale(self, from_=0, to=250, orient='horizontal', label='Brightness', command=self.slider_update)
        self.contrast_slider = tk.Scale(self, from_=0, to=20, orient='horizontal', label='Contrast', command=self.slider_update)

        self.save_image_toggle = ttk.Checkbutton(self, text="Save Image", onvalue=True, offvalue=False, command=self.save_image_toggle_func)
        self.process_image_toggle = ttk.Checkbutton(self, text="Process Image", onvalue=True, offvalue=False, command=self.process_image_toggle_func)


        # Get initial slider values from the params.txt file
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

        # Place sliders
        self.image_label.pack()
        self.fps_label.pack()
        self.save_image_toggle.pack()
        self.process_image_toggle.pack()
        self.red_slider.pack()
        self.green_slider.pack()
        self.blue_slider.pack()
        self.difference_slider.pack()
        self.blur_slider.pack()
        self.brightness_slider.pack()
        self.contrast_slider.pack()

    def display_image(self, pil_image):
        self.current_pil_image = pil_image  # Store the PIL Image object
        image = pil_image.resize((800, 600))
        photo_image = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo_image)
        self.image_label.image = photo_image  # Keep a reference to avoid garbage collection

    def change_image(self, new_image_array, fps=0.0):
        new_pil_image = Image.fromarray(new_image_array)
        self.display_image(new_pil_image)
        self.fps_label.configure(text=f"FPS: {fps:.4f}")
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
