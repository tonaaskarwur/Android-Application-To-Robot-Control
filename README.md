# Overview

Android application to wireless robot control. The application is built in Python based on the kivy library. It allows you to control a mobile robot built specifically for this project. The application consists of the main menu, selection of control, manual control, control by draw a route for robot and a window for drawing the robot's speed and direction.

## Application build

The easiest way is to install the file myapp-0.1-debug.apk.

If you want to change something in the code, you have to build the application again. The buildozer tool is used for this. Instruction on how to use the tool is available at this link [Buildozer](https://github.com/kivy/buildozer).

**When building the application, replace the generated file *buildozer.spec* with the one from this repository. If you don't do this, the application will not work correctly**

## How to use

First, run app_server.py on RaspberryPi. The console displays the address where the server listens for connections.

In mobile appplication after pressing the WI-Fi logo, it is possible to connect to the server that is on the robot. After the correct connection, the tick icon will appear. In the MANUAL CONTROL tab, you can set the speed of the robot, the direction of movement, turn on the indicator and change the turn by rotating the phone. In the AUTO CONTROL tab you can draw a route that the robot has to drive. In the DATABASE tab, after clicking on the database icon, the speed and direction of the robot will be drawn.

### Images

![Image 1](/Images/1.png)
![Image 2](/Images/2.png) 
![Image 3](/Images/3.png)
![Image 4](/Images/4.png)
![Image 5](/Images/5.png)

## Requirements

### To build app

* [Kivy](https://kivy.org/#home) - Library for development of applications
* [PyGame](https://www.pygame.org/news) - Library for making multimedia applications like games built on top of the SDL library
* [Pillow](https://pillow.readthedocs.io/en/stable/) - Imaging Library
* [Plyer](https://plyer.readthedocs.io/en/latest/#) - Library for accessing features of your hardware / platforms
* [Pyjnius](https://pyjnius.readthedocs.io/en/latest/) - Library for accessing Java classes

### To run server on RaspberryPi

* [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) - Package provides a class to control the GPIO on a Raspberry Pi.
* [netifaces](https://pypi.org/project/netifaces/) - Library to get the address(es) of the machine’s network interfaces from Python
* [Numpy](http://www.numpy.org) - Package for scientific computing

## Author

* **Przemysław Kanach** - [Przemysław Kanach](https://github.com/Przemoo16)
