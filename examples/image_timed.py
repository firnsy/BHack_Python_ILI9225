# Copyright (c) 2017 Ballarat Hackerspace Inc.
# Author: Ian Firns
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.# Fixed by SwetyCore
from PIL import Image

import BHack_ILI9225 as TFT
from busio import SPI
import board

# Raspberry Pi configuration.
RS = board.D19
RST =board.D26

# BeagleBone Black configuration.
# RS = 'P9_15'
# RST = 'P9_12'
# SPI_PORT = 1
# SPI_DEVICE = 0

# Create TFT LCD display class.
spi = SPI(board.SCLK, board.MOSI, board.MISO)
disp = TFT.ILI9225(RS, rst=RST, spi=spi)

# Initialize display.
disp.begin()

# Load an image.
print('Loading image...')
image = Image.open('cat.jpg')

# Resize the image and rotate it so it's 176x220 pixels.
image = image.rotate(90).resize((176, 220))

print('Press Ctrl-C to exit')
while(True):
    # Draw the image on the display hardware.
    print('Drawing image')
    start_time = time.time()
    disp.display(image)
    end_time = time.time()
    print('Time to draw image: ' + str(end_time - start_time))
    disp.clear((0, 0, 0))
    disp.display()
