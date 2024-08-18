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


## Usage
The client is split into three panels: the camera settings panel, the image panel, and the tuning panel, in order from left to right.
The camera settings panel is where you can modify the settings of the camera. In general, this should only be used by people who know what they are doing.
The image panel is where the processed image is displayed. It will show the last image it received from the server, along with an fps counter in the bottom right corner. Sometimes this can be inaccurate, we know.
The tuning panel is the one that is safe to use. It is where you can modify the parameters of the vision processing algorithm. The parameters are split into two categories: the general parameters and the camera parameters. 
All parameters are camera specific, but they will stay the same in the client until you change them.

### The Camera Settings Panel
The camera settings panel is on the left side of the screen.
![](/readme-helpers/Left-panel.png)