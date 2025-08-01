## Info about the cameras
Each camera has a unique ID, which is used to identify it in the system. It also gets its own unique websocket, starting at port 50001 for the first camera, 50002 for the second, and so on.

The function format for the camera commands is as follows:
```
{
    "functiopn": "command_name",
    "arg1": value1,
    "arg2": value2,
    ...,
    "argN": valueN
}
```

---

# Camera Commands

### **`info`**

**Description:** Returns a comprehensive set of information about the current camera's configuration.

**Returns:**
* **`cam_name`** (string): The path to the camera.
* **`identifier`** (string): A unique identifier for the camera, often including its serial number, manufacturer, and model. If multiple cameras share a serial number, the program will append the USB port ID.
* **`horizontal_focal_length`** (float): The camera's horizontal focal length, used for distance calculations.
* **`vertical_focal_length`** (float): The camera's vertical focal length, also used for distance calculations.
* **`height`** (float): The camera's height off the ground, used for distance calculations.
* **`horizontal_resolution_pixels`** (int): The number of pixels in the horizontal direction.
* **`vertical_resolution_pixels`** (int): The number of pixels in the vertical direction.
* **`downscale_factor`** (int): An integer (greater than 1) that determines the scale at which the image is processed. The output resolution will be the original resolution divided by this factor, which can improve performance.
* **`tilt_angle_radians`** (float): The camera's angle relative to the ground. 0 is straight down, and π/2 is straight ahead.
* **`horizontal_field_of_view_radians`** (float): The horizontal viewing angle of the camera, measured in radians.
* **`vertical_field_of_view_radians`** (float): The vertical viewing angle of the camera, measured in radians.
* **`color_list`** (list): A list of dictionaries. Each dictionary contains the red, green, blue, difference, and blur values for a specific color to be detected.
* **`active_color`** (int): The index of the color from the `color_list` that the object detection model is currently using.
* **`record`** (bool): Indicates whether the camera is currently recording.

---

### **`raw`**

**Description:** Triggers the server to capture and send a raw image.

**Arguments:**
* **`quality`** (float, optional): The quality of the returned image, from 0 to 1.

**Returns:**
* **`image_string`** (string): The captured JPG image as a UTF-8 encoded string.

---

### **`switch_color`**

**Description:** Changes the object detection color to a new one from the color list.

**Arguments:**
* **`new_color`** (int): The index of the new color in the `color_list` to be set as the active color.

**Returns:** The same information as the `info` command, updated with the new active color.

---

### **`save_color`**

**Description:** Updates the values of the currently active color.

**Arguments:**
* **`red`** (int): The red value (RGB).
* **`green`** (int): The green value (RGB).
* **`blue`** (int): The blue value (RGB).
* **`difference`** (int): The maximum acceptable difference between the target color and a color in the image.
* **`blur`** (int): The amount of blurring to apply before processing the image.

**Returns:** The same information as the `info` command, updated with the new color values.

---

### **`add_color`**

**Description:** Adds a new color with specified values to the `color_list`.

**Arguments:**
* **`red`** (int): The red value (RGB).
* **`green`** (int): The green value (RGB).
* **`blue`** (int): The blue value (RGB).
* **`difference`** (int): The maximum acceptable difference between the target color and a color in the image.
* **`blur`** (int): The amount of blurring to apply before processing the image.

**Returns:** The same information as the `info` command, updated with the new color added to the list.

---

### **`delete_color`**

**Description:** Removes a color from the `color_list` at a specified index.

**Arguments:**
* **`color_index`** (int): The index of the color to be removed.

**Returns:** The same information as the `info` command, with the specified color removed from the list.

---

### **`piece`**

**Description:** Extracts a game piece from an image.

**Arguments:**
* **`return_image`** (bool, optional): If `True`, the extracted game piece image is returned.
* **`quality`** (float, optional): The quality of the returned image, from 0 to 1.

**Returns:**
* **`image_string`** (string, optional): The extracted game piece image as a JPG UTF-8 string.
* **`distance`** (float, optional): The distance to the piece in meters.
* **`angle`** (float, optional): The horizontal angle to the piece in radians.
* **`center`** (tuple, optional): The pixel coordinates of the piece's center.
* **`piece_angle`** (float, optional): The angle of the piece itself in radians.

---

### **`apriltag`**

**Description:** Detects AprilTags in the image and returns their positions, orientations, and other related data.

**Arguments:**
* **`return_image`** (bool, optional): If `True`, the image is returned with the detected AprilTags drawn on it.
* **`preprocessing_mode`** (string, optional): The preprocessing mode for the image. Options are:
    * `0`: Grayscale
    * `1`: L1
    * `2`: L2 (recommended)
    * `3`: L3 (recommended)
* **`quality`** (float, optional): The quality of the returned image, from 0 to 1.
* **`preprocessor_parameters`** (string, optional): Parameters for the preprocessor in JSON format.

**Returns:**
* **`image_string`** (string, optional): The image with AprilTags drawn on it as a JPG UTF-8 string.
* **`tags`** (list, optional): A list of dictionaries, each containing information about a detected tag, including its `tag_id`, 3D `position`, 3D `orientation`, `distance`, `horizontal angle`, and `vertical angle`.

---

### **`set_camera_params`**

**Description:** Modifies various camera parameters to change how images are captured and processed.

**Arguments:**
* **`horizontal_focal_length`** (float, optional): The horizontal focal length.
* **`vertical_focal_length`** (float, optional): The vertical focal length.
* **`height`** (float, optional): The camera's height off the ground.
* **`horizontal_resolution_pixels`** (int, optional): The horizontal resolution of the camera.
* **`vertical_resolution_pixels`** (int, optional): The vertical resolution of the camera.
* **`downscale_factor`** (int, optional): The scale to process the image at (integer greater than 1).
* **`tilt_angle_radians`** (float, optional): The camera's angle relative to the ground.
* **`horizontal_field_of_view_radians`** (float, optional): The horizontal field of view.
* **`vertical_field_of_view_radians`** (float, optional): The vertical field of view.
* **`record`** (bool, optional): Whether the camera should record the video stream to a file.
* **`aperture`** (float, optional): The size of the lens opening.
* **`autofocus`** (int, optional): `1` to enable autofocus, `0` to disable.
* **`autoexposure`** (int, optional): `1` to enable autoexposure, `0` to disable.
* **`backlight`** (float, optional): The amount of backlight compensation.
* **`brightness`** (float, optional): The camera's brightness.
* **`buffer_size`** (float, optional): The number of frames to store in the buffer.
* **`contrast`** (float, optional): The camera's contrast.
* **`convert_rgb`** (int, optional): `1` or `0`. Use this if the colors in your image are inverted.
* **`exposure`** (float, optional): The camera's exposure.
* **`focus`** (float, optional): The camera's focus.
* **`fps`** (float, optional): A hardware FPS limiter (not supported by most cameras).
* **`frame_height`** (int, optional): The hardware-controlled height of the captured frame. Use `vertical_resolution_pixels` instead.
* **`frame_width`** (int, optional): The hardware-controlled width of the captured frame. Use `horizontal_resolution_pixels` instead.
* **`gain`** (float, optional): The camera's gain.
* **`gamma`** (float, optional): The camera's gamma.
* **`hue`** (float, optional): The camera's hue.
* **`iso_speed`** (float, optional): The camera's ISO speed.
* **`position_frames`** (float, optional): The position of camera frames.
* **`position_milliseconds`** (float, optional): The position of camera frames in milliseconds.
* **`saturation`** (float, optional): The saturation of the image.
* **`sharpness`** (float, optional): The sharpness of the image.
* **`temperature`** (float, optional): The color temperature of the image (usually above 6000).
* **`trigger`** (float, optional): The camera's trigger speed.
* **`white_balance_blue_u`** (float, optional): The white balance blue value.
* **`white_balance_red_v`** (float, optional): The white balance red value.
* **`zoom`** (float, optional): The camera's zoom level.

**Returns:** The same information as the `info` command, updated with the new camera parameters.