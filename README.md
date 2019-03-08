# Introduction

This repo contains:

* The Python based server meant to run on a RaspberryPi 2 (root folder)
* The Arduino sketch for the servo position detector (Arduino folder)
* The schematic for the additional PCB (hw folder)

# The server

## Development environment

Within the development environment both the servo and the Arduino are mocked.

### Requirements
* Python 2.7
* (Windows only) Install the VC++ compiler for Python 2.7 (http://www.microsoft.com/en-us/download/details.aspx?id=44266)

### Setup
I recommend using `pip` and `virtualenv`. One way to do so is:

1. Download PyCharm (https://www.jetbrains.com/pycharm/download/) - Community Edition is sufficient
1. Open this repository
1. Set interpreter to Python2.7
    1. Go to "File" -> "Settings"
    1. Search for "Interpreter"
    1. Set to Python 2.7
1. Open `epos_control_server.py`
1. PyCharm should now display that some requirements are missing -> click "Install requirements"

### Run

`python epos_control_server.py`

## Production

Ready-to-use SD card images can be built following the instructions at https://github.com/j-be/vj-control-server-buildenv

# Arduino

Download the Arduino IDE (https://www.arduino.cc) and follow the usual Arduino
procedures as described at https://www.arduino.cc/en/Guide/ArduinoUno.

# Unity3D

The API can be found at https://github.com/j-be/vj-unity-apis. Follow the
instructions there. For this server you need:

* `AbstractSocketioClient.cs`
* `ServoControllerClient.cs`
