import cv2
import numpy as np
import json
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

        # Preprocess the target color for maximum efficiency

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
        _, image, _, _ = cv2.floodFill(image, mask, (y, x), new_color,
                                       [self.color_list[self.active_color]["dif"] for _ in range(3)],
                                       [self.color_list[self.active_color]["dif"] for _ in range(3)])
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

    def locate_stripped(self, image):
        """
        This function locates the object in the image. It uses the target color and the parameters to find the object.
        :param image: Numpy array of the image
        :return: (ndarray, tuple, int) where the first is the processed image with crosshairs etc.,
        center is the center of the object (x, y), and width is the width of the object
        """

        # Convert the image and target color to the Lab color space
        new_color = [-1, -1, -1]

        # Normalize the image and target color
        array = np.sum(np.square(image - np.array([self.color_list[self.active_color]["red"],
                                                   self.color_list[self.active_color]["green"],
                                                   self.color_list[self.active_color]["blue"]])), 2)
        if np.all(array > self.color_list[self.active_color]["dif"]**2*3):
            #print("No matching color found")
            return image, (-1, -1), -1
        x, y = np.unravel_index(np.argmin(array), array.shape)

        if self.color_list[self.active_color]["blur"] > 0:
            kernel = (np.ones((self.color_list[self.active_color]["blur"],
                              self.color_list[self.active_color]["blur"]), np.float32)
                      / (self.color_list[self.active_color]["blur"] ** 2))
            image = cv2.filter2D(image, -1, kernel)
            image = cv2.medianBlur(image, self.color_list[self.active_color]["blur"]*2+1)

        cols, rows = image.shape[:2]


        image = image.astype(np.float32)

        # Create a mask that is 2 pixels larger in each dimension than the image
        mask = np.zeros((cols + 2, rows + 2), np.uint8)

        # Perform the flood fill operation
        _, image, _, _ = cv2.floodFill(image, mask, (y, x), new_color,
                                       [self.color_list[self.active_color]["dif"] for _ in range(3)],
                                       [self.color_list[self.active_color]["dif"] for _ in range(3)])
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

        # loc_from_center(center, right-left)

        return center, right-left

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
    # print(f"Dist in inches: {loc}")
