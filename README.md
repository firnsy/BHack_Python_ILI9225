# BHack Python ILI9225

Python library to control an ILI9225 TFT LCD display. Allows simple drawing on the display without installing a kernel module.
This library is compatible with both Python 3 (recommended) and Python 2.

## Installation

### Python 3 (Recommended)

For all platforms (Raspberry Pi and Beaglebone Black) make sure you have the following dependencies:
```
sudo apt-get update
sudo apt-get install build-essential python3-dev python3-smbus python3-pip python3-imaging python3-numpy
```

For a Raspberry Pi make sure you have the RPi.GPIO library by executing:

```
sudo pip3 install RPi.GPIO
```

For a BeagleBone Black make sure you have the Adafruit_BBIO library by executing:

```
sudo pip3 install Adafruit_BBIO
```

Install the library by downloading with the download link on the right, unzipping the archive, navigating inside the library's directory and executing:

```
sudo python3 setup.py install
```

### Python 2

For all platforms (Raspberry Pi and Beaglebone Black) make sure you have the following dependencies:
```
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging python-numpy
```

For a Raspberry Pi make sure you have the RPi.GPIO library by executing:

```
sudo pip install RPi.GPIO
```

For a BeagleBone Black make sure you have the Adafruit_BBIO library by executing:

```
sudo pip install Adafruit_BBIO
```

Install the library by downloading with the download link on the right, unzipping the archive, navigating inside the library's directory and executing:

```
sudo python setup.py install
```


## Examples

See example of usage in the examples folder.

Ballarat Hackerspace Inc. invests time and resources providing this open source code, please support Ballarat Hackerspace and open-source hardware by becoming a member/sponsor!

Written by Ian Firns for Ballarat Hackerspace Inc.

MIT license, all text above must be included in any redistribution
