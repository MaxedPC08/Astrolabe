# Computer Client
This directory contains a client for the websocket for use on a team's computer. It comes in the form of a tkinter 
application that can do most of the stuff required for tuning the parameters of the vision processing algorithm, seeing
errors, the processed image, and general information about the system. The client can also save the processed image to 
the computer for later use. None of the images are modified in any way, so the client can be used for tuning the parameters.
By no means is this client required for the vision processing algorithm to work. It is just a tool to help with tuning the
parameters and seeing the processed image. The code is also an example of how to interact with the server.

## Installation
To install all dependencies, run the following command on your machine from this directory:
```bash
pip install -r requirements.txt
```
## Important information
* To select a color, click on the image where the color is. This will set the color to the color of the pixel you clicked on.
* The client will not work if the server is not running. Make sure the server is running before starting the client.
* If you are getting really low fps, restart the server or let it cool down.


---

## Usage
The client is split into three panels: the camera settings panel, the image panel, and the tuning panel, in order from left to right.
The camera settings panel is where you can modify the settings of the camera. In general, this should only be used by people who know what they are doing.
The image panel is where the processed image is displayed. It will show the last image it received from the server, along with an fps counter in the bottom right corner. Sometimes this can be inaccurate, we know.
The tuning panel is the one that is safe to use. It is where you can modify the parameters of the vision processing algorithm. The parameters are split into two categories: the general parameters and the camera parameters. 
All parameters are camera specific, but they will stay the same in the client until you change them.
---
### The Camera Settings Panel
The camera settings panel is on the left side of the screen.
The camera settings panel is where you can modify the settings of the camera. In general, this should only be used by people who know what they are doing, seriously.
The settings are:
* Height - The height of the camera from the ground. Note that this unit is arbitrary, but it is the unit that the object detection distances will be in.
* Horizontal Resolution - The horizontal resolution of the camera. This is the width of the image.
* Vertical Resolution - The vertical resolution of the camera. This is the height of the image.
* Processing Scale - Before an image is processed, it is scaled down by this factor. This is useful for speeding up the processing of the image. It is an integer, and the resolution of the image will be divided by this number.
* Tilt Angle - The angle of the camera from the ground in ***RADIANS***. This is used to calculate the distance to the object. 0 is looking straight down and pi/2 is looking straight ahead. (note that you must enter the actual number, not something like pi/2. pi/2 is 1.570796326 in case you need that 😉)
* Horizontal FOV - The horizontal field of view of the camera in ***RADIANS***. This is used to calculate the distance to the object. This is the angle that the camera can see from left to right. **Note that this is not the angle that is marketed usually. If you do not know this, skip it for a minute.**
* Vertical FOV - The vertical field of view of the camera in ***RADIANS***. This is used to calculate the distance to the object. This is the angle that the camera can see from top to bottom. **Note that this is not the angle that is marketed usually. If you do not know this, skip it for a minute.**

Now, we have a handy dandy calculator for the Horizontal and Vertical FOV. If you know the aspect ratio and the 
diagonal FOV (the one that is usually marketed), you can use this to calculate the actual FOV. Simply 
enter the aspect ratio and the diagonal FOV, and the calculator will do the rest. The aspect ratio is the ratio of the 
width to the height of the image. For example, 16:9 is 16/9. The diagonal FOV is the angle that the camera can see from 
one corner to the other. This is the angle that is usually marketed. **Note that this is in degrees, as that is what 
most cameras use**. The calculator will automatically fill in the Horizontal and Vertical FOV for you. 

Lastly, we have the "Additional Flags" section. This is where you can add additional flags to the camera. They must be in 
python dictionary form, like {"CAP_PROP_EXPOSURE": 0, "CAP_PROP_BRIGHTNESS": 150}. The key is the flag, and the value is the value of the flag.
Note that not all cameras respond to all flags. This is not an issue, but simply a fact of life. 
The availible flags are:

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

Lastly are the "Send Values", "Get Info", and "Get Hardware Info" buttons. The "Send Values" button sends the values to 
the server. The "Get Info" button gets the information about the camera from the server and outputs it in the quasi-terminal in the left-most panel. 
The "Get Hardware Info" button gets the hardware information about the camera from the server and also outputs it in the terminalesque field in the left panel.

---
## The Image Panel

The image panel is in the middle of the screen. It displays the image from the server. If the server is not sending images, it will not change the image.
It has an FPS counter in the bottom right corner. This is the frames per second that the client is receiving from the server. Sometimes this can be wildly inaccurate, and we are working on that. If your FPS is greater than 1000, it is likely that the FPS counter is inaccurate.
All the images on the screen are not modified by the client in any way, so the client can be used for tuning the parameters.

---
## The Tuning Panel
The tuning panel is on the right side of the screen. It is where you can tune the parameters of the vision processing algorithm.
The first field on this side is where you enter the ip address and port of the server. The ip is usually 10.42.0.118, but it can be other things. Each camera hosted by the server has a dedicated port, starting at 50000. Click the "Update IP and Port" button to connect to the server.


The next line has the `Load`, `Save`, `Add Color`, and `Delete Color` buttons, along with a drop-down menu to select the color. The `Load` button opens a file dialog where you can load a color file. The `Save` button saves the colors to a file. The `Add Color` button adds a color to the list of colors. The `Delete Color` button deletes the selected color from the list of colors. 
Use the dropdown menu to select the color you want to modify and use.

The next section is the mode drop-down menu. This is where you can select the mode of the vision processing algorithm. The modes are:
* Apriltag - This mode is for detecting apriltags. It will draw circles at the corners and centers of the apriltags in the image
* Processed - This mode is for showing the processed image. It will show the image after the vision processing algorithm has been run. It highlights the detected object and adds crosshairs to the center of the object.
* Raw - This mode is for showing the raw image. It will show the image as it comes from the camera.
* Headless piece detection - this mode is for detecting the game pieces without a camera output. It will print a dictionary of information about the detected game pieces in the terminal.
* Headless apriltag detection - this mode is for detecting apriltags without a camera output. It will print a dictionary of information about the detected apriltags in the terminal.

The next section is the color detection section. This is one of the two ways you can select a color for detection. You can either modify these values via the sliders, or click directly on the image to set the target color to where you clicked. This is where you can modify the parameters of the color detection algorithm. The parameters are:
* Red - The red value of the color.
* Green - The green value of the color.
* Blue - The blue value of the color.
* Difference - The difference between the color and the pixel in the image. This is the maximum difference between the color and the pixel in the image. The higher this number, the more pixels will be detected as the color.
* Blur - The amount of blur to apply to the image before detecting the color. This is useful for removing noise from the image, thus it can help with the detection of the color, but it can also be resource-intensive.


The Current Color block shows the current color that is selected for visualization. The `Save Image` check box is where 
you can select whether to save the image to the computer. The terminal is where the output of the server is displayed. If you are running anything in headless mode, this is where the output will be displayed.