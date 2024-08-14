# Coprocessor
## Installation
Install the required dependencies by running `pip install -r requirements.txt` in the `Coprocessor` directory. Also, 
install [this apriltag library](https://github.com/swatbotics/apriltag) by Matt Zucker in the `Coprocessor` directory. Follow all 
the instructions in the README of the apriltag library to install it, including installing it system-wide. We 
*highly* recommend installing Astrolabe in a virtual environment to avoid conflicts with other python packages.


## Overview
The coprocessor is a python program that runs on the Raspberry Pi. It is responsible for processing the camera feed and
sending the processed data to the client via a websocket. It hosts a websocket server for each camera connected to it,
starting with port 50000. Each camera has its own process and handles requests independently. Every command is camera 
specific, so there is no main socket to send general commands to. The client will connect to the server and send bash-style
commands to the server. The server will then reply with either a bytes object or a json string.

# Usage
## Commands
### Processed Image ("processed_image", "pi")
The processed image command will return the processed image as a bytes object. This command will trigger the server to
take a picture, process it, and return the processed image. It will highlight the detected objects and add crosshairs
to the center of the detected objects. The processed image will be returned as a bytes object. There is no json data
returned when calling this function.
#### Parameters:
None
#### Example Usage:
```processed_image```, ```pi```

### Raw Image ("raw_image", "ri")
The raw image command will return the raw image as a bytes object. This command will trigger the server to
take a picture and return the processed image. The image will be returned as a bytes object. There is no json data
returned when calling this function.
#### Parameters:
None
#### Example Usage:
```raw_image```, ```ri```

### AprilTag Detection ("find_apriltag", "at")
The apriltag detection command will return the image with the apriltags highlighted as a bytes object. This command will trigger the server to
take a picture, locate the apriltag, highlight it, and send the image back. The apriltag will have green circle-ish objects on the corners and a red circle-ish blob in the center.
The processed image will be returned as a bytes object. There is no json data returned when calling this function.
#### Parameters:
None
#### Example Usage:
```find_apriltag```, ```at```

### Switch Color ("switch_color", "sc")
The switch color command will switch the color that the server is looking for. This command will trigger the server to 
switch the color that it is looking for. The server will reply with `"success"` if the color was switched. Otherwise,
it will reply with an error message like `{"error": "An error occurred when trying to switch colors"}`.
#### Parameters:
new_color: The index of the new color to switch to. This is an integer value where 0 is the first index.
#### Example Usage:
```sc -new_color=1```

### Save Colors ("color")
This function sets the colors that the server is looking for. This command will trigger the server to save the colors
to a json file, then you use the switch color command to switch between the colors. The server will reply with an error like `{"error": "An error occurred when trying to save colors"}`
if an error occurs, otherwise it will reply with `"success"`

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
```
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
