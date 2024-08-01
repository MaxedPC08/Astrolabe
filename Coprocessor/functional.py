import time

import cv2
import numpy as np
from Locater import Locater
import json
from apriltag import Detector
from constants import (APRIL_TAG_WIDTH, APRIL_TAG_HEIGHT,
                       HORIZONTAL_FOCAL_LENGTH, VERTICAL_FOCAL_LENGTH, CAMERA_HORIZONTAL_RESOLUTION_PIXELS,
                       CAMERA_VERTICAL_RESOLUTION_PIXELS, PROCESSING_SCALE)

class FunctionalObject:
    def __init__(self, name):
        self.functionDict = {
            "processed_image": self.processed_image,
            "pi": self.processed_image,
            "raw_image": self.raw_image,
            "ri": self.raw_image,
            "switch_color": self.switch_color,
            "sc": self.switch_color,
            "save_params": self.save_params,
            "sp": self.save_params,
            "apriltag": self.apriltag_image,
            "at": self.apriltag_image,
            "find_piece": self.find_piece,
        }
        print(name)
        self.locater = Locater()
        self.detector = Detector()
        self.camera = cv2.VideoCapture(name)
        self.name = name

        #load the camera data from the JSON file
        try:
            with open('camera-params.json', 'r') as f:
                camera_params = json.load(f)
            self.horizontal_focal_length = camera_params[name]["horizontal_focal_length"]
            self.vertical_focal_length = camera_params[name]["vertical_focal_length"]
            self.camera_height = camera_params[name]["camera_height"]
            self.camera_horizontal_resolution_pixels = camera_params[name]["camera_horizontal_resolution_pixels"]
            self.camera_vertical_resolution_pixels = camera_params[name]["camera_vertical_resolution_pixels"]
            self.tilt_angle_radians = camera_params[name]["tilt_angle_radians"]

        except FileNotFoundError:
            print("camera-params.json not found. Using default values.")
            self.horizontal_focal_length = HORIZONTAL_FOCAL_LENGTH
            self.vertical_focal_length = VERTICAL_FOCAL_LENGTH
            self.camera_height = 0
            self.camera_horizontal_resolution_pixels = CAMERA_HORIZONTAL_RESOLUTION_PIXELS
            self.camera_vertical_resolution_pixels = CAMERA_VERTICAL_RESOLUTION_PIXELS
            self.tilt_angle_radians = 0
            camera_params = {f"{name}": {"horizontal_focal_length": self.horizontal_focal_length,
                                            "vertical_focal_length": self.vertical_focal_length,
                                            "camera_height": self.camera_height,
                                            "camera_horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                                            "camera_vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                                            "tilt_angle_radians": self.tilt_angle_radians}}
            with open('camera-params.json', 'w') as f:
                json.dump(camera_params, f, indent=4)
        except KeyError:
            print("Camera name not found in camera-params.json or params are invalid. Using default values.")
            self.horizontal_focal_length = HORIZONTAL_FOCAL_LENGTH
            self.vertical_focal_length = VERTICAL_FOCAL_LENGTH
            self.camera_height = 0
            self.camera_horizontal_resolution_pixels = CAMERA_HORIZONTAL_RESOLUTION_PIXELS
            self.camera_vertical_resolution_pixels = CAMERA_VERTICAL_RESOLUTION_PIXELS
            self.tilt_angle_radians = 0

    def int_we(self, value, name):
        try:
            return int(value)
        except ValueError as e:
            raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to an integer.') from e

    def float_we(self, value, name):
        try:
            return float(value)
        except ValueError as e:
            raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to a float.') from e

    def json_we(self, value, name):
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError as e:
            raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to a JSON object.') from e

    async def processed_image(self, websocket):
        img = cv2.cvtColor(self.camera.read()[1], cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (160, 120))
        img, center, width = self.locater.locate(img)  # Locate the object in the image. Comment out this line if you don't want to process the image.
        # loc_from_center(center, width)
        image_array = np.asarray(img).flatten()  # You can adjust this if you want to get the center and width of the object
        await websocket.send(image_array.tobytes())


    async def raw_image(self, websocket):
        img = cv2.cvtColor(self.camera.read()[1], cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (160, 120))
        image_array = np.asarray(img).flatten()
        await websocket.send(image_array.tobytes())

    def switch_color(self, new_color=0):
        print(new_color)
        self.locater.active_color = min(self.int_we(new_color, "new_color"), len(self.locater.color_list) - 1)

    def save_params(self, values):
        json_vals = json.loads(values)
        self.locater.color_list = json_vals[:-1]
        self.locater.active_color = json_vals[-1]
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, int(self.locater.color_list[self.locater.active_color]["brightness"]))
        self.camera.set(cv2.CAP_PROP_CONTRAST, int(self.locater.color_list[self.locater.active_color]["contrast"]))
        with open('params.json', 'w') as f:
            json.dump(self.locater.color_list, f, indent=4)

    async def apriltag_image(self, websocket):
        # Capture an image frame
        ret, frame = self.camera.read()
        if not ret:
            print("Failed to capture image")
            return

        # Convert the image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags in the image
        tags = self.detector.detect(gray)

        # Convert the frame to RGB for visualization
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        for tag in tags:
            # Calculate distances using tag corners
            distance_horizontal = (APRIL_TAG_WIDTH * self.horizontal_focal_length) / np.linalg.norm(np.array(tag["corners"][0]) - np.array(tag["corners"][1]))
            distance_vertical = (APRIL_TAG_HEIGHT * self.vertical_focal_length) / np.linalg.norm(np.array(tag["corners"][1]) - np.array(tag["corners"][2]))
            distance_avg = (distance_horizontal + distance_vertical) / 2

            # Pose estimation to get the translation vector
            pose_R, pose_T, init_error, final_error = self.detector.detection_pose(tag, [self.horizontal_focal_length,
                                                                                    self.vertical_focal_length,
                                                                                    self.camera_horizontal_resolution_pixels / 2,
                                                                                    self.camera_vertical_resolution_pixels / 2],
                                                                              APRIL_TAG_WIDTH)
            euler_angles = cv2.Rodrigues(pose_R)[0].flatten()

            print(f"Position: {pose_T.flatten()}")
            print(f"Orientation (Euler angles in radians): {euler_angles}")

            # Visualization
            cv2.circle(img, (int(tag["center"][0]), int(tag["center"][1])), 5, (255, 0, 0), -1)
            for corner in tag["corners"]:
                cv2.circle(img, (int(corner[0]), int(corner[1])), 3, (0, 255, 0), -1)

            text_position = (int(tag["center"][0]), int(tag["center"][1]) + 20)
            distance_text = f"{distance_avg:.2f} units"
            angle_text = f"Angle: {np.round(euler_angles, 2)}°"

            cv2.putText(img, distance_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(img, angle_text, (text_position[0], text_position[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        img = cv2.resize(img, (int(self.camera_horizontal_resolution_pixels / PROCESSING_SCALE),
                               int(self.camera_vertical_resolution_pixels / PROCESSING_SCALE)))
        image_array = np.asarray(img)

        await websocket.send(image_array.tobytes())

    async def find_piece(self, websocket):
        img = cv2.cvtColor(self.camera.read()[1], cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (160, 120))
        _, center, width = self.locater.locate_stripped(img)  # Locate the object in the image. Comment out this line if you don't want to process the image.
        if width==-1:
            await websocket.send("{distance: -1,\n angle: -1}")
        else:
            dist, angle = self.locater.loc_from_center(center)
            await websocket.send("{distance: " + str(dist) + ",\n angle: " + str(angle) + "}")

    async def set_camera_params(self, websocket, values):
        json_vals = json.loads(values)
        self.horizontal_focal_length = json_vals["horizontal_focal_length"]
        self.vertical_focal_length = json_vals["vertical_focal_length"]
        self.camera_height = json_vals["camera_height"]
        self.camera_horizontal_resolution_pixels = json_vals["camera_horizontal_resolution_pixels"]
        self.camera_vertical_resolution_pixels = json_vals["camera_vertical_resolution_pixels"]
        self.tilt_angle_radians = json_vals["tilt_angle_radians"]
        camera_params = {f"{self.name}": {"horizontal_focal_length": self.horizontal_focal_length,
                                          "vertical_focal_length": self.vertical_focal_length,
                                          "camera_height": self.camera_height,
                                          "camera_horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                                          "camera_vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                                          "tilt_angle_radians": self.tilt_angle_radians}}
        with open('camera-params.json', 'w') as f:
            json.dump(camera_params, f, indent=4)
        await websocket.send("Camera parameters set successfully.")

    def __del__(self):
        # Cleanup code
        if self.camera.isOpened():
            self.camera.release()
        print(f"FunctionalObject {self.name} has been deleted")
        del self


