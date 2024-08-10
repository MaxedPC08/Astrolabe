import cv2
import numpy as np
import json
from constants import (CAMERA_HORIZONTAL_RESOLUTION_PIXELS, CAMERA_VERTICAL_RESOLUTION_PIXELS, TILT_ANGLE_RADIANS,
                    CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS, CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS, CAMERA_HEIGHT)
class Locater:
    """
    This class is used to find the object in an image. It is faster to use a class than just a function.
    """
    def __init__(self, camera_horizontal_resolution_pixels=CAMERA_HORIZONTAL_RESOLUTION_PIXELS,
                 camera_vertical_resolution_pixels=CAMERA_VERTICAL_RESOLUTION_PIXELS,
                 tilt_angle_radians=TILT_ANGLE_RADIANS, camera_height=CAMERA_HEIGHT,
                 camera_horizontal_field_of_view_radians=CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS,
                 camera_vertical_field_of_view_radians=CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS):
        """
        This function initializes the Locater class. It reads the parameters from the params.json file and sets the target color.
        If there is no such file then it uses the default values. Please make sure that file exists.
        """
        self.active_color = 0
        self.green_line = np.array([[0, 255, 0] for i in range(11)])
        self.red_line = np.array([[0, 0, 255] for i in range(11)])
        try:
            with open('params.json', 'r') as f:
                self.color_list = json.load(f)
        except json.decoder.JSONDecodeError:
            print("params.json has an incorrect format. Using default values.")
            self.color_list = [{"red": 255,
                                "green": 255,
                                "blue": 255,
                                "difference": 50,
                                "blur": 5}]

            with open('params.json', 'w') as f:
                json.dump(self.color_list, f, indent=4)

        except FileNotFoundError:
            print("params.json not found. Using default values.")
            self.color_list = [{"red": 255,
                                "green": 255,
                                "blue": 255,
                                "difference": 50,
                                "blur": 5}]

            with open('params.json', 'w') as f:
                json.dump(self.color_list, f, indent=4)

        self.camera_horizontal_resolution_pixels = camera_horizontal_resolution_pixels
        self.camera_vertical_resolution_pixels = camera_vertical_resolution_pixels
        self.tilt_angle_radians = tilt_angle_radians
        self.camera_height = camera_height
        self.camera_horizontal_field_of_view_radians = camera_horizontal_field_of_view_radians
        self.camera_vertical_field_of_view_radians = camera_vertical_field_of_view_radians

        self.res_corresp_horizontal = np.tan(self.camera_horizontal_field_of_view_radians / 2.0) / (self.camera_horizontal_resolution_pixels / 2.0)
        self.res_corresp_vertical = np.tan(self.camera_vertical_field_of_view_radians / 2.0) / (self.camera_vertical_resolution_pixels / 2.0)
        self.max_vertical_angle = self.camera_vertical_resolution_pixels * self.res_corresp_vertical
        self.max_horizontal_angle = self.camera_horizontal_resolution_pixels * self.res_corresp_horizontal


    def locate(self, image, blur=-1, dif=-1):
        """
        This function locates the object in the image. It uses the target color and the parameters to find the object.
        :param blur:
        :param dif:
        :param red_val:
        :param image: Numpy array of the image
        :return: (ndarray, tuple, int) where the first is the processed image with crosshairs etc.,
        center is the center of the object (x, y), and width is the width of the object
        """
        if blur == -1:
            blur = self.color_list[self.active_color]["blur"]

        if dif == -1:
            dif = self.color_list[self.active_color]["difference"]

        # Convert the image and target color to the Lab color space
        new_color = [-0.666, -0.666, -0.666]
        image_copy = image.copy()

        # Normalize the image and target color
        array = np.average(np.abs(image - np.array([self.color_list[self.active_color]["red"],
                                                    self.color_list[self.active_color]["green"],
                                                    self.color_list[self.active_color]["blue"]])), 2)
        if np.all(array > dif*2):
            # print("No matching color found")
            return image, (-1, -1), -1
        x, y = np.unravel_index(np.argmin(array), array.shape)

        if blur > 0:
            """image = cv2.blur(image, (blur, blur))
            image = cv2.medianBlur(image, blur//2*2+1)"""
            image = cv2.bilateralFilter(image, blur, blur*2, blur//2)


        cols, rows = image.shape[:2]


        image = image.astype(np.float32)

        # Create a mask that is 2 pixels larger in each dimension than the image
        mask = np.zeros((cols + 2, rows + 2), np.uint8)

        # Perform the flood fill operation
        _, image, _, _ = cv2.floodFill(image, mask, (y, x), new_color, [dif, dif, dif], [dif, dif, dif])
        image = image[:, :, 0].clip(-1, 0) * -1

        # Process the image and make it viewer - worthy
        # Get the indices where image equals 1
        indices = np.where(image == -new_color[0])

        # Calculate the center, left, and right directly from the indices
        center = np.mean(indices, axis=1)
        left = np.min(indices[1])
        right = np.max(indices[1])

        image += 0.334
        image = image_copy * image[:, :, np.newaxis]
        image = image.astype(np.uint8)


        # draw a crosshair

        try:
            image[int(center[0]) - 5:int(center[0]) + 6, int(center[1])] = self.red_line
            image[int(center[0]), int(center[1]) - 5:int(center[1]) + 6] = self.red_line

            image[int(center[0]) - 5:int(center[0]) + 6, left] = self.green_line
            image[int(center[0]) - 5:int(center[0]) + 6, right] = self.green_line
        except:
            pass

        return image, center, right-left

    def locate_stripped(self, image, blur=-1, dif=-1):
        """
        This function locates the object in the image. It uses the target color and the parameters to find the object.
        :param blur:
        :param dif:
        :param red_val:
        :param image: Numpy array of the image
        :return: (ndarray, tuple, int) where the first is the processed image with crosshairs etc.,
        center is the center of the object (x, y), and width is the width of the object
        """
        if blur == -1:
            blur = self.color_list[self.active_color]["blur"]

        if dif == -1:
            dif = self.color_list[self.active_color]["difference"]

        # Convert the image and target color to the Lab color space
        new_color = [-1, -1, -1]

        # Normalize the image and target color
        array = np.average(np.abs(image - np.array([self.color_list[self.active_color]["red"],
                                                    self.color_list[self.active_color]["green"],
                                                    self.color_list[self.active_color]["blue"]])), 2)
        if np.all(array > dif*2):
            return image, (-1, -1), -1
        x, y = np.unravel_index(np.argmin(array), array.shape)

        if blur > 0:
            image = cv2.bilateralFilter(image, blur, blur*2, blur//2)

        cols, rows = image.shape[:2]

        image = image.astype(np.float32)

        # Create a mask that is 2 pixels larger in each dimension than the image
        mask = np.zeros((cols + 2, rows + 2), np.uint8)

        # Perform the flood fill operation
        _, image, _, _ = cv2.floodFill(image, mask, (y, x), new_color, [dif, dif, dif], [dif, dif, dif])
        image = image[:, :, 0].clip(-1, 0) * -1

        # Process the image and make it viewer - worthy
        # Get the indices where image equals 1
        indices = np.where(image == -new_color[0])

        # Calculate the center, left, and right directly from the indices
        center = np.mean(indices, axis=1)
        left = np.min(indices[1])
        right = np.max(indices[1])

        return image, center, right-left

    def loc_from_center(self, center):
        """
        This function calculates the location of the object in the image from the center and width.
        :param center: tuple of the center of the object (x, y)
        :param width: int of the width of the object
        :return: tuple of the location of the object (x, y)
        """
        #width = width * RES_CORRESP_HORIZONTAL
        # distance = OBJECT_WIDTH / (2 * np.tan(width / 2)) # This is the distance in inches calcualted with the width of the image
        angle_radians_horiz = ((center[1] * self.res_corresp_horizontal) -
                               self.camera_horizontal_field_of_view_radians * 0.5)

        angle_radians_vert = ((self.max_vertical_angle - center[0] * self.res_corresp_vertical) +
                              self.tilt_angle_radians - self.camera_vertical_field_of_view_radians * 0.5)
        dist = (np.tan(angle_radians_vert) * self.camera_height) / np.cos(angle_radians_horiz)
        return dist, angle_radians_horiz
