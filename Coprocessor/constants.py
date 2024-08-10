import numpy as np
import cv2

# This file contains all the default values for the constants used in the program. These values can be changed by the
# user in the GUI. The values are used in the Locater class to calculate the distance to the object in the image, and
# the apriltag class to calculate the pose of the apriltag in the image. It also contains a dictionary of the cv2
# properties that can be changed in the GUI.

CAMERA_HORIZONTAL_RESOLUTION_PIXELS = 640  # This is the resolution of the input image, not necessarily the camera.
CAMERA_VERTICAL_RESOLUTION_PIXELS = 480  # This is the resolution of the input image, not necessarily the camera.
PROCESSING_SCALE = 4
TILT_ANGLE_RADIANS = 2*np.pi/6-0.1  # This is the tilt of the camera. 0 is looking straight down, pi/2 is looking
# straight ahead
CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS = 68 * np.pi / 180  # This is the field of view of the camera horizontally
CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS = 51 * np.pi / 180  # This is the field of view of the camera vertically
CAMERA_HEIGHT = 30  # This is the height of the camera in whatever units you want the distance to be calculated in
# Default is cm

APRIL_TAG_WIDTH = 0.155  # This is the width of the April tag in the desired unit. Default is meters.
APRIL_TAG_HEIGHT = 0.155  # This is the height of the April tag in the desired unit. Default is meters.


# Calculate the focal lengths from the other information.
HORIZONTAL_FOCAL_LENGTH = ((CAMERA_HORIZONTAL_RESOLUTION_PIXELS / 2) /
                           np.tan(CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS / 2))

VERTICAL_FOCAL_LENGTH = (CAMERA_VERTICAL_RESOLUTION_PIXELS / 2) / np.tan(CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS / 2)

cv2_props_dict = {
    "CAP_PROP_APERTURE": cv2.CAP_PROP_APERTURE,
    "CAP_PROP_AUTOFOCUS": cv2.CAP_PROP_AUTOFOCUS,
    "CAP_PROP_AUTO_EXPOSURE": cv2.CAP_PROP_AUTO_EXPOSURE,
    "CAP_PROP_BACKLIGHT": cv2.CAP_PROP_BACKLIGHT,
    "CAP_PROP_BRIGHTNESS": cv2.CAP_PROP_BRIGHTNESS,
    "CAP_PROP_BUFFERSIZE": cv2.CAP_PROP_BUFFERSIZE,
    "CAP_PROP_CONTRAST": cv2.CAP_PROP_CONTRAST,
    "CAP_PROP_CONVERT_RGB": cv2.CAP_PROP_CONVERT_RGB,
    "CAP_PROP_EXPOSURE": cv2.CAP_PROP_EXPOSURE,
    "CAP_PROP_FOCUS": cv2.CAP_PROP_FOCUS,
    "CAP_PROP_FPS": cv2.CAP_PROP_FPS,
    "CAP_PROP_FRAME_HEIGHT": cv2.CAP_PROP_FRAME_HEIGHT,
    "CAP_PROP_FRAME_WIDTH": cv2.CAP_PROP_FRAME_WIDTH,
    "CAP_PROP_GAIN": cv2.CAP_PROP_GAIN,
    "CAP_PROP_GAMMA": cv2.CAP_PROP_GAMMA,
    "CAP_PROP_HUE": cv2.CAP_PROP_HUE,
    "CAP_PROP_ISO_SPEED": cv2.CAP_PROP_ISO_SPEED,
    "CAP_PROP_POS_FRAMES": cv2.CAP_PROP_POS_FRAMES,
    "CAP_PROP_POS_MSEC": cv2.CAP_PROP_POS_MSEC,
    "CAP_PROP_SATURATION": cv2.CAP_PROP_SATURATION,
    "CAP_PROP_SHARPNESS": cv2.CAP_PROP_SHARPNESS,
    "CAP_PROP_TEMPERATURE": cv2.CAP_PROP_TEMPERATURE,
    "CAP_PROP_TRIGGER": cv2.CAP_PROP_TRIGGER,
    "CAP_PROP_WHITE_BALANCE_BLUE_U": cv2.CAP_PROP_WHITE_BALANCE_BLUE_U,
    "CAP_PROP_WHITE_BALANCE_RED_V": cv2.CAP_PROP_WHITE_BALANCE_RED_V,
    "CAP_PROP_ZOOM": cv2.CAP_PROP_ZOOM
}

