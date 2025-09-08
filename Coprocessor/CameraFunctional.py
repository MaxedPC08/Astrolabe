import base64
from fileinput import filename
import os
import time
import cv2
import numpy as np
from Locater import Locater
import json
import base64
from apriltag import Detector, DetectorOptions
from constants import (APRIL_TAG_WIDTH, APRIL_TAG_HEIGHT,
                       HORIZONTAL_FOCAL_LENGTH, VERTICAL_FOCAL_LENGTH, CAMERA_HORIZONTAL_RESOLUTION_PIXELS,
                       CAMERA_VERTICAL_RESOLUTION_PIXELS, DOWNSCALE_FACTOR, CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS,
                       CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS, CAMERA_HEIGHT, RECORD, cv2_props_dict)

"""
This file contains the FunctionalObject class which is used to create an object that can be used to interact with the
camera and the image processing functions. The class contains functions that can be called by the client to perform
various tasks such as capturing an image, processing an image, finding an object in an image, and setting camera
parameters. The class also contains a function to get the performance information of the Raspberry Pi. The class uses
the Locater class to locate objects in an image and the apriltag library to detect apriltags in an image. The class
also uses the cv2 library to capture images from the camera and perform image processing tasks. It is the core of the
coprocessor functionality. It can be safely edited by the user for custom functionality.
"""
def encode_image_for_websocket(image_path, format="png"):
    # Read the image
    img = cv2.imread(image_path)
    
    # Encode the image to PNG or JPEG bytes
    if format.lower() == "png":
        _, img_encoded = cv2.imencode('.png', img)
    else:
        # For JPEG, can specify quality (0-100)
        _, img_encoded = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    
    # Convert to base64 string
    base64_string = base64.b64encode(img_encoded).decode('utf-8')
    
    # Create a message with metadata
    message = {
        "image": base64_string,
        "format": format,
        "width": img.shape[1],
        "height": img.shape[0]
    }
    
    # Convert to JSON string for sending
    return json.dumps(message)

def draw_image_to_record(image, text=None, color=None):
    if not color:
        color = (255, 255, 255)
    height, width = image.shape[:2]
    rect_height = int(height * 0.1)
    # Make the image taller and add a colored rectangle above the original image without covering it
    new_height = height + rect_height
    new_image = np.zeros((new_height, width, 3), dtype=image.dtype)
    # Fill the top rectangle with the color
    new_image[0:rect_height, :, :] = color
    # Copy the original image below the rectangle
    new_image[rect_height:, :, :] = image

    if text:
        font_scale = 1.0
        thickness = 2
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = 10
        text_y = rect_height // 2 + text_size[1] // 2
        cv2.putText(new_image, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
    return new_image


# The following functions are used to convert the values received from the client to the correct data type. If the
# conversion fails, an error message is raised with the parameter name and value that caused the error. The functions
# are used in the FunctionalObject class to convert the values received from the client to the correct data type before
# using them in the functions of the class. They are simply used to provide intuitive error messages.

def get_with_type(d, key, default=None, expected_type=int):
    # Basically dictionary.get but enforces types
    value = d.get(key, default)
    return value if isinstance(value, expected_type) else default

def json_we(value, name):
    try:
        return json.loads(value)
    except json.decoder.JSONDecodeError as e:
        raise ValueError(f'Error: Could not convert parameter "{name}" with value "{value}" to a JSON object.') from e


def float_we(value, name):
    try:
        return float(value)
    except ValueError as e:
        raise ValueError(f'Error: Could not convert parameter "{name}" with value "{value}" to a float.') from e


def int_we(value, name):
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f'Error: Could not convert parameter "{name}" with value "{value}" to an integer.') from e
    
def bool_we(value, name):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ['true', '1']:
            return True
        elif value.lower() in ['false', '0']:
            return False
    raise ValueError(f'Error: Could not convert parameter "{name}" with value "{value}" to a boolean.')


def l3_preprocess(image, **kwargs):
    # TODO: make stuff scale to image size
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=get_with_type(kwargs, "clahe_clip_limit", 3), 
        tileGridSize=(get_with_type(kwargs, "clahe_tile_size", 8), get_with_type(kwargs, "clahe_tile_size", 8)))
    enhanced = clahe.apply(gray_image)

    edges = cv2.Canny(gray_image, 
        get_with_type(kwargs, "canny_threshold_1", 50), get_with_type(kwargs, "canny_threshold_1", 150))
    kernel = np.ones([get_with_type(kwargs, "edge_refinement_kernel_size", 3), 
        get_with_type(kwargs, "edge_refinement_kernel_size", 3)], np.uint8)
    dilated = cv2.dilate(edges, kernel, 1)

    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=1)

    thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 35,3)

    highlighted = cv2.bitwise_and(thresh, thresh, closed)
    return highlighted

def l2_preprocess(image, **kwargs):
    # TODO: make stuff scale to image size
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray_image, 
        get_with_type(kwargs, "canny_threshold_1", 50), get_with_type(kwargs, "canny_threshold_1", 150))
    kernel = np.ones([get_with_type(kwargs, "edge_refinement_kernel_size", 3), 
        get_with_type(kwargs, "edge_refinement_kernel_size", 3)], np.uint8)
    dilated = cv2.dilate(edges, kernel, 1)

    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=1)

    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 
        get_with_type(kwargs, "threshold_block_size", 35), get_with_type(kwargs, "threshold_offset", 3))

    highlighted = cv2.bitwise_and(thresh, thresh, closed)
    return highlighted


def l1_preprocess(image, **kwargs):
    # TODO: make stuff scale to image size
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 
        get_with_type(kwargs, "threshold_block_size", 35), get_with_type(kwargs, "threshold_offset", 3))

    highlighted = cv2.bitwise_and(thresh, thresh, gray_image)
    return highlighted

class CameraFunctionalObject:

    """
    TODO: Implement new naming convention on all functions -----
    TODO: Consolidate VP functions into one -----
    TODO: Further optimize combined VP funcitons
    TODO: Truely implement testing mode
    TODO: Implement Scaling
    TODO: Implement time for Apriltag
    """
    def __init__(self, name, serial_number, host_data=None):
        # This dictionary contains all the commands availible on the coprocessor. If you add a function, make sure to
        # add it to this dictionary.
        self.function_dict = {
            "raw": self.raw,
            "switch_color": self.switch_color,
            "save_color": self.save_color,
            "add_color": self.add_color,
            "delete_color": self.delete_color,
            "set_camera_params": self.set_camera_params,
            "piece": self.piece,
            "apriltag": self.apriltag,
            "info": self.info,
            "function_info": self.function_info,
        }

        self.name = name

        options = DetectorOptions(refine_edges=False)
        self.detector = Detector(options=options)
        self.name = name
        self.serial_number = serial_number
        self.previous_image = None
        self.previous_image_information = None
        self.previous_image_color = None

        temp_camera = cv2.VideoCapture(name)
        if temp_camera.isOpened():
            temp_camera.release()
            

        # Open the camera and check if it works
        self.camera = cv2.VideoCapture(name)
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Set the codec to MJPG,
        # as it is compatible with most cameras.
        cam_works, _ = self.get_image()
        if not cam_works:
            print(f"Camera {name} not found.")
        
        # load the camera data from the JSON file
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, ".cache", "camera-params.json")
            with open(data_path, 'r') as f:
                camera_params = json.load(f)
            self.horizontal_focal_length = max(camera_params[serial_number]["horizontal_focal_length"], 0)
            self.vertical_focal_length = max(camera_params[serial_number]["vertical_focal_length"], 0)
            self.camera_height = max(camera_params[serial_number]["camera_height"], 0)
            self.camera_horizontal_resolution_pixels = max(camera_params[serial_number]["horizontal_resolution_pixels"], 1)
            self.camera_vertical_resolution_pixels = max(camera_params[serial_number]["vertical_resolution_pixels"], 1)
            self.tilt_angle_radians = camera_params[serial_number]["tilt_angle_radians"]
            self.horizontal_field_of_view = max(camera_params[serial_number]["horizontal_field_of_view_radians"], 0)
            self.vertical_field_of_view = max(camera_params[serial_number]["vertical_field_of_view_radians"], 0)
            self.downscale_factor = max(camera_params[serial_number]["downscale_factor"], 1)
            self.record = bool(camera_params[serial_number]["record"])

            for key in cv2_props_dict:
                try:
                    self.camera.set(cv2_props_dict[key], int_we(camera_params[serial_number][key], key))
                except KeyError:
                    pass

        except KeyError as e:
            print("Camera name not found in camera-params.json or params are invalid. Using default values.")
            print(e)
            self.horizontal_focal_length = HORIZONTAL_FOCAL_LENGTH
            self.vertical_focal_length = VERTICAL_FOCAL_LENGTH
            self.camera_height = CAMERA_HEIGHT
            self.camera_horizontal_resolution_pixels = CAMERA_HORIZONTAL_RESOLUTION_PIXELS
            self.camera_vertical_resolution_pixels = CAMERA_VERTICAL_RESOLUTION_PIXELS
            self.tilt_angle_radians = 0
            self.horizontal_field_of_view = CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS
            self.vertical_field_of_view = CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS
            self.downscale_factor = DOWNSCALE_FACTOR
            self.record = RECORD

            # Overwrite the parameters in the file with the defaults
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, ".cache", "camera-params.json")
            with open(data_path, 'r') as f:
                camera_params = json.load(f)
            camera_params[serial_number] = {
                "horizontal_focal_length": self.horizontal_focal_length,
                "vertical_focal_length": self.vertical_focal_length,
                "camera_height": self.camera_height,
                "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                "tilt_angle_radians": self.tilt_angle_radians,
                "horizontal_field_of_view_radians": self.horizontal_field_of_view,
                "vertical_field_of_view_radians": self.vertical_field_of_view,
                "downscale_factor": self.downscale_factor,
                "record": self.record
            }
            with open(data_path, 'w') as f:
                json.dump(camera_params, f, indent=4)

        except:
            self.horizontal_focal_length = HORIZONTAL_FOCAL_LENGTH
            self.vertical_focal_length = VERTICAL_FOCAL_LENGTH
            self.camera_height = CAMERA_HEIGHT
            self.camera_horizontal_resolution_pixels = CAMERA_HORIZONTAL_RESOLUTION_PIXELS
            self.camera_vertical_resolution_pixels = CAMERA_VERTICAL_RESOLUTION_PIXELS
            self.tilt_angle_radians = 0
            self.horizontal_field_of_view = CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS
            self.vertical_field_of_view = CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS
            self.downscale_factor = DOWNSCALE_FACTOR
            self.record = RECORD
            camera_params = {f"{serial_number}": {"horizontal_focal_length": self.horizontal_focal_length,
                                         "vertical_focal_length": self.vertical_focal_length,
                                         "camera_height": self.camera_height,
                                         "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                                         "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                                         "tilt_angle_radians": self.tilt_angle_radians,
                                         "horizontal_field_of_view_radians": self.horizontal_field_of_view,
                                         "vertical_field_of_view_radians": self.vertical_field_of_view,
                                         "downscale_factor": self.downscale_factor}}
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, ".cache", "camera-params.json")
            with open(data_path, 'w') as f:
                json.dump(camera_params, f, indent=4)

        self.locater = Locater(self.camera_horizontal_resolution_pixels,
                               self.camera_vertical_resolution_pixels,
                               self.tilt_angle_radians, self.camera_height,
                               self.horizontal_field_of_view, self.vertical_field_of_view)
        
        if self.record:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # or 'XVID', 'MJPG', etc.
            video_filename = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                ".saves",
                f"{self.serial_number}", 
                f"{time.strftime('%Y%m%d_%H-%M-%S')}.avi"
            )
            video_dir = os.path.dirname(video_filename)
            os.makedirs(video_dir, exist_ok=True)

            self.video_writer = cv2.VideoWriter(
                video_filename,
                fourcc,
                20.0,  # FPS
                (self.camera_horizontal_resolution_pixels, 
                 self.camera_vertical_resolution_pixels + int(self.camera_vertical_resolution_pixels * 0.1))
            )
            if not self.video_writer.isOpened():
                raise RuntimeError(f"Could not open video writer for {video_filename}. Check permissions or path.") 
    
    def get_image(self, rec_level=0):
        if self.name == -1:
            return True, cv2.imread("Coprocessor/images/resized_IMG_20250515_204201.jpg")
        
        ret, frame = self.camera.read()
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            if rec_level <= 2:
                self.camera.release()
                time.sleep(2)
                self.camera = cv2.VideoCapture(self.name)
                return self.get_image(rec_level+1)
            return None, None

        if not ret:
            self.camera.release()
            self.camera = cv2.VideoCapture(self.name)
            return None, None

        return (ret, frame)
    
    def save_frame(self, frame, text, color):
        """
        Saves a frame to the video writer with a text overlay.
        :param frame: The frame to save.
        :param text: The text to overlay on the frame.
        :param color: The color of the text overlay.
        """
        if self.record:
            try:
                frame_to_write = cv2.cvtColor(draw_image_to_record(frame, text=text, color=color), cv2.COLOR_RGB2BGR)
                self.video_writer.write(frame_to_write)
            except Exception as e:
                print(f"Error writing to video file: {e}")
    
    
    async def report_no_cams(self, websocket):
        await websocket.send('{"error":"This function is not availible when no camera is detected."}')

    async def raw(self, websocket, quality=0.9, **kwargs):
        """
        This function captures an image from the camera and sends it to the client. It does not do any processing.
        :param websocket:
        :return:
        """
        # Attempt to get a frame from the camera
        ret, frame = self.get_image()
        if not ret:

            await websocket.send('{"error": "Failed to capture image"}')
            return

        # Convert the frame to RGB for visualization and resize it to the processing scale
        try:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #img = cv2.resize(img, (self.camera_horizontal_resolution_pixels // self.processing_scale,
            #                       self.camera_vertical_resolution_pixels // self.processing_scale))
        except Exception as e:
            await websocket.send('{"error": "' + str(e) + '"}')
            return
        
        img = cv2.resize(img, (img.shape[1] // self.downscale_factor, img.shape[0] // self.downscale_factor))
        image_array = np.asarray(img)
        if self.record:
            self.save_frame(frame, text="Raw Image", color=(255, 255, 255))

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality*100)]
        _, encoded_img = cv2.imencode('.jpg', image_array, encode_param)
    
        jpg_string = base64.b64encode(encoded_img).decode('utf-8')
        

        # Send the image to the client
        await websocket.send(json.dumps({"image_string":jpg_string}))

    async def apriltag(self, websocket, return_image=False, preprocessing_mode="3", quality=0.9, preprocessor_parameters="{}", **kwargs):
        """
        This function captures an image from the camera, detects AprilTags in the image, and returns the image with
        dots on the corners and center to show the detected AprilTags.
        :param websocket:
        :return:
        """
        # Capture an image frame
        ret, frame = self.get_image()
        if not ret:

            await websocket.send('{"error": "Failed to capture image"}')
            return
        print(frame.shape)
        # TODO: Do the processingscale thing
        # frame = cv2.resize(frame, (int(self.camera_horizontal_resolution_pixels / self.processing_scale),
        #                           int(self.camera_vertical_resolution_pixels / self.processing_scale)))
        
        processed_image = None
        if preprocessing_mode == "0":
            processed_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif preprocessing_mode == "1":
            processed_image = l1_preprocess(frame)
        elif preprocessing_mode == "2":
            processed_image = l2_preprocess(frame)
        elif preprocessing_mode == "3":
            processed_image = l3_preprocess(frame)
            
        # Detect AprilTags in the image
        tags = self.detector.detect(processed_image)

        # Convert the frame to RGB for visualization
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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

            angle_radians_horiz = ((tag["center"][0] * horizontal_correspondant) -
                                   self.horizontal_field_of_view * 0.5)

            vertical_correspondant = (np.tan(self.vertical_field_of_view / 2.0) /
                                        (self.camera_vertical_resolution_pixels / 2.0))
            max_vertical_angle = self.camera_vertical_resolution_pixels * vertical_correspondant

            angle_radians_vert = ((max_vertical_angle - tag["center"][1] * (np.tan(self.vertical_field_of_view / 2.0) /
                                     (self.camera_vertical_resolution_pixels / 2.0))) +
                                  self.tilt_angle_radians - self.vertical_field_of_view * 0.5)

            tag_list.append(
                {"tag_id": tag["tag_id"], "position": pose_T.flatten().tolist(), "orientation": euler_angles.tolist(),
                 "distance": distance_avg, "horizontal_angle": angle_radians_horiz, "vertical_angle": -angle_radians_vert}) # TODO: Add Time
        
        data = {"tags": tag_list}

        if return_image:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (img.shape[1] // self.downscale_factor, img.shape[0] // self.downscale_factor))

            for tag in tags:
                # Visualization
                cv2.circle(img, (int(tag["center"][0]), int(tag["center"][1])), 5, (255, 0, 0), -1)
                for corner in tag["corners"]:
                    cv2.circle(img, (int(corner[0]), int(corner[1])), 3, (0, 255, 0), -1)

            image_array = np.asarray(img)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality*100)]
            _, encoded_img = cv2.imencode('.jpg', image_array, encode_param)
        
            jpg_string = base64.b64encode(encoded_img).decode('utf-8')
            
            data["image_string"] = jpg_string

        

        await websocket.send(json.dumps(data))

    async def switch_color(self, websocket, new_color=0):
        """
        Change the active color in the Locater object.
        :param new_color:
        :return:
        """
        try:
            self.locater.active_color = min(int_we(new_color, "new_color"), len(self.locater.color_list) - 1)
        except Exception as e:
            await websocket.send('{"error": "' + str(e) + '"}')
            return
        await self.info(websocket)

    async def save_color(self, websocket, red, blue, green, difference, blur, **kwargs):
        """
        Save the color list and active color to a JSON file.
        :param values:
        :return:
        """
        try:
            # Validate required keys and convert to int
            red = int_we(red)
            blue = int_we(blue)
            green = int_we(green)
            difference = int_we(difference)
            blur = int_we(blur)

            color = {
                "red": red,
                "blue": blue,
                "green": green,
                "difference": difference,
                "blur": blur
            }
            
            self.locater.color_list[self.locater.active_color] = color

            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, ".cache", "params.json")
            with open(data_path, 'w') as f:
                json.dump(self.locater.color_list, f, indent=4)
        except Exception as e:
            await websocket.send('{"error": ' + str(e) + '}')
            return
        
        await self.info(websocket)
    
    async def add_color(self, websocket, red, blue, green, difference, blur, **kwargs):
        """
        Save the color list and active color to a JSON file.
        :param values:
        :return:
        """
        try:
            print(red, green, blue)
            # Validate required keys and convert to int
            red = int_we(red, "red")
            blue = int_we(blue, "blue")
            green = int_we(green, "green")
            difference = int_we(difference, "difference")
            blur = int_we(blur, "blur")

            color = {
                "red": red,
                "blue": blue,
                "green": green,
                "difference": difference,
                "blur": blur
            }

            if len(self.locater.color_list) >=11:
                await websocket.send('{"error": "Color list is full. Please delete a color before adding a new one."}')
                return
            self.locater.color_list.append(color)

            # Save the color list to a JSON file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, ".cache", "params.json")
            with open(data_path, 'w') as f:
                json.dump(self.locater.color_list, f, indent=4)
        except Exception as e:
            await websocket.send(json.dumps({"error":e}))
            return
        
        await self.info(websocket)

    async def delete_color(self, websocket, index, **kwargs):
        """
        Save the color list and active color to a JSON file.
        :param values:
        :return:
        """
        try:
            # Validate required keys and convert to int
            index = int_we(index)

            if 0 <= index < len(self.locater.color_list):
                del self.locater.color_list[index]
                self.locater.active_color = min(self.locater.active_color, len(self.locater.color_list) - 1)

            # Save the color list to a JSON file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, ".cache", "params.json")
            with open(data_path, 'w') as f:
                json.dump(self.locater.color_list, f, indent=4)
        except Exception as e:
            await websocket.send('{"error": ' + str(e) + '}')
            return

        await self.info(websocket)


    async def set_camera_params(self, websocket, **kwargs):
        if isinstance(kwargs, dict):
            json_vals = kwargs
        else:
            json_vals = json.loads(kwargs)
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
            "downscale_factor": self.downscale_factor, 
            "record": self.record
        }

        for key in values_dict.keys():
            try:
                if json_vals[key] == '':
                    continue
                values_dict[key] = json_vals[key]
            except KeyError:
                pass

        self.horizontal_focal_length = float_we(values_dict["horizontal_focal_length"], "horizontal_focal_length")
        self.vertical_focal_length = float_we(values_dict["vertical_focal_length"], "vertical_focal_length")
        self.camera_height = float_we(values_dict["height"], "height")
        self.camera_horizontal_resolution_pixels = max(int_we(values_dict["horizontal_resolution_pixels"],
                                                          "horizontal_resolution_pixels"), 1)
        self.camera_vertical_resolution_pixels = max(int_we(values_dict["vertical_resolution_pixels"],
                                                        "vertical_resolution_pixels"), 1)
        self.tilt_angle_radians = float_we(values_dict["tilt_angle_radians"], "tilt_angle_radians")
        self.horizontal_field_of_view = max(float_we(values_dict["horizontal_field_of_view_radians"],
                                                 "horizontal_field_of_view_radians"), 1)
        self.vertical_field_of_view = max(float_we(values_dict["vertical_field_of_view_radians"],
                                               "vertical_field_of_view_radians"), 1)
        self.downscale_factor = max(int_we(values_dict["downscale_factor"], "downscale_factor"), 1)

        previous_record = self.record
        self.record = bool_we(json_vals.get("record", RECORD), "record")

        if not previous_record and self.record:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # or 'XVID', 'MJPG', etc.
            video_filename = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                ".saves",
                f"{self.serial_number}", 
                f"{time.strftime('%Y%m%d_%H-%M-%S')}.avi"
            )
            video_dir = os.path.dirname(video_filename)
            os.makedirs(video_dir, exist_ok=True)

            self.video_writer = cv2.VideoWriter(
                video_filename,
                fourcc,
                20.0,  # FPS
                (self.camera_horizontal_resolution_pixels, 
                 self.camera_vertical_resolution_pixels + int(self.camera_vertical_resolution_pixels * 0.1))
            )
            if not self.video_writer.isOpened():
                raise RuntimeError(f"Could not open video writer for {video_filename}. Check permissions or path.") 

        new_params = {
                "horizontal_focal_length": self.horizontal_focal_length,
                "vertical_focal_length": self.vertical_focal_length,
                "camera_height": self.camera_height,
                "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                "tilt_angle_radians": self.tilt_angle_radians,
                "horizontal_field_of_view_radians": self.horizontal_field_of_view,
                "vertical_field_of_view_radians": self.vertical_field_of_view,
                "downscale_factor": self.downscale_factor,
                "record": self.record
            }

        for key in cv2_props_dict:
            try:
                if json_vals[key] == '':
                    continue
                self.camera.set(cv2_props_dict[key], float_we(json_vals[key], key))
                new_params[key] = float_we(json_vals[key], key)
            except KeyError:
                pass
        
        

        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, ".cache", "camera-params.json")
        with open(data_path, 'r') as f:
            camera_params = json.loads(f.read())

        try:
            camera_params[self.serial_number] = new_params
        except KeyError as e:
            print("Camera name not found in camera-params.json or params are invalid. Using default values.")
            self.horizontal_focal_length = HORIZONTAL_FOCAL_LENGTH
            self.vertical_focal_length = VERTICAL_FOCAL_LENGTH
            self.camera_height = CAMERA_HEIGHT
            self.camera_horizontal_resolution_pixels = CAMERA_HORIZONTAL_RESOLUTION_PIXELS
            self.camera_vertical_resolution_pixels = CAMERA_VERTICAL_RESOLUTION_PIXELS
            self.tilt_angle_radians = 0
            self.horizontal_field_of_view = CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS
            self.vertical_field_of_view = CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS
            self.downscale_factor = DOWNSCALE_FACTOR
            self.record = RECORD

            # Overwrite the parameters in the file with the defaults
            with open(data_path, 'r') as f:
                camera_params = json.loads(f.read())
            camera_params[self.serial_number] = {
                "horizontal_focal_length": self.horizontal_focal_length,
                "vertical_focal_length": self.vertical_focal_length,
                "camera_height": self.camera_height,
                "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
                "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
                "tilt_angle_radians": self.tilt_angle_radians,
                "horizontal_field_of_view_radians": self.horizontal_field_of_view,
                "vertical_field_of_view_radians": self.vertical_field_of_view,
                "downscale_factor": self.downscale_factor,
                "record": self.record
            }
            websocket.send("Camera name not found in camera-params.json or params are invalid. Using default values.")
        with open(data_path, 'w') as f:
            json.dump(camera_params, f, indent=4)

        self.locater = Locater(self.camera_horizontal_resolution_pixels,
                               self.camera_vertical_resolution_pixels,
                               self.tilt_angle_radians, self.camera_height,
                               self.horizontal_field_of_view, self.vertical_field_of_view)

        await self.info(websocket)


    async def piece(self, websocket, return_image=False, quality=0.9, **kwargs):
        """
        This function captures an image from the camera, attempts to detect a piece in it, and returns the distance and
        angle to the detected piece. It assumes that the piece is on the ground.
        :param websocket:
        :return:
        """
        ret, frame = self.get_image()
        if not ret:

            await websocket.send('{"error": "Failed to capture image"}')
            return
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out_image = center = width = coefficient = jpg_string = None
        if return_image or self.record:
            out_image, center, width, coefficient = self.locater.locate(
                img)
            
            if return_image:
                out_image = cv2.resize(out_image, (out_image.shape[1] // self.downscale_factor, out_image.shape[0] // self.downscale_factor))

                image_array = np.asarray(out_image)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality*100)]
                _, encoded_img = cv2.imencode('.jpg', image_array, encode_param)
            
                jpg_string = base64.b64encode(encoded_img).decode('utf-8')
            
            if self.record:
                center_percent = (center[0] / out_image.shape[1] * 100, center[1] / out_image.shape[0] * 100)
                width_percent = width / out_image.shape[1] * 100

                self.save_frame(out_image,
                        text=f"Piece Detection. \nCenter: ({center_percent[0]:.1f}%, {center_percent[1]:.1f}%)\nWidth: {width_percent:.1f}%",
                        color=((255, 128, 128) if width == -1 else (128, 255, 128))
                    )

        else:
            _, center, width, coefficient = self.locater.locate_stripped(
                img)
        if width == -1:
            if return_image:
                await websocket.send(json.dumps({"distance":-1, "angle":-1, "center":(-1,-1), "piece_angle":-1, "image_string":jpg_string}))
            else:
                await websocket.send(json.dumps({"distance":-1, "angle":-1, "center":(-1,-1), "piece_angle":-1}))
        else:
            dist, angle_horiz, angle_vert = self.locater.loc_from_center(center)
                    # Calculate the angle of the line in degrees
            piece_angle = np.arctan(coefficient)

            # Calculate the vertical angle to the piece
            angle_to_piece_vertical = self.tilt_angle_radians - (self.vertical_field_of_view / 2.0) + angle_vert

            new_piece_angle = np.arctan(np.tan(piece_angle)/np.cos(angle_to_piece_vertical))

            # print(coefficient, np.degrees(angle_to_piece_vertical)) TODO: is angle horiz correct
            if return_image:
                await websocket.send(json.dumps({"distance":dist, "angle":angle_horiz, "center":(center[0], center[1]), "piece_angle":new_piece_angle, "image_string":jpg_string}))
            else:
                await websocket.send(json.dumps({"distance":dist, "angle":angle_horiz, "center":(center[0], center[1]), "piece_angle":new_piece_angle}))
            
    async def info(self, websocket, *args, **kwargs):
        info_dict = {
            "cam_name": self.name,
            "identifier": self.serial_number,
            "horizontal_focal_length": self.horizontal_focal_length,
            "vertical_focal_length": self.vertical_focal_length,
            "height": self.camera_height,
            "horizontal_resolution_pixels": self.camera_horizontal_resolution_pixels,
            "vertical_resolution_pixels": self.camera_vertical_resolution_pixels,
            "downscale_factor": self.downscale_factor,
            "tilt_angle_radians": self.tilt_angle_radians,
            "horizontal_field_of_view_radians": self.horizontal_field_of_view,
            "vertical_field_of_view_radians": self.vertical_field_of_view,
            "color_list": self.locater.color_list,
            "active_color": self.locater.active_color,
            "record": self.record
        }

        for key in cv2_props_dict:
            try:
                info_dict[key] = self.camera.get(cv2_props_dict[key])
            except:
                pass

        await websocket.send(json.dumps(info_dict))

    async def function_info(self, websocket, *args, **kwargs):
        info = {"description":"The command will return a lot of information about the current camera setup.",
                     "arguments": {},
                     "returns":
                        {"cam_name":{"type":"string",
                                     "description":"The name of the camera. This is the path to the camera.",
                                     "guarantee":True},

                        "identifier":{"type":"string",
                                     "description":"The identifier of the camera. This is a unique identifier for the camera, "
                                     "assigned by our program. It is usually the serial number of the camera, the manufacturer, "
                                     "and the model number. If there are two cameras with the same serial number, the program will "
                                     "append the platform (essentially the id of the usb port the camera is plugged into) to the "
                                     "end of the identifier.",
                                     "guarantee":True},

                        "horizontal_focal_length":{"type":"float",
                                     "description":"The horizontal focal length of the camera. "
                                     "This is used to calculate the distance to the object.",
                                     "guarantee":True},
                        
                        "vertical_focal_length":{"type":"float",
                                     "description":"The vertical focal length of the camera. "
                                     "This is used to calculate the distance to the object as well (shocker).",
                                     "guarantee":True},
                        
                        "height":{"type":"float",
                                     "description":"The height of the camera off the ground. "
                                     "This is used to calculate the distance to the object.",
                                     "guarantee":True},
                        
                        "horizontal_resolution_pixels":{"type":"int",
                                     "description":"The horizontal resolution of the camera. "
                                     "This is the number of pixels in the horizontal direction.",
                                     "guarantee":True},

                        "vertical_resolution_pixels":{"type":"int",
                                     "description":"The vertical resolution of the camera. "
                                     "This is the number of pixels in the vertical direction.",
                                     "guarantee":True},
                        
                        "downscale_factor":{"type":"int",
                                     "description":"The scale to process the image at. This is an integer greater than 1. "
                                     "The resolution of the photos sent over the websocket will be reduced by this factor. "
                                     "This can help with performance. The output resolution of the camera is the "
                                     "resolution of the camera divided by the processing scale.",
                                     "guarantee":True},
                                     
                        "tilt_angle_radians":{"type":"float",
                                     "description":"The angle of the camera relative to the ground. This is used to calculate "
                                     "the distance to the object. 0 is straight down, pi/2 is straight ahead.",
                                     "guarantee":True},

                        "horizontal_field_of_view_radians":{"type":"float",
                                     "description":"The horizontal field of view of the camera. This is the angle that the "
                                     "camera can see. This is used to calculate the distance to the object. It is measured in "
                                     "radians, not degrees!",
                                     "guarantee":True},
                        
                        "vertical_field_of_view_radians":{"type":"float",
                                     "description":"The vertical field of view of the camera. This is the angle that the camera "
                                     "can see. This is used to calculate the distance to the object. It is measured in radians, "
                                     "not degrees!",
                                     "guarantee":True},
                        
                        "color_list":{"type":"list",
                                     "description":"A list of dictionaries containing the red, green, blue, difference, "
                                     "and blur values of the colors to save, followed by the index of the desired active color. "
                                     "The difference and blur help with vision processing. The red, green, and blue values are the "
                                     "RGB values of the color being looked for. The difference is the maximum difference between "
                                     "the color in the image and the color being looked for. It is a somewhat arbitrary value. "
                                     "The blur represents the amount of blurring to do before processing the image. This often helps "
                                     "smooth colors out to provide a better detection, but it does introduce some lag.",
                                     "guarantee":True},
                        
                        "active_color":{"type":"int",
                                     "description":"The index of the active color. This is the index of the color in the color "
                                     "list that the object detection model is currently looking for.",
                                     "guarantee":True},
                        "record":{"type":"bool",
                                  "description":"Whether the camera is currently recording.",
                                  "guarantee":True}
                        
                     }}
        
        raw = {"description":"The raw command will return a the image as a stringified json image. This command will trigger the server to"
                     "take a picture and send it over the websocket.",
                     "arguments": 
                         {"quality":{"type":"float",
                                     "description":"Quality of returned image from 0 to 1.",
                                     "optional":True}},
                     "returns":
                         {"image_string":{"type":"string",
                                     "description":"JPG image represented as a utf8 encoded string.",
                                     "guarantee":True}}
                     }
        
        switch_color ={"description":"This command switches the object detection color to the passed index.",
                     "arguments": 
                         {"new_color":{"type":"int",
                                     "description":"Index of new color set in 'set_color' function.",
                                     "optional":False}}, 
                     "returns":info["returns"]}

        save_color = {"description":"This command changes the current color's values to the passed values.",
                     "arguments": 
                         {"red":{"type":"int",
                                     "description":"Red value of the color.",
                                     "optional":False},
                         "green":{"type":"int",
                                     "description":"Green value of the color.",
                                     "optional":False},
                         "blue":{"type":"int",
                                     "description":"Blue value of the color.",
                                     "optional":False},
                         "difference":{"type":"int",
                                     "description":"Difference value of the color.",
                                     "optional":False},
                         "blur":{"type":"int",
                                     "description":"Blur value of the color.",
                                     "optional":False}},
                     "returns":info["returns"]}

        add_color = {"description":"This command adds a new color to the color list.",
                     "arguments": 
                         {"red":{"type":"int",
                                     "description":"Red value of the color.",
                                     "optional":False},
                         "green":{"type":"int",
                                     "description":"Green value of the color.",
                                     "optional":False},
                         "blue":{"type":"int",
                                     "description":"Blue value of the color.",
                                     "optional":False},
                         "difference":{"type":"int",
                                     "description":"Difference value of the color.",
                                     "optional":False},
                         "blur":{"type":"int",
                                     "description":"Blur value of the color.",
                                     "optional":False}},
                     "returns":info["returns"]}

        delete_color = {"description":"This command removes the color at the passed index from the color list.",
                     "arguments": 
                         {"color_index":{"type":"int",
                                     "description":"Index of the color to remove from the list.",
                                     "optional":False}}, 
                     "returns":info["returns"]}
        
        piece = {"description":"This command extracts a game piece from an image.",
                     "arguments": 
                         {"return_image":{"type":"bool",
                                     "description":"Whether to return the image of the extracted piece.",
                                     "optional":True},
                        "quality":{"type":"float",
                                    "description":"Quality of returned image from 0 to 1.",
                                    "optional":True}}, 
                     "returns":{
                        "image_string":{"type":"string",
                                "description":"The extracted game piece image. JPG UTF8 string",
                                "guarantee":False},
                        "distance":{"type":"float",
                                    "description":"The distance to the piece in meters.",
                                    "guarantee":False},
                        "angle":{"type":"float",
                                    "description":"The angle to the piece in radians.",
                                    "guarantee":False},
                        "center":{"type":"tuple",
                                    "description":"The center of the piece in pixels.",
                                    "guarantee":False},
                        "piece_angle":{"type":"float",
                                    "description":"The angle of the piece in radians.",
                                    "guarantee":False}}}
        
        apriltag = {"description":"This command detects AprilTags in the image and returns their positions, orientations, "
                     "distances, and angles.",
                     "arguments": 
                         {"return_image":{"type":"bool",
                                     "description":"Whether to return the image with the AprilTags drawn on it.",
                                     "optional":True},
                          "preprocessing_mode":{"type":"string",
                                     "description":"The preprocessing mode to use. 0 is grayscale, 1 is L1, 2 is L2, 3 is L3. We recommend using 2 or 3.",
                                     "optional":True},
                          "quality":{"type":"float",
                                     "description":"Quality of returned image from 0 to 1.",
                                     "optional":True},
                          "preprocessor_parameters":{"type":"string",
                                     "description":"Parameters for the preprocessor in JSON format.",
                                     "optional":True}},
                        "returns":{
                        "image_string":{"type":"string",
                                "description":"The image with the AprilTags drawn on it. JPG UTF8 string",
                                "guarantee":False},
                        "tags":{"type":"list",
                                "description":"A list of dictionaries containing the tag_id, position (3D vector), orientation (3D vector), "
                                "distance, horizontal angle, and vertical angle.",
                                "guarantee":False}}}
        
        set_camera_params = {"description":"Use this to change the values used by the camera capture.",
                     "arguments": 
                         {"horizontal_focal_length":{"type":"float",
                                     "description":"The horizontal focal length of the camera. "
                                     "This is used to calculate the distance to the object.",
                                     "optional":True},
                        
                        "vertical_focal_length":{"type":"float",
                                     "description":"The vertical focal length of the camera. "
                                     "This is used to calculate the distance to the object as well (shocker).",
                                     "optional":True},
                        
                        "height":{"type":"float",
                                     "description":"The height of the camera off the ground. "
                                     "This is used to calculate the distance to the object.",
                                     "optional":True},
                        
                        "horizontal_resolution_pixels":{"type":"int",
                                     "description":"The horizontal resolution of the camera. "
                                     "This is the number of pixels in the horizontal direction.",
                                     "optional":True},

                        "vertical_resolution_pixels":{"type":"int",
                                     "description":"The vertical resolution of the camera. "
                                     "This is the number of pixels in the vertical direction.",
                                     "optional":True},
                        
                        "downscale_factor":{"type":"int",
                                     "description":"The scale to process the image at. This is an integer greater than 1. "
                                     "The resolution of the photos sent over the websocket will be reduced by this factor. "
                                     "This can help with performance. The output resolution of the camera is the "
                                     "resolution of the camera divided by the processing scale.",
                                     "optional":True},
                                     
                        "tilt_angle_radians":{"type":"float",
                                     "description":"The angle of the camera relative to the ground. This is used to calculate "
                                     "the distance to the object. 0 is straight down, pi/2 is straight ahead.",
                                     "optional":True},

                        "horizontal_field_of_view_radians":{"type":"float",
                                     "description":"The horizontal field of view of the camera. This is the angle that the "
                                     "camera can see. This is used to calculate the distance to the object. It is measured in "
                                     "radians, not degrees!",
                                     "optional":True},
                        
                        "vertical_field_of_view_radians":{"type":"float",
                                     "description":"The vertical field of view of the camera. This is the angle that the camera "
                                     "can see. This is used to calculate the distance to the object. It is measured in radians, "
                                     "not degrees!",
                                     "optional":True},

                        "record":{"type":"bool",
                                  "description":"Whether the camera is currently recording. This is used to save the video stream to a file",
                                  "optional":True},

                        "aperture":{"type":"float",
                                     "description":"The aperture of the camera. This is the size of the opening in the lens that lets light in.",
                                     "optional":True},

                        "autofocus":{"type":"int",
                                     "description":"(1 or 0) Whether the camera should autofocus.",
                                     "optional":True},
                        
                        "autoexposure":{"type":"int",
                                     "description":"(1 or 0) Whether the camera should use autoexposure.",
                                     "optional":True},

                        "backlight":{"type":"float",
                                     "description":"Amount of backlight.",
                                     "optional":True},
                        
                        "brightness":{"type":"float",
                                     "description":"Brightness.",
                                     "optional":True},

                        "buffer_size":{"type":"float",
                                     "description":"Number of frames to store in buffer. Don't mess with unless you know what you are doing.",
                                     "optional":True},
                        
                        "contrast":{"type":"float",
                                     "description":"Contrast.",
                                     "optional":True},
                        
                        "convert_rgb":{"type":"int",
                                     "description":"(1 or 0) If colors in your image are inverted, like red things look blue, change this.",
                                     "optional":True},
                        
                        "exposure":{"type":"float",
                                     "description":"Exposure.",
                                     "optional":True},

                        "focus":{"type":"float",
                                     "description":"Focus of camera. Don't mess with unless you know what you are doing.",
                                     "optional":True},
                        
                        "fps":{"type":"float",
                                     "description":"Hardware FPS limiter - does not exist on most cameras.",
                                     "optional":True},
                        
                        "frame_height":{"type":"int",
                                     "description":"Hardware controlled hight of captured frame. Please use \"vertical_resolution_pixels\"",
                                     "optional":True},
                        
                        "frame_width":{"type":"int",
                                     "description":"Hardware controlled width of captured frame. Please use \"horizontal_resolution_pixels\"",
                                     "optional":True},

                        "gain":{"type":"float",
                                     "description":"Camera Gain (look up if necessary).",
                                     "optional":True},
                        
                        "gamma":{"type":"float",
                                     "description":"Camera Gamma (look up if necessary).",
                                     "optional":True},
                        
                        "hue":{"type":"float",
                                     "description":"Hue.",
                                     "optional":True},

                        "iso_speed":{"type":"float",
                                     "description":"ISO of camera - like brightness.",
                                     "optional":True},

                        "position_frames":{"type":"float",
                                     "description":"The position of the frames of the camera - does nothing on most cameras.",
                                     "optional":True},
                        
                        "position_milliseconds":{"type":"float",
                                     "description":"The position of the milliseconds of the camera. This usually does not do anything, but it can help with debugging.",
                                     "optional":True},
                        
                        "saturation":{"type":"float",
                                     "description":"Saturation of image.",
                                     "optional":True},
                        
                        "sharpness":{"type":"float",
                                     "description":"Sharpness of image. Generally dont mess with this.",
                                     "optional":True},

                        "temperature":{"type":"float",
                                     "description":"Temperature of image. Usually over 6000",
                                     "optional":True},
                        
                        "trigger":{"type":"float",
                                     "description":"The trigger speed of the camera. We are not entirely sure what this does. It seems to have no effect.",
                                     "optional":True},
                        
                        "white_balance_blue_u":{"type":"float",
                                     "description":"The white balance blue value of the camera.",
                                     "optional":True},

                        "white_balance_red_v":{"type":"float",
                                     "description":"The white balance red value of the camera.",
                                     "optional":True},

                        "zoom":{"type":"float",
                                     "description":"The zoom of the camera.",
                                     "optional":True},
                                     },
                        
                                     
                        "returns":info["returns"]}
        
        warning = {"warning":"fake_image_string"}
        
        await websocket.send(json.dumps({
            "warning": warning,
            "raw": raw,
            "switch_color": switch_color,
            "save_color": save_color,
            "add_color": add_color,
            "delete_color": delete_color,
            "set_camera_params": set_camera_params,
            "piece": piece,
            "apriltag": apriltag,
            "info": info,
        }))

    def __del__(self):
        # Cleanup code

        if hasattr(self, 'camera') and self.camera.isOpened():
            self.camera.release()
        if hasattr(self, 'video_writer') and self.video_writer is not None:
            print("Releasing video writer.")
            self.video_writer.release()
        del self
