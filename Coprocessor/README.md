# Coprocessor
## Installation
Install the required dependencies by running `pip install -r requirements.txt` in the `Coprocessor` directory. Also, 
install [this apriltag library](https://github.com/swatbotics/apriltag) by Matt Zucker in the `Coprocessor` directory. Follow all 
the instructions in the README of the apriltag library to install it, including installing it system-wide. We 
*highly* recommend installing Astrolabe in a virtual environment to avoid conflicts with other python packages. To install 
Astrolabe automatically on a fresh Raspberry Pi, run the `install.sh` script in the `Coprocessor` directory using the following command:
```bash
wget -O - https://raw.githubusercontent.com/MaxedPC08/Astrolabe/master/Coprocessor/install.sh | sudo bash
```


## Overview
The coprocessor is a python program that runs on the Raspberry Pi. It is responsible for processing the camera feed and
sending the processed data to the client via a websocket. It hosts a websocket server for each camera connected to it,
starting with port 50000. Each camera has its own process and handles requests independently. Every command is camera 
specific, so there is no main socket to send general commands to. The client will connect to the server and send bash-style
commands to the server. The server will then reply with either a bytes object or a json string.

## Useful information
* The port that the server listens on is 50000 + the camera number. For example, if you have two cameras, the ports will be 50000 and 50001.
* The server will always reply to a request. It will reply either with a bytes object or a json string. This is outlined in the command's documentation.
* The server defaults to looking for tags in the family 36h11. This can be changed in the [apriltag.py](apriltag.py) file.
* On some rare occasions, the server may not be able to open/find the camera. This is usually due to the camera being in use by another program. If this happens, restart the server.
---
# Usage
## Commands
### Processed Image ("processed_image", "pi")
The processed image command will return the processed image as a bytes object. This command will trigger the server to
take a picture, process it, and return the processed image. It will highlight the detected objects and add cross-hairs
to the center of the detected objects. The processed image will be returned as a bytes object. There is no json data
returned when calling this function.
#### Parameters:
None
#### Example Usage:
```processed_image```, ```pi```
---
### Raw Image ("raw_image", "ri")
The raw image command will return the raw image as a bytes object. This command will trigger the server to
take a picture and return the processed image. The image will be returned as a bytes object. There is no json data
returned when calling this function.
#### Parameters:
None
#### Example Usage:
```raw_image```, ```ri```
---
### AprilTag Detection Image ("find_apriltag", "at")
The apriltag detection command will return the image with the apriltags highlighted as a bytes object. This command will trigger the server to
take a picture, locate the apriltag, highlight it, and send the image back. The apriltag will have green circle-ish objects on the corners and a red circle-ish blob in the center.
The processed image will be returned as a bytes object. There is no json data returned when calling this function.
#### Parameters:
None
#### Example Usage:
```find_apriltag```, ```at```
---
### Switch Color ("switch_color", "sc")
The switch color command will switch the color that the server is looking for. This command will trigger the server to 
switch the color that it is looking for. The server will reply with the output of [info](#info-info-i) if the color was switched. Otherwise,
it will reply with an error message like `{"error": "An error occurred when trying to switch colors"}`.
#### Parameters:
new_color: The index of the new color to switch to. This is an integer value where 0 is the first index.
#### Example Usage:
```sc -new_color=1```
---
### Save Colors ("color")
This function sets the colors that the server is looking for. This command will trigger the server to save the colors
to a json file, then you use the switch color command to switch between the colors. The server will reply with an error like `{"error": "An error occurred when trying to save colors"}`
if an error occurs, otherwise it will reply with the output of [info](#info-info-i).

#### Parameters:
values: A list of dictionaries containing the red, green, blue, difference, and blur values of the colors to save, followed by the index of the desired active color. 
The difference and blur help with vision processing. 

The red, green, and blue values are the RGB values of the color being looked for. 

The difference is the maximum difference between the color in the image and the color being looked for. 

The blur represents the amount of blurring to do before processing the image. Generally, blurring the image slightly 
before processing helps with object detection, but it can be resource-intensive.

The values are integers in the range of 0-255. The blur is an integer in the range of 0-10. 
The difference is an integer in the range of 0-255.

#### Example Usage:
```bash
sp -values=[{"red": 250.0, 
                "green": 196.0, 
                "blue": 183.0, 
                "difference": 7, 
                "blur": 3}, 
           {"red": 35, 
                "green": 0.0, 
                "blue": 0.0, 
                "difference": 40.0, 
                "blur": 0.0}, 
           0]
```
---
## Set Camera Parameters ("set_camera_params", "scp")
This function sets the camera parameters for the camera. It takes a dictionary of camera parameters and sets them. The server will reply with the same output of [info](#info-info-i) if the parameters were set. Otherwise, it will reply with an error message like `{"error": "An error occurred when trying to set the camera parameters"}`.

### Parameters:
`values`: A dictionary containing the camera parameters to set. The possible parameters are:
* Height (`"height"`): The height of the camera off the ground. This is used to calculate the distance to the object.
* Tilt angle (`"tilt_angle"`): The angle of the camera relative to the ground. This is used to calculate the distance to the object. 0 is straight down, pi/2 is straight ahead.
* Horizontal Resolution (`"horizontal_resolution_pixels"`): The horizontal resolution of the desired image. This cannot exceed the camera's maximum resolution.
* Vertical Resolution (`"vertical_resolution_pixels"`): The vertical resolution of the desired image. This cannot exceed the camera's maximum resolution.
* Processing Scale (`"processing_scale"`): The scale to process the image at. This is an integer greater than 1. The resolution of the camera will be divided by this number for processing. 
This can help with performance. To calculate the resolution of the image coming from the camera, divide the camera's resolution by the processing scale.
* Horizontal Field of View (`"horizontal_field_of_view_radians"`): The horizontal field of view of the camera. This is the angle that the camera can see. This is used to calculate the distance to the object. It is measured in radians, not degrees!
* Vertical Field of View (`"vertical_field_of_view_radians"`): The vertical field of view of the camera. This is the angle that the camera can see. This is used to calculate the distance to the object. It is measured in radians, not degrees! If you do not know the horizontal field of view, see the Client README and client application as it has a built-in calculator using the aspect ratio and the diagonal FOV, which is what companies usually market.
* Horizontal Focal Length (`"horizontal_focal_length"`): The horizontal focal length of the camera. This is used to calculate the distance to the object, we do not expect you to know this value. It too can be calculated in the client application.
* Vertical Focal Length (`"vertical_focal_length"`): The vertical focal length of the camera. This is used to calculate the distance to the object, we do not expect you to know this value. It too can be calculated in the client application.
* Additional Flags (`"additional_flags"`): These are additional flags to pass to the camera. This should be a dictionary with the flag name as the key and the flag value as the value. The value is always an integer. The possible flags are:
  * `"CAP_PROP_APERTURE"`: The aperture of the camera. This is the size of the opening in the lens that lets light in.
  * `"CAP_PROP_AUTOFOCUS"`: Whether the camera should autofocus.
  * `"CAP_PROP_AUTO_EXPOSURE"`: Whether the camera should automatically adjust the exposure.
  * `"CAP_PROP_BACKLIGHT"`: The backlight compensation of the camera.
  * `"CAP_PROP_BRIGHTNESS"`: The brightness of the camera.
  * `"CAP_PROP_BUFFERSIZE"`: The size of the buffer for the camera.
  * `"CAP_PROP_CONTRAST"`: The contrast of the camera.
  * `"CAP_PROP_CONVERT_RGB"`: Whether the camera should convert the image to RGB. Do not mess with this unless you have problems.
  * `"CAP_PROP_EXPOSURE"`: The exposure of the camera.
  * `"CAP_PROP_FOCUS"`: The focus of the camera.
  * `"CAP_PROP_FPS"`: The frames per second of the camera. Leave this alone unless you know what you are doing.
  * `"CAP_PROP_FRAME_HEIGHT"`: The height of the camera's frame. Leave this alone unless you know what you are doing.
  * `"CAP_PROP_FRAME_WIDTH"`: The width of the camera's frame. Leave this alone unless you know what you are doing.
  * `"CAP_PROP_GAIN"`: The gain of the camera.
  * `"CAP_PROP_GAMMA"`: The gamma of the camera.
  * `"CAP_PROP_HUE"`: The hue of the camera.
  * `"CAP_PROP_ISO_SPEED"`: The ISO speed of the camera.
  * `"CAP_PROP_POS_FRAMES"`: The position of the frames of the camera.
  * `"CAP_PROP_POS_MSEC"`: The position of the milliseconds of the camera. This usually does not do anything, but it can help with debugging.
  * `"CAP_PROP_SATURATION"`: The saturation of the camera.
  * `"CAP_PROP_SHARPNESS"`: The sharpness of the camera.
  * `"CAP_PROP_TEMPERATURE"`: The temperature of images from the camera.
  * `"CAP_PROP_TRIGGER"`: The trigger speed of the camera. We are not entirely sure what this does. It seems to have no effect.
  * `"CAP_PROP_WHITE_BALANCE_BLUE_U"`: The white balance blue value of the camera.
  * `"CAP_PROP_WHITE_BALANCE_RED_V"`: The white balance red value of the camera.
  * `"CAP_PROP_ZOOM"`: The zoom of the camera.

#### Example Usage:
```json lines
scp -values={"height": 0.0, 
                "tilt_angle": 0.0, 
                "horizontal_resolution_pixels": 640, 
                "vertical_resolution_pixels": 480, 
                "processing_scale": 2, 
                "horizontal_field_of_view_radians": 1.3962634015954636, 
                "vertical_field_of_view_radians": 1.0471975511965976, 
                "horizontal_focal_length": 0.0, 
                "vertical_focal_length": 0.0, 
                "additional_flags": {"CAP_PROP_AUTO_EXPOSURE": 1, 
                                    "CAP_PROP_AUTOFOCUS": 1, 
                                    "CAP_PROP_BRIGHTNESS": 128, 
                                    "CAP_PROP_CONTRAST": 32, 
                                    "CAP_PROP_EXPOSURE": -6, 
                                    "CAP_PROP_FPS": 30, 
                                    "CAP_PROP_GAIN": 0, 
                                    "CAP_PROP_GAMMA": 100, 
                                    "CAP_PROP_HUE": 0, 
                                    "CAP_PROP_ISO_SPEED": 0, 
                                    "CAP_PROP_SATURATION": 32, 
                                    "CAP_PROP_SHARPNESS": 0, 
                                    "CAP_PROP_WHITE_BALANCE_BLUE_U": 0, 
                                    "CAP_PROP_WHITE_BALANCE_RED_V": 0}}
```
---
## Find Piece ("find_piece", "fp")
This function will return the location of the piece in the current image. The server will take a picture, process it, and return the location of the piece. It considers only the currently selected color, which can be changed with [the switch color command](#switch-color-switch_color-sc).
The location of the object is given in the form of a json string of a dictionary containing the `distance`, `angle`, and `center` of the object. 
* `distance` is the distance to the object in whatever unit the height parameter in the [set_camera_params](#set-camera-parameters-set_camera_params-scp) is in.
* `angle` is the angle to the object in radians.
* `center` is the center of the object in the image in the form of a tuple of the x and y coordinates. 

If the object is not found, the server will reply with `{distance: -1, angle: -1, center: (-1, -1)}`.
If an error occurs, the server will reply with an error message like `{"error": "Failed to open camera."}`.


### Parameters:
None

### Example Usage:
```shell
fp
```
---
## Find Apriltag ("find_apriltag", "fa")
This function returns lots of information about the apriltags in the image. It comes in the form of a `json` string with a list of dictionaries for each tag found. An example message is:
```json
[{"tag_id": 13, "position": [-0.1, -0.2, 1.1], "orientation": [0.2, -6.2e-05, 0.018], "distance": 1.0, "horizontal_angle": -0.2, "vertical_angle": -0.67},
  {"tag_id": 14, "position": [0.1, 0.2, 1.1], "orientation": [0.2, -6.2e-05, 0.018], "distance": 1.0, "horizontal_angle": 0.2, "vertical_angle": 0.67}]
```
Let's break this down by the keys:
* `tag_id`: The id of the tag found.
* `position`: The position of the tag in the form of a list of the x, y, and z coordinates on the camera's coordinate plane. It is in the unit that the size of the apriltag is in. This is defined in the [constants.py](constants.py) file.
* `orientation`: The orientation of the tag in the form of a list of the x, y, and z angles. This is in radians. Think of these angles as the angles from the tag to the camera, not the other way around.
* `distance`: The distance to the tag in whatever unit the apriltag size is in.
* `horizontal_angle`: The horizontal angle to the tag in radians. Whether this is positive or negative depends on if your camera mirrors the image by default. Test it.
* `vertical_angle`: The vertical angle to the tag in radians.

### Parameters:
None

### Example Usage:
```shell
fa
```
---
## Info ("info", "i")
This function returns information about the current camera. It defaults to camera mode, but it can also do hardware mode if the user passes `-h=True`. In camera mode, it returns a json string with the following keys:
* `cam_name`: The name of the camera. This is the path to the camera.
* `identifier`: The identifier of the camera. This is a unique identifier for the camera, assigned by our program. It is usually the serial number of the camera, the manufacturer, and the model number. If there are two cameras with the same serial number, the program will append the platform (essentially the id of the usb port the camera is plugged into) to the end of the identifier.
* `horizontal_focal_length`: The horizontal focal length of the camera. This is used to calculate the distance to the object.
* `vertical_focal_length`: The vertical focal length of the camera. This is used to calculate the distance to the object as well (shocker).
* `height`: The height of the camera off the ground. This is used to calculate the distance to the object.
* `horizontal_resolution_pixels`: The horizontal resolution of the camera. This is the number of pixels in the horizontal direction.
* `vertical_resolution_pixels`: The vertical resolution of the camera. This is the number of pixels in the vertical direction.
* `processing_scale`: The scale to process the image at. This is an integer greater than 1. The resolution of the camera will be divided by this number for processing. This can help with performance. The output resolution of the camera is the resolution of the camera divided by the processing scale.
* `tilt_angle_radians`: The angle of the camera relative to the ground. This is used to calculate the distance to the object. 0 is straight down, pi/2 is straight ahead.
* `horizontal_field_of_view_radians`: The horizontal field of view of the camera. This is the angle that the camera can see. This is used to calculate the distance to the object. It is measured in radians, not degrees!
* `vertical_field_of_view_radians`: The vertical field of view of the camera. This is the angle that the camera can see. This is used to calculate the distance to the object. It is measured in radians, not degrees!
* `color_list`: A list of dictionaries containing the red, green, blue, difference, and blur values of the colors to save, followed by the index of the desired active color. The difference and blur help with vision processing. The red, green, and blue values are the RGB values of the color being looked for. The difference is the maximum difference between the color in the image and the color being looked for. It is a somewhat arbitrary value. The blur represents the amount of blurring to do before processing the image. 
* `active_color`: The index of the active color. This is the index of the color in the color list that the server is currently looking for.

In hardware mode, it returns a json string with the following keys:
* `temperature`: The temperature of the board in Celsius.
* `cpu_usage`: The percentage of the CPU being used.
* `memory_usage`: The percentage of the memory being used.
* `disk_usage`: The percentage of the disk being used.
* `system_info`: A dictionary containing information about the system. The value of the information in this dictionary varies widely depending on the hardware. The keys are:
  * `system`: The system the board is running.
  * `node_name`: The name of the board.
  * `release`: The release of the system.
  * `version`: The version of the system.
  * `machine`: The architecture of the cpu.
  * `processor`: The processor the system is running on. This is usually empty, but in some cases it is not. We are aware of this issue.

### Parameters:
`-h`: A boolean value that dictates whether the function should return hardware information. If this is `True`, the function will return hardware information. If this is `False`, the function will return camera information. This is optional, and the default valeu is False.

### Example Usage:
```shell
info -h=True
```
or 
```shell
info
```

