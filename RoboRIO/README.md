# RoboRIO
The contents of this directory contain the code implimentation that will allow the coprocessor to talk to the RoboRIO with websockets.
This is an example and a starting point, your implimentation may look slightly different depending on your team's paradigms and style.
Currently, Java is the only supported implimentation at this time.

## Installation
Unfortunatley, this program uses libraries that don't come pre-packaged with WPILib. This means that dependency installation is a little bit more involved than a `pip install`.

Once you have your WPI project has been created, it already sets up a build system (Gradle) for you. Gradle manages dependencies before they get sent off to the robot. In order to install dependencies, we need to tell Gradle to inject the dependency into the jarfile that it compiles, before it sends that information off to the robot. Start by opening the `build.gradle` file in your favorite text editor. Find the `dependencies` section. On most projects, this starts around line 50. Once you've found this section, you'll need to add a couple of lines to the end of this section. On a new line within the curly brackets that contain the dependency section, add a new line with this code: `compileOnly group: 'jakarta.websocket', name: 'jakarta.websocket-api', version: '2.2.0'`, and another new line with thise code: `implementation group: 'com.google.code.gson', name: 'gson', version: '2.11.0'`.

Voila! If done correctly, Gradle will include these dependencies in the jar file that runs on the RoboRIO. 

#### Note:
It is nessecary that you run a gradle build task with a stable internet connection before you deploy code to the robot, so that gradle can grab the dependencies from the web. If you aren't sure how to run a gradle build task, please look at an online tutorial or even the WPILib documentation, as the process is different between operating systems and IDEs. (Unless you're a CLI chad, where are my `./gradle build` brothers?).

*code implimentation stuff will go here when I'm done*
