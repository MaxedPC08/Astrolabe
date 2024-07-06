import cv2
import numpy as np
import time

# Set up some constants for distance calcs
CAMERA_HORIZONTAL_RESOLUTION_PIXELS = 640//4 #This is the resolution of the input image, not necessarily the camera.
CAMERA_VERTICAL_RESOLUTION_PIXELS = 480//4 #This is the resolution of the input image, not necessarily the camera.
TILT_ANGLE_RADIANS = 2*np.pi/6-0.1# This is the tilt of the camera. 0 is looking straight down, pi/2 is looking straight ahead
CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS = 75 * np.pi / 180 # This is the field of view of the camera horizontally
CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS = 56.26 * np.pi / 180 # This is the field of view of the camera vertically
CAMERA_HEIGHT = 30 # This is the height of the camera in whatever units you want the distance to be calculated in
OBJECT_WIDTH = 8

# DO NOT CHANGE THESE VALUES
RES_CORRESP_HORIZONTAL = np.tan(CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS / 2.0) / (CAMERA_HORIZONTAL_RESOLUTION_PIXELS / 2.0)
RES_CORRESP_VERTICAL = np.tan(CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS / 2.0) / (CAMERA_VERTICAL_RESOLUTION_PIXELS / 2.0)

MAX_VERTICAL_ANGLE = CAMERA_VERTICAL_RESOLUTION_PIXELS * RES_CORRESP_VERTICAL
MAX_HORIZONTAL_ANGLE = CAMERA_HORIZONTAL_RESOLUTION_PIXELS * RES_CORRESP_HORIZONTAL


class Locater:
    """
    This class is used to find the object in an image. It is faster to use a class than just a function.
    """
    def __init__(self):
        """
        This function initializes the Locater class. It reads the parameters from the params.txt file and sets the target color.
        If there is no such file then it uses the default values. Please make sure that file exists.
        """
        self.green_line = np.array([[0, 255, 0] for i in range(11)])
        self.red_line = np.array([[0, 0, 255] for i in range(11)])
        try:
            with open('../FYRE-FRSee/params.txt', 'r') as f:
                lines = f.readlines()
                self.red_val = int(lines[0].split(": ")[1])
                self.green_val = int(lines[1].split(": ")[1])
                self.blue_val = int(lines[2].split(": ")[1])
                self.blur_val = int(lines[3].split(": ")[1])
                self.difference_val = int(lines[4].split(": ")[1])
        except FileNotFoundError:
            print("params.txt not found. Using default values.")
            self.red_val = 0
            self.green_val = 0
            self.blue_val = 0
            self.blur_val = 0
            self.difference_val = 50

        # Preprocess the target color for maximum efficiency
        self.target_color= np.array([self.red_val, self.green_val, self.blue_val])

    def locate(self, image, blur=-1, dif=-1, red_val=-1, green_val=-1, blue_val=-1):
        """
        This function locates the object in the image. It uses the target color and the parameters to find the object.
        :param image: Numpy array of the image
        :return: (ndarray, tuple, int) where the first is the processed image with crosshairs etc.,
        center is the center of the object (x, y), and width is the width of the object
        """
        if blur == -1:
            blur = self.blur_val

        if dif == -1:
            dif = self.difference_val

        if red_val != -1 or green_val != -1 or blue_val != -1:
            self.red_val = red_val
            self.green_val = green_val
            self.blue_val = blue_val
            self.target_color = np.array([self.red_val, self.green_val, self.blue_val])

        # Convert the image and target color to the Lab color space
        new_color = [-0.666, -0.666, -0.666]
        image_copy = image.copy()

        # Normalize the image and target color
        array = np.average(np.abs(image - np.array(self.target_color)), 2)
        if np.all(array > dif*2):
            print("No matching color found")
            return image, (-1, -1), -1
        x, y = np.unravel_index(np.argmin(array), array.shape)

        if blur > 0:
            kernel = np.ones((blur, blur), np.float32) / (blur ** 2)
            image = cv2.filter2D(image, -1, kernel)

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

        loc_from_center(center, right-left)

        return image, center, right-left

    def locate_stripped(self, image, blur=-1, dif=-1, red_val=-1, green_val=-1, blue_val=-1):
        """
        This function locates the object in the image. It uses the target color and the parameters to find the object.
        :param image: Numpy array of the image
        :return: (ndarray, tuple, int) where the first is the processed image with crosshairs etc.,
        center is the center of the object (x, y), and width is the width of the object
        """
        if blur == -1:
            blur = self.blur_val

        if dif == -1:
            dif = self.difference_val

        if red_val != -1 or green_val != -1 or blue_val != -1:
            self.red_val = red_val
            self.green_val = green_val
            self.blue_val = blue_val
            self.target_color = np.array([self.red_val, self.green_val, self.blue_val])

        # Convert the image and target color to the Lab color space
        new_color = [-1, -1, -1]

        # Normalize the image and target color
        array = np.average(np.abs(image - np.array(self.target_color)), 2)
        if np.all(array > dif*2):
            print("No matching color found")
            return image, (-1, -1), -1
        x, y = np.unravel_index(np.argmin(array), array.shape)

        if blur > 0:
            kernel = np.ones((blur, blur), np.float32) / (blur ** 2)
            image = cv2.filter2D(image, -1, kernel)

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
        bottom = np.max(indices[0])
        top = np.min(indices[0])

        loc_from_center(center, right-left)

        return image, center, right-left

def loc_from_center(center, width):
    """
    This function calculates the location of the object in the image from the center and width.
    :param center: tuple of the center of the object (x, y)
    :param width: int of the width of the object
    :return: tuple of the location of the object (x, y)
    """
    #width = width * RES_CORRESP_HORIZONTAL
    # distance = OBJECT_WIDTH / (2 * np.tan(width / 2)) # This is the distance in inches calcualted with the width of the image
    angle_radians_horiz = ((center[1] * RES_CORRESP_HORIZONTAL) -
                           CAMERA_HORIZONTAL_FIELD_OF_VIEW_RADIANS * 0.5)

    angle_radians_vert = ((MAX_VERTICAL_ANGLE - center[0] * RES_CORRESP_VERTICAL) +
                          TILT_ANGLE_RADIANS - CAMERA_VERTICAL_FIELD_OF_VIEW_RADIANS * 0.5)
    loc = (np.tan(angle_radians_vert) * CAMERA_HEIGHT) / np.cos(angle_radians_horiz)
    print(f"Dist in inches: {loc}")
    return loc, angle_radians_horiz