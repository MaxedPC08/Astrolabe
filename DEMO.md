## If you are here, you are probably looking for how to run Astrolabe. Welcome!

### Below are installation instructions and hardware requirements for Astrolabe. If you do not have these, here is a video demo of Astrolabe in action. [Demo Video](https://photos.app.goo.gl/d8d1BrXxFQ55kBTw8) Additionally, the robot (Number 5480, second farthest from the camera) in [this video](https://photos.app.goo.gl/TB7kf1TqXvu61tkAA) is a swerve drive robot using Astrolabe to align itself with an AprilTag in real time.

#### To see Astrolabe's full potential, you need an FRC robot with a swerve drive and the below hardware. 

---
### For Astrolabe, you need to have the following hardware:
- A Raspberry Pi 3B+ or later
- A camera that is compatible with the Raspberry Pi (e.g., Raspberry Pi Camera Module,
  USB webcam, etc.)
- A USB drive (optional, for saving images and videos)
- An SD card with Raspberry Pi OS installed (a clean install of the latest 64-bit lite version is recommended)
- A way to connect to the Raspberry Pi (e.g., SSH, VNC, etc.)

### To install Astrolabe, please follow the steps outlined in the [Installation Guide](README.md#installation).

For a desktop demo, simply connect the Raspberry Pi to your network, and connect to `raspberrypi.local:5000` (using raspberrypi.local only for Linux and Mac computers), or directly to the IP address of the Raspberry Pi. Astrolabe has a neat little feature where it finds its own IP address and writes it to an inserted USB drive. Please view the below video for more information on Astrolabe's features and how to use it.

Note that the Reinforcement Learning motion control feature is not availible in the web interface, but there is a demo available in [this file](Coprocessor/Reinforcement/demos/1d_momentum_sim.py). It includes a stipped down version of the Astrolabe code that can be run alone (all you need is that file and opencv (for visualization)).

