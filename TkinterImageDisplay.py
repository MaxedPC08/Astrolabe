from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage
import asyncio
import websockets
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np


SAVE_IMAGE = False
PROCESS_IMAGE = False
RASPBERRY_PI_IP = "192.168.39.182" # Ah! You have my IP address! I'm doomed! Jk this is just the local one.

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.new_vals = None
        self.title("Image Viewer")
        self.geometry("1000x1200")

        self.current_image = None
        self.image_label = tk.Label(self, width=640, height=480)
        self.fps_label = tk.Label(self, width=50, height=20, text="FPS: 0")


        # Define sliders
        self.red_slider = tk.Scale(self, from_=0, to=255, orient='horizontal', label='Red', command=self.slider_update)
        self.green_slider = tk.Scale(self, from_=0, to=255, orient='horizontal', label='Green',
                                     command=self.slider_update)
        self.blue_slider = tk.Scale(self, from_=0, to=255, orient='horizontal', label='Blue', command=self.slider_update)
        self.difference_slider = tk.Scale(self, from_=0, to=40, orient='horizontal', label='Difference',
                                          command=self.slider_update)
        self.blur_slider = tk.Scale(self, from_=0, to=40, orient='horizontal', label='Blur', command=self.slider_update)

        # Place sliders

        self.image_label.pack()
        self.fps_label.pack()
        self.red_slider.pack()
        self.green_slider.pack()
        self.blue_slider.pack()
        self.difference_slider.pack()
        self.blur_slider.pack()


    def display_image(self, image):
        image = image.resize((800, 600))
        image = ImageTk.PhotoImage(image)
        self.image_label.configure(image=image)
        self.image_label.image = image

    def change_image(self, new_image_array, fps=0.0):
        new_image = Image.fromarray(new_image_array)
        self.display_image(new_image)
        self.fps_label.configure(text=f"FPS: {fps:.4f}")
        if SAVE_IMAGE:
            new_image.save("image.jpg")

    def slider_update(self, value):
        # Assemble the slider values into a string
        red_value = self.red_slider.get()
        green_value = self.green_slider.get()
        blue_value = self.blue_slider.get()
        difference_value = self.difference_slider.get()
        blur_value = self.blur_slider.get()
        values = f"{red_value},{green_value},{blue_value},{difference_value},{blur_value}"
        print(f"Sending values: {values}")

        #Save files to the local params.txt file
        with open('params.txt', 'w') as f:
            f.write(f"Red: {red_value}\n")
            f.write(f"Green: {green_value}\n")
            f.write(f"Blue: {blue_value}\n")
            f.write(f"Blur: {blur_value}\n")
            f.write(f"Difference: {difference_value}\n")


        self.new_vals = values

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
