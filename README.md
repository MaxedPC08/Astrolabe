FYRE Object Detection
======================
This is a super quick and dirty implementation of a floodfill object detection algorithm. It's not perfect, but it's a good starting point for a more robust implementation. The algorithm is based on the floodfill algorithm, which is a simple algorithm that fills in a region of pixels with a specific color. The algorithm works by starting at a seed pixel and then recursively filling in neighboring pixels that are within a certain color threshold. The algorithm is not perfect, but it's a good starting point for a more robust implementation.

Installation
------------
Clone this repository. Install the following dependencies on the coprocessor:

~~~
opencv-python
numpy
websockets
~~~

Install the following dependencies on the computer:
~~~
opencv-python
numpy
websockets
PyQt6
Tkinter
Pillow
~~~
Upload only RaspberryPiMain.py to the coprocessor. Create a params.txt file in the same directory as RaspberryPiMain.py with the same contents as those in this repository.

Usage
-----
To generate the parameters, run the Finetuner.py script on your computer. This script will open a window with the last saved image from the camera. Use the sliders to adjust the parameters until the object is detected correctly.
Make sure to copy the params.txt file to the coprocessor after generating the parameters.
To view the live stream of the camera, run the TkinterImageDisplay.py script on your computer. This script will open a window with the live stream of the camera. 
The RaspberryPiMain.py script should be run on the coprocessor. This script will connect to the computer and send the processed image to the computer. The computer will then display the processed image.
The coprocessor adds all the crosshairs and the highlighted object to the image. The computer only displays the processed image.
Set the SAVE_IMAGE variable in TkinterImageDisplay to True to save the image to the computer for tuning. Set it to False to skip saving the image.
Set the PROCESS_IMAGE variable in TkinterImageDisplay to True to process the image. Set it to False to skip processing the image. Use it in this mode for tuning.
