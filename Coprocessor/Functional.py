import os
import psutil
import platform
import cv2
import numpy as np
from Locater import Locater
import json
from apriltag import Detector
from constants import (APRIL_TAG_WIDTH, APRIL_TAG_HEIGHT,
                       HORIZONTAL_FOCAL_LENGTH, VERTICAL_FOCAL_LENGTH, CAMERA_HORIZONTAL_RESOLUTION_PIXELS,
                       CAMERA_VERTICAL_RESOLUTION_PIXELS, PROCESSING_SCALE, CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS,
                       CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS, cv2_props_dict)

"""
This file contains the FunctionalObject class which is used to create an object that can be used to interact with the
camera and the image processing functions. The class contains functions that can be called by the client to perform
various tasks such as capturing an image, processing an image, finding an object in an image, and setting camera
parameters. The class also contains a function to get the performance information of the Raspberry Pi. The class uses
the Locater class to locate objects in an image and the apriltag library to detect apriltags in an image. The class
also uses the cv2 library to capture images from the camera and perform image processing tasks. It is the core of the
coprocessor functionality. It can be safely edited by the user for custom functionality.
"""


def get_raspberry_pi_performance():
    """
    This function gets the performance information of the Raspberry Pi such as temperature, CPU usage, memory usage,
    disk usage, and system information.
    :return: a dictionary containing the performance information
    """

    # Get temperature
    temp_output = os.popen("vcgencmd measure_temp").readline()
    temp_value = temp_output.replace("temp=", "").replace("'C\n", "")

    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Get memory usage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    # Get disk usage
    disk_info = psutil.disk_usage('/')
    disk_usage = disk_info.percent

    # Get system information
    system_info = platform.uname()

    # Combine all information into a dictionary
    performance_info = {
        "temperature": float(temp_value),
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "system_info": {
            "system": system_info.system,
            "node_name": system_info.node,
            "release": system_info.release,
            "version": system_info.version,
            "machine": system_info.machine,
            "processor": system_info.processor
        }
    }

    return performance_info


# The following functions are used to convert the values received from the client to the correct data type. If the
# conversion fails, an error message is raised with the parameter name and value that caused the error. The functions
# are used in the FunctionalObject class to convert the values received from the client to the correct data type before
# using them in the functions of the class. They are simply used to provide intuitive error messages.

def json_we(value, name):
    try:
        return json.loads(value)
    except json.decoder.JSONDecodeError as e:
        raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to a JSON object.') from e


def float_we(value, name):
    try:
        return float(value)
    except ValueError as e:
        raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to a float.') from e


def int_we(value, name):
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to an integer.') from e


class FunctionalObject:
    def __init__(self, name):
        # This dictionary contains all the commands availible on the coprocessor. If you add a function, make sure to
        # add it to this dictionary.
        self.functionDict = {
            "processed_image": self.processed_image,
            "pi": self.processed_image,
            "raw_image": self.raw_image,
            "ri": self.raw_image,
            "switch_color": self.switch_color,
            "sc": self.switch_color,
            "save_params": self.save_params,
            "sp": self.save_params,
            "apriltag_image": self.apriltag_image,
            "ai": self.apriltag_image,
            "find_piece": self.find_piece,
            "fp": self.find_piece,
            "apriltag_headless": self.apriltag_headless,
            "at": self.apriltag_headless,
            "set_camera_params": self.set_camera_params,
            "scp": self.set_camera_params,
            "info": self.info,
        }
        self.detector = Detector()
        self.name = name

        # load the camera data from the JSON file
        try:
            with open('camera-params.json', 'r') as f:
                camera_params = json.load(f)
            self.horizontal_focal_length = camera_params[name]["horizontal_focal_length"]
            self.vertical_focal_length = camera_params[name]["vertical_focal_length"]
            self.camera_height = camera_params[name]["camera_height"]
            self.camera_horizontal_resolution_pixels = camera_params[name]["horizontal_resolution_pixels"]
            self.camera_vertical_resolution_pixels = camera_params[name]["vertical_resolution_pixels"]
            self.tilt_angle_radians = camera_params[name]["tilt_angle_radians"]
            self.horizontal_field_of_view = camera_params[name]["horizontal_field_of_view_radians"]
            self.vertical_field_of_view = camera_params[name]["vertical_field_of_view_radians"]
            self.processing_scale = camera_params[name]["processing_scale"]

        except json.JSONDecodeError:
            print("camera-params.json not found. Using default values.")
            self.horizontal_focal_length = HORIZONTAL_FOCAL_LENGTH
            self.vertical_focal_length = VERTICAL_FOCAL_LENGTH
            self.camera_height = 0
            self.camera_horizontal_resolution_pixels = CAMERA_HORIZONTAL_RESOLUTION_PIXELS
            self.camera_vertical_resolution_pixels = CAMERA_VERTICAL_RESOLUTION_PIXELS
            self.tilt_angle_radians = 0
            self.horizontal_field_of_view = CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS
            self.vertical_field_of_view = CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS
            self.processing_scale = PROCESSING_SCALE
            camera_params = {f"{name}": {"horizontal_focal_length": self.horizontal_focal_length,
                                         "vertical_focal_length": self.vertical_focal_length,
                                         "camera_height": self.camera_height,
                                         "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                                         "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                                         "tilt_angle_radians": self.tilt_angle_radians,
                                         "horizontal_field_of_view_radians": self.horizontal_field_of_view,
                                         "vertical_field_of_view_radians": self.vertical_field_of_view,
                                         "processing_scale": self.processing_scale}}
            with open('camera-params.json', 'w') as f:
                json.dump(camera_params, f, indent=4)
        except KeyError as e:
            print("Camera name not found in camera-params.json or params are invalid. Using default values.")
            print(e)
            self.horizontal_focal_length = HORIZONTAL_FOCAL_LENGTH
            self.vertical_focal_length = VERTICAL_FOCAL_LENGTH
            self.camera_height = 0
            self.camera_horizontal_resolution_pixels = CAMERA_HORIZONTAL_RESOLUTION_PIXELS
            self.camera_vertical_resolution_pixels = CAMERA_VERTICAL_RESOLUTION_PIXELS
            self.tilt_angle_radians = 0
            self.horizontal_field_of_view = CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS
            self.vertical_field_of_view = CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS
            self.processing_scale = PROCESSING_SCALE

            # Overwrite the parameters in the file with the defaults
            with open('camera-params.json', 'r') as f:
                camera_params = json.loads(f.read())
            camera_params[name] = {
                "horizontal_focal_length": self.horizontal_focal_length,
                "vertical_focal_length": self.vertical_focal_length,
                "camera_height": self.camera_height,
                "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                "tilt_angle_radians": self.tilt_angle_radians,
                "horizontal_field_of_view_radians": self.horizontal_field_of_view,
                "vertical_field_of_view_radians": self.vertical_field_of_view,
                "processing_scale": self.processing_scale
            }
            with open('camera-params.json', 'w') as f:
                json.dump(camera_params, f, indent=4)

        self.locater = Locater(self.camera_horizontal_resolution_pixels,
                               self.camera_vertical_resolution_pixels,
                               self.tilt_angle_radians, self.camera_height,
                               self.horizontal_field_of_view, self.vertical_field_of_view,
                               self.processing_scale)

        # Open the camera and check if it works. This code block can sometimes be beneficial for clearing the camera.
        temp_camera = cv2.VideoCapture(name)
        if temp_camera.isOpened():
            temp_camera.release()

        # Open the camera and check if it works
        self.camera = cv2.VideoCapture(name)
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Set the codec to MJPG,
        # as it is compatible with most cameras.
        cam_works, _ = self.camera.read()
        if not cam_works:
            print(f"Camera {name} not found.")
        self.name = name

    async def processed_image(self, websocket):
        """
        This function captures an image from the camera, attempts to detect a piece in it, and returns an image with
        overlayed lines and crosshairs to show the detected piece.
        :param websocket:
        :return:
        """
        ret, frame = self.camera.read()
        if not ret:
            self.camera.release()
            self.camera = cv2.VideoCapture(self.name)
            await websocket.send("Failed to capture image")
            return

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize the image to the processing scale to speed up processing
        img = cv2.resize(img, (self.camera_horizontal_resolution_pixels // self.processing_scale,
                               self.camera_vertical_resolution_pixels // self.processing_scale))
        img, _, _ = self.locater.locate(
            img)  # Locate the object in the image.
        image_array = np.asarray(
            img).flatten()
        await websocket.send(bytearray(image_array.tolist()))

    async def raw_image(self, websocket):
        """
        This function captures an image from the camera and sends it to the client. It does not do any processing.
        :param websocket:
        :return:
        """
        # Attempt to get a frame from the camera
        ret, frame = self.camera.read()
        if not ret:
            self.camera.release()
            self.camera = cv2.VideoCapture(self.name)
            await websocket.send('{"error": "Failed to capture image"}')
            return

        # Convert the frame to RGB for visualization and resize it to the processing scale
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.camera_horizontal_resolution_pixels // self.processing_scale,
                               self.camera_vertical_resolution_pixels // self.processing_scale))
        image_array = np.asarray(img).flatten()

        # Send the image to the client
        await websocket.send(bytearray(image_array.tolist()))

    def switch_color(self, new_color=0):
        """
        Change the active color in the Locater object.
        :param new_color:
        :return:
        """
        self.locater.active_color = min(int_we(new_color, "new_color"), len(self.locater.color_list) - 1)

    def save_params(self, values):
        """
        Save the color list and active color to a JSON file.
        :param values:
        :return:
        """
        # Get Values
        json_vals = json.loads(values)
        self.locater.color_list = json_vals[:-1]
        self.locater.active_color = json_vals[-1]

        # Save the color list to a JSON file
        with open('params.json', 'w') as f:
            json.dump(self.locater.color_list, f, indent=4)

    async def apriltag_image(self, websocket):
        """
        This function captures an image from the camera, detects AprilTags in the image, and returns the image with
        dots on the corners and center to show the detected AprilTags.
        :param websocket:
        :return:
        """
        # Capture an image frame
        ret, frame = self.camera.read()
        if not ret:
            self.camera.release()
            self.camera = cv2.VideoCapture(self.name)
            await websocket.send('{"error": "Failed to capture image"}')
            return

        # Convert the image to grayscale
        frame = cv2.resize(frame, (int(self.camera_horizontal_resolution_pixels / self.processing_scale),
                                   int(self.camera_vertical_resolution_pixels / self.processing_scale)))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags in the image
        tags = self.detector.detect(gray)

        # Convert the frame to RGB for visualization
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        for tag in tags:
            # Visualization
            cv2.circle(img, (int(tag["center"][0]), int(tag["center"][1])), 5, (255, 0, 0), -1)
            for corner in tag["corners"]:
                cv2.circle(img, (int(corner[0]), int(corner[1])), 3, (0, 255, 0), -1)

        image_array = np.asarray(img)

        await websocket.send(bytearray(image_array.tolist()))

    async def apriltag_headless(self, websocket):
        """
        This function captures an image from the camera, detects AprilTags in the image, and returns information
        about the detected AprilTags.
        :param websocket:
        :return:
        """

        # Capture an image frame
        ret, frame = self.camera.read()
        if not ret:
            self.camera.release()
            self.camera = cv2.VideoCapture(self.name)
            print("Failed to capture image")
            await websocket.send('{"error": "Failed to capture image"}')
            return

        # Convert the image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags in the image
        tags = self.detector.detect(gray)

        # Convert the frame to RGB for visualization
        tag_list = []

        for tag in tags:
            # Calculate distances using tag corners
            distance_horizontal = (APRIL_TAG_WIDTH * self.horizontal_focal_length) / np.linalg.norm(
                np.array(tag["corners"][0]) - np.array(tag["corners"][1]))
            distance_vertical = (APRIL_TAG_HEIGHT * self.vertical_focal_length) / np.linalg.norm(
                np.array(tag["corners"][1]) - np.array(tag["corners"][2]))
            distance_avg = (distance_horizontal + distance_vertical) / 2

            # Pose estimation to get the translation vector
            pose_R, pose_T, init_error, final_error = (
                self.detector.detection_pose(tag, [self.horizontal_focal_length,
                                                   self.vertical_focal_length,
                                                   self.camera_horizontal_resolution_pixels / 2,
                                                   self.camera_vertical_resolution_pixels / 2],
                                             APRIL_TAG_WIDTH))
            euler_angles = cv2.Rodrigues(pose_R)[0].flatten()

            # Calculate the direction to the tag
            horizontal_correspondant = (np.tan(self.horizontal_field_of_view / 2.0) /
                                       (self.camera_horizontal_resolution_pixels / 2.0))

            angle_radians_horiz = ((tag["center"][1] * horizontal_correspondant) -
                                   self.horizontal_field_of_view * 0.5)

            vertical_correspondant = (np.tan(self.vertical_field_of_view / 2.0) /
                                        (self.camera_vertical_resolution_pixels / 2.0))
            max_vertical_angle = self.camera_vertical_resolution_pixels / self.processing_scale * vertical_correspondant

            angle_radians_vert = ((max_vertical_angle - tag["center"][0] * (np.tan(self.vertical_field_of_view / 2.0) /
                                     (self.camera_vertical_resolution_pixels / 2.0))) +
                                  self.tilt_angle_radians - self.vertical_field_of_view * 0.5)

            tag_list.append(
                {"tag_id": tag["tag_id"], "position": pose_T.flatten().tolist(), "orientation": euler_angles.tolist(),
                 "distance": distance_avg, "horizontal_angle": angle_radians_horiz, "vertical_angle": angle_radians_vert})

        await websocket.send(json.dumps(tag_list))

    async def find_piece(self, websocket):
        """
        This function captures an image from the camera, attempts to detect a piece in it, and returns the distance and
        angle to the detected piece. It assumes that the piece is on the ground.
        :param websocket:
        :return:
        """
        ret, frame = self.camera.read()
        if not ret:
            self.camera.release()
            self.camera = cv2.VideoCapture(self.name)
            print("Failed to capture image")
            await websocket.send('{"error": "Failed to capture image"}')
            return
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.camera_horizontal_resolution_pixels // self.processing_scale,
                               self.camera_vertical_resolution_pixels // self.processing_scale))
        _, center, width = self.locater.locate_stripped(
            img)  # Locate the object in the image. Comment out this line if you don't want to process the image.
        if width == -1:
            await websocket.send("{distance: -1,\n angle: -1}")
        else:
            dist, angle = self.locater.loc_from_center(center)
            await websocket.send("{distance: " + str(dist) + ",\n angle: " + str(angle) + "}")

    async def set_camera_params(self, websocket, values):
        print(values)
        json_vals = json.loads(values)
        try:
            self.horizontal_focal_length = json_vals["horizontal_focal_length"]
            self.vertical_focal_length = json_vals["vertical_focal_length"]

        except KeyError:
            try:
                json_vals["horizontal_focal_length"] = ((json_vals["horizontal_resolution_pixels"] / 2)
                                                        / np.tan(json_vals["horizontal_field_of_view_radians"] / 2))
                json_vals["vertical_focal_length"] = ((json_vals["vertical_resolution_pixels"] / 2)
                                                      / np.tan(json_vals["vertical_field_of_view_radians"] / 2))
            except KeyError:
                pass

        values_dict = {
            "horizontal_focal_length": self.horizontal_focal_length,
            "vertical_focal_length": self.vertical_focal_length,
            "height": self.camera_height,
            "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
            "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
            "tilt_angle_radians": self.tilt_angle_radians,
            "horizontal_field_of_view_radians": self.horizontal_field_of_view,
            "vertical_field_of_view_radians": self.vertical_field_of_view,
            "processing_scale": self.processing_scale
        }

        for key, value in values_dict.items():
            try:
                value = json_vals[key]
            except KeyError:
                pass

        self.horizontal_focal_length = float_we(values_dict["horizontal_focal_length"], "horizontal_focal_length")
        self.vertical_focal_length = float_we(values_dict["vertical_focal_length"], "vertical_focal_length")
        self.camera_height = float_we(values_dict["height"], "height")
        self.camera_horizontal_resolution_pixels = int_we(values_dict["horizontal_resolution_pixels"],
                                                          "horizontal_resolution_pixels")
        self.camera_vertical_resolution_pixels = int_we(values_dict["vertical_resolution_pixels"],
                                                        "vertical_resolution_pixels")
        self.tilt_angle_radians = float_we(values_dict["tilt_angle_radians"], "tilt_angle_radians")
        self.horizontal_field_of_view = float_we(values_dict["horizontal_field_of_view_radians"],
                                                 "horizontal_field_of_view_radians")
        self.vertical_field_of_view = float_we(values_dict["vertical_field_of_view_radians"],
                                               "vertical_field_of_view_radians")
        self.processing_scale = int_we(values_dict["processing_scale"], "processing_scale")

        try:
            params_list = [[key, value] for key, value in json.loads(json_vals["additional_flags"]).items()]
            for param in params_list:
                self.camera.set(cv2_props_dict[param[0]], int_we(param[1], param[0]))

        except KeyError as e:
            await websocket.send('{"error": "Failed to capture image due to KeyError ' + str(e) + '"}')
            return
        except Exception as e:
            if "Expecting value" in str(e):
                pass
            else:
                await websocket.send('{"error": ' + str(e) + '}')
                return

        with open('camera-params.json', 'w') as f:
            json.dump(values_dict, f, indent=4)
        await self.info(websocket)

    async def info(self, websocket, h=False):
        info_dict = {
            "cam_name": self.name,
            "horizontal_focal_length": self.horizontal_focal_length,
            "vertical_focal_length": self.vertical_focal_length,
            "height": self.camera_height,
            "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
            "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
            "processing_scale": self.processing_scale,
            "tilt_angle_radians": self.tilt_angle_radians,
            "horizontal_field_of_view_radians": self.horizontal_field_of_view,
            "vertical_field_of_view_radians": self.vertical_field_of_view,
            "color_list": self.locater.color_list,
            "active_color": self.locater.active_color
        }

        hardware = get_raspberry_pi_performance()

        if h:
            await websocket.send(json.dumps(hardware))
        else:
            await websocket.send(json.dumps(info_dict))

    def __del__(self):
        # Cleanup code
        if self.camera.isOpened():
            self.camera.release()
        del self
