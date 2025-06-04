import numpy as np
import cv2
import json
import os

with open('defaults.json', 'r') as f:
    defaults = json.load(f)

CAMERA_HORIZONTAL_RESOLUTION_PIXELS = defaults["horizontal_resolution"]  # This is the resolution of the input image, not necessarily the camera.
CAMERA_VERTICAL_RESOLUTION_PIXELS = defaults["vertical_resolution"]  # This is the resolution of the input image, not necessarily the camera.
DOWNSCALE_FACTOR = defaults["downscale_factor"]  # This is the factor by which to downscale the image. 1 means no downscaling.
TILT_ANGLE_RADIANS = defaults["tilt_angle"]  # This is the tilt of the camera. 0 is looking straight down, pi/2 is looking
# straight ahead
CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS = defaults["horizontal_fov"]  # This is the field of view of the camera horizontally
CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS = defaults["vertical_fov"]  # This is the field of view of the camera vertically
CAMERA_HEIGHT = defaults["camera_height"]  # This is the height of the camera in whatever units you want the distance to be calculated in

APRIL_TAG_WIDTH = defaults["april_tag_width"]  # This is the width of the AprilTag in meters
APRIL_TAG_HEIGHT = defaults["april_tag_height"]  # This is the height of the AprilTag in meters

IMAGE_FORMAT = "jpg"
LOCAL_HOST = True
TEST_MODE_FALLBACK = True

HORIZONTAL_FOCAL_LENGTH = ((CAMERA_HORIZONTAL_RESOLUTION_PIXELS / 2) /
                           np.tan(CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS / 2))
VERTICAL_FOCAL_LENGTH = (CAMERA_VERTICAL_RESOLUTION_PIXELS / 2) / np.tan(CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS / 2)
AVG_FOCAL_LENGTH = (HORIZONTAL_FOCAL_LENGTH + VERTICAL_FOCAL_LENGTH) / 2

cv2.CAP_PROP_APERTURE

cv2_props_dict = {
    "aperture": cv2.CAP_PROP_APERTURE,
    "autofocus": cv2.CAP_PROP_AUTOFOCUS,
    "auto_exposure": cv2.CAP_PROP_AUTO_EXPOSURE,
    "backlight": cv2.CAP_PROP_BACKLIGHT,
    "brightness": cv2.CAP_PROP_BRIGHTNESS,
    "buffer_size": cv2.CAP_PROP_BUFFERSIZE,
    "contrast": cv2.CAP_PROP_CONTRAST,
    "convert_rgb": cv2.CAP_PROP_CONVERT_RGB,
    "exposure": cv2.CAP_PROP_EXPOSURE,
    "focus": cv2.CAP_PROP_FOCUS,
    "fps": cv2.CAP_PROP_FPS,
    "frame_height": cv2.CAP_PROP_FRAME_HEIGHT,
    "frame_width": cv2.CAP_PROP_FRAME_WIDTH,
    "gain": cv2.CAP_PROP_GAIN,
    "gamma": cv2.CAP_PROP_GAMMA,
    "hue": cv2.CAP_PROP_HUE,
    "iso_speed": cv2.CAP_PROP_ISO_SPEED,
    "position_frames": cv2.CAP_PROP_POS_FRAMES,
    "position_milliseconds": cv2.CAP_PROP_POS_MSEC,
    "saturation": cv2.CAP_PROP_SATURATION,
    "sharpness": cv2.CAP_PROP_SHARPNESS,
    "temperature": cv2.CAP_PROP_TEMPERATURE,
    "trigger": cv2.CAP_PROP_TRIGGER,
    "white_balance_blue_u": cv2.CAP_PROP_WHITE_BALANCE_BLUE_U,
    "white_balance_red_v": cv2.CAP_PROP_WHITE_BALANCE_RED_V,
    "zoom": cv2.CAP_PROP_ZOOM
}

