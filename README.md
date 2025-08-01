# Astrolabe 
Now with Reinforcement Learning Motion Control, meaning your robot will constantly improve its motion control skills as it drives around the field!

For installation instructions, please see the [Installation](#installation) section below.

## Overview
Astrolabe is a vision processing and reinforcement learning motion control software designed specifically for FRC teams. Astrolabe has two ends, a server, usually the 
coprocessor, and a client, usually the driver station or the robot, whichever is connected to the server. The server is 
responsible for processing the image and sending the results to the client. The client is responsible for interacting 
with the server in a UI. The server and client communicate over an ethernet connection. The server is started by 
running the [main.py](Coprocessor/main.py) script in the `Coprocessor` directory. Each camera has its own process and 
handles requests independently. There is no main socket to send general commands to. The client will connect to the 
server and send bash-style commands to the server. The server will then reply with either a bytes object or a json 
string.

## Features
* The server can process images from any number of cameras, limited only by the hardware it is running on.
* Full, color based object detection and location calculation.
* AprilTag detection and location, pose, and direction calculation.
* Websocket communication between the server and the client.
* Reinforcement learning motion control algorithms that can be run on the coprocessor, constantly learning and improving the robot's motion control.

## Why Astrolabe?
* Astrolabe is a vision processing software that is designed to be easy to use and easy to understand.
  * The client is built to be intuitive for anyone to use, even non-programmers.
  * The unique bash-style command system allows for easy and familiar communication between the client and the server. No more wrestling with JSON strings to send simple commands!
* Astrolabe is designed to be modular and extensible.
  * The server is a relatively simple Python script that can be easily modified to fit your needs, whether that be adding new vision processing algorithms or changing the way the server communicates with the client.
  * The client is built with a modular design in mind, so adding new features is as simple as adding a new function to the server's code.
* Astrolabe is designed to be fast and efficient.
  * While the entire repository is written in Python, the server uses highly optimized libraries like OpenCV and NumPy to process images as quickly as possible, approaching the speed of libraries written in C++ while maintaining the ease of use of Python.
  * The server is built with a simple and efficient design, so it can run on even the most modest of hardware. For example, the server can host three cameras on a Raspberry Pi 3B without breaking a sweat.
  * The server only performs an operation when it is requested by the client, so it is not wasting resources on processing images that are not needed.
* Astrolabe is designed to be reliable and robust.
  * The server is built with error handling in mind, so it can recover from most errors without causing any problems. 
  * If a major error does occur, it will only affect the camera that caused the error, so the other cameras can continue to function normally.
* Astrolabe uses separate processes for each camera.
  * Astrolabe uses a websocket server for each camera. This means that each camera has its own process and handles requests independently. This allows for better performance and reliability, as an error in one camera will not affect the others.
  * The server is designed to be able to handle any number of cameras, limited only by the hardware it is running on. Currently, Pi Cameras are not supported, but support for them is planned in the near future.
  * Each camera can be used for a different purpose, such as tracking the robot, detecting game pieces, or detecting the field elements. This allows for a wide range of vision processing tasks to be performed simultaneously.
  * Also, each camera can have its own settings, such as exposure, resolution, and frame rate. This allows for each camera to be optimized for its specific task.
  * The client can connect to any camera by specifying the camera's port number. This allows for easy switching between cameras, or even connecting to multiple cameras at once.
* Astrolabe does not require a dedicated coprocessor.
  * We understand that teams may have a limited number of coprocessors, so we designed Astrolabe to be able to run in parallel with other software that may be running on the coprocessor. This allows teams to use Astrolabe without having to dedicate a coprocessor to it.
* Astrolabe is easy to install and use. Just run the installation script on the coprocessor, and you are ready to go!
  * The installation script will install all the necessary dependencies and set up the server to run automatically on boot.
  * The client is a simple web interface that can be accessed from any device on the same network as the coprocessor. Just connect to the coprocessor's IP address and you are ready to go!

## Installation
Install the required dependencies by running pip install -r requirements.txt in the Coprocessor directory. Also, install this apriltag library by Matt Zucker in the Coprocessor directory. Follow all the instructions in the README of the apriltag library to install it, including installing it system-wide. We highly recommend installing Astrolabe in a virtual environment to avoid conflicts with other python packages. To install Astrolabe automatically on a fresh Raspberry Pi, run the install.sh script in the Coprocessor directory using the following command:

```wget -O - https://raw.githubusercontent.com/MaxedPC08/Astrolabe/master/Coprocessor/install.sh | sudo bash```

 From there, to run the app, simply insert a USB drive into the coprocessor, connect a camera, and connect to the ip address of the coprocessor! This is configured specifically for the default FRC VH109 Radio, so you will have the best luck with that.
