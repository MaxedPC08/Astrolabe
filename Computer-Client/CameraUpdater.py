import tkinter as tk
from tkinter import ttk
from tkinter import Text
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

class CameraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Camera Settings")
        self.config_file = "camera-settings.json"

        # Create input fields for IP address and port
        self.create_input_field("IP Address:", "ip_address")
        self.create_input_field("Port:", "port")

        # Create input fields for camera values
        self.create_input_field("Height:", "height")
        self.create_input_field("Horizontal Resolution:", "horizontal_resolution_pixels")
        self.create_input_field("Vertical Resolution:", "vertical_resolution_pixels")
        self.create_input_field("Processing Scale:", "processing_scale")
        self.create_input_field("Tilt Angle (radians):", "tilt_angle_radians")
        self.create_input_field("Horizontal FOV (radians):", "horizontal_field_of_view_radians")
        self.create_input_field("Vertical FOV (radians):", "vertical_field_of_view_radians")

        # Add a separator
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', pady=10)

        # Create input fields for aspect ratio and diagonal FOV
        self.create_input_field("Aspect Ratio (Horizontal):", "aspect_ratio_horizontal")
        self.create_input_field("Aspect Ratio (Vertical):", "aspect_ratio_vertical")
        self.create_input_field("Diagonal FOV (degrees):", "diagonal_fov")

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', pady=10)

        self.create_input_field("Additional Flags:", "additional_flags")

        # Add a button to send the values
        self.send_button = ttk.Button(self, text="Send Values", command=self.send_values)
        self.send_button.pack(pady=10)

        # Add a text box for server response
        self.response_text = Text(self, height=10, wrap='word')
        self.response_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Load parameters from file
        self.load_parameters()

    def create_input_field(self, label_text, var_name):
        frame = ttk.Frame(self)
        frame.pack(pady=5, padx=10, fill=tk.X)

        label = ttk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT, padx=5)

        entry = ttk.Entry(frame)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        setattr(self, var_name, entry)

    def get_values(self):
        try:
            dict = {}
            var_names = [["ip_address", self.ip_address, str], ["port", self.port, int], ["height", self.height, float],
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
            self.response_text.insert(tk.END, f"Error: {e}\n")
        except KeyError as e:
            self.response_text.insert(tk.END, f"Error: {e}\n")
    def set_values(self, values):
        self.ip_address.insert(0, values.get("ip_address", ""))
        self.port.insert(0, values.get("port", ""))
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



        uri = f"ws://{values['ip_address']}:{values['port']}"
        message = "scp -values=" + json.dumps(values)
        self.save_parameters()
        try:
            asyncio.run(self.send_message(uri, message))
        except Exception as e:
            self.response_text.insert(tk.END, f"Error when sending message: {e}\n")

    async def send_message(self, uri, message):
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)

            response = await websocket.recv()
            self.response_text.insert(tk.END, f"Response from server: {response}\n")

if __name__ == "__main__":
    app = CameraApp()
    app.mainloop()
