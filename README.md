# Astrolabe (now with nix!)
Am I going to add poetry2nix? no
## Overview
Astrolabe is a vision processing software designed specifically for FRC teams. Astrolabe has two ends, a server, usually the 
coprocessor, and a client, usually the driver station or the robot, whichever is connected to the server. The server is 
responsible for processing the image and sending the results to the client. The client is responsible for interacting 
with the server in a UI. The server and client communicate over an ethernet connection. The server is started by 
running the [main.py](Coprocessor/main.py) script in the `Coprocessor` directory. The client is started by running [main.py](Client/main.py) script in the `Client` directory. The server hosts a 
websocket server for each camera connected to it, starting with port 50000. Each camera has its own process and 
handles requests independently. There is no main socket to send general commands to. The client will connect to the 
server and send bash-style commands to the server. The server will then reply with either a bytes object or a json 
string.

## Features
* The server can process images from any number of cameras, limited only by the hardware it is running on.
* Full, color based object detection and location calculation.
* AprilTag detection and location, pose, and direction calculation.
* Websocket communication between the server and the client.

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
* Astrolabe is easy to install and use.
  * The server and client are both written in Python, so they can be run on any platform that supports Python. This includes Windows, Mac, and Linux.
  * The client has a `requirements.txt` file that lists all of the dependencies that need to be installed. This makes it easy to install all of the required libraries with a single command.
  * The server has a bash script that installs all of the required dependencies. This makes it easy to get the server up and running, even if you are not familiar with Python.
  * The client has a `README.md` file that explains how to use the client. This makes it easy to get started with the client, even if you are not familiar with the code.
  * The server has a `README.md` file that explains how to use the server. This makes it easy to get started with the server, even if you are not familiar with the code.

## Installation
Installations for the coprocessor and the client are different. The instructions for the coprocessor are in the
[Coprocessor's README file](Coprocessor/README.md). The instructions for the client are in the 
[Client's README file](Client/README.md). The instructions for the robot code implimentation are in the [RoboRIO README file](RoboRIO/README.md).
