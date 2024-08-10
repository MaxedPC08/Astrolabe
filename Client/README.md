# Computer Client
This directory contains everything that will be run locally on a team laptop.

## Installation
To install all dependencies, run the following command on your machine from this directory:
```pip install -r requirements.txt```

Upload only RaspberryPiMain.py to the coprocessor. Create a params.txt file in the same directory as RaspberryPiMain.py with the same contents as those in this repository.

## Usage
To generate the parameters, run the Finetuner.py script on your computer. This script will open a window with the last saved image from the camera. Use the sliders to adjust the parameters until the object is detected correctly.
Make sure to copy the params.txt file to the coprocessor after generating the parameters.
To view the live stream of the camera, run the TkinterImageDisplay.py script on your computer. This script will open a window with the live stream of the camera. 
The RaspberryPiMain.py script should be run on the coprocessor. This script will connect to the computer and send the processed image to the computer. The computer will then display the processed image.
The coprocessor adds all the crosshairs and the highlighted object to the image. The computer only displays the processed image.
Set the SAVE_IMAGE variable in TkinterImageDisplay to True to save the image to the computer for tuning. Set it to False to skip saving the image.
Set the PROCESS_IMAGE variable in TkinterImageDisplay to True to process the image. Set it to False to skip processing the image. Use it in this mode for tuning.
