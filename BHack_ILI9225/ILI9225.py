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
# THE SOFTWARE.
import numbers
import time
import numpy as np

from PIL import Image
from PIL import ImageDraw

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# ILI9225 screen size
ILI9225_TFTWIDTH                = 176
ILI9225_TFTHEIGHT               = 220

# ILI9225 LCD Registers
ILI9225_DRIVER_OUTPUT_CTRL      = 0x01 # Driver Output Control
ILI9225_LCD_AC_DRIVING_CTRL     = 0x02 # LCD AC Driving Control
ILI9225_ENTRY_MODE              = 0x03 # Entry Mode
ILI9225_DISP_CTRL1              = 0x07 # Display Control 1
ILI9225_BLANK_PERIOD_CTRL1      = 0x08 # Blank Period Control
ILI9225_FRAME_CYCLE_CTRL        = 0x0B # Frame Cycle Control
ILI9225_INTERFACE_CTRL          = 0x0C # Interface Control
ILI9225_OSC_CTRL                = 0x0F # Osc Control
ILI9225_POWER_CTRL1             = 0x10 # Power Control 1
ILI9225_POWER_CTRL2             = 0x11 # Power Control 2
ILI9225_POWER_CTRL3             = 0x12 # Power Control 3
ILI9225_POWER_CTRL4             = 0x13 # Power Control 4
ILI9225_POWER_CTRL5             = 0x14 # Power Control 5
ILI9225_VCI_RECYCLING           = 0x15 # VCI Recycling
ILI9225_RAM_ADDR_SET1           = 0x20 # Horizontal GRAM Address Set
ILI9225_RAM_ADDR_SET2           = 0x21 # Vertical GRAM Address Set
ILI9225_GRAM_DATA_REG           = 0x22 # GRAM Data Register
ILI9225_GATE_SCAN_CTRL          = 0x30 # Gate Scan Control Register
ILI9225_VERTICAL_SCROLL_CTRL1   = 0x31 # Vertical Scroll Control 1 Register
ILI9225_VERTICAL_SCROLL_CTRL2   = 0x32 # Vertical Scroll Control 2 Register
ILI9225_VERTICAL_SCROLL_CTRL3   = 0x33 # Vertical Scroll Control 3 Register
ILI9225_PARTIAL_DRIVING_POS1    = 0x34 # Partial Driving Position 1 Register
ILI9225_PARTIAL_DRIVING_POS2    = 0x35 # Partial Driving Position 2 Register
ILI9225_HORIZONTAL_WINDOW_ADDR1 = 0x36 # Horizontal Address Start Position
ILI9225_HORIZONTAL_WINDOW_ADDR2 = 0x37 # Horizontal Address End Position
ILI9225_VERTICAL_WINDOW_ADDR1   = 0x38 # Vertical Address Start Position
ILI9225_VERTICAL_WINDOW_ADDR2   = 0x39 # Vertical Address End Position
ILI9225_GAMMA_CTRL1             = 0x50 # Gamma Control 1
ILI9225_GAMMA_CTRL2             = 0x51 # Gamma Control 2
ILI9225_GAMMA_CTRL3             = 0x52 # Gamma Control 3
ILI9225_GAMMA_CTRL4             = 0x53 # Gamma Control 4
ILI9225_GAMMA_CTRL5             = 0x54 # Gamma Control 5
ILI9225_GAMMA_CTRL6             = 0x55 # Gamma Control 6
ILI9225_GAMMA_CTRL7             = 0x56 # Gamma Control 7
ILI9225_GAMMA_CTRL8             = 0x57 # Gamma Control 8
ILI9225_GAMMA_CTRL9             = 0x58 # Gamma Control 9
ILI9225_GAMMA_CTRL10            = 0x59 # Gamma Control 10

ILI9225C_INVOFF                 = 0x20
ILI9225C_INVON                  = 0x21

ILI9225_BLACK                   = 0x0000
ILI9225_BLUE                    = 0x001F
ILI9225_RED                     = 0xF800
ILI9225_GREEN                   = 0x07E0
ILI9225_CYAN                    = 0x07FF
ILI9225_MAGENTA                 = 0xF81F
ILI9225_YELLOW                  = 0xFFE0
ILI9225_WHITE                   = 0xFFFF


def color565(r, g, b):
    """Convert red, green, blue components to a 16-bit 565 RGB value. Components
    should be values 0 to 255.
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def image_to_data(image):
    """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
    #NumPy is much faster at doing this. NumPy code provided by:
    #Keith (https://www.blogger.com/profile/02555547344016007163)
    pb = np.array(image.convert('RGB')).astype('uint16')
    color = ((pb[:,:,0] & 0xF8) << 8) | ((pb[:,:,1] & 0xFC) << 3) | (pb[:,:,2] >> 3)
    return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()

class ILI9225(object):
    """Representation of an ILI9225 TFT LCD."""

    def __init__(self, rs, spi, rst=None, gpio=None, width=ILI9225_TFTWIDTH, height=ILI9225_TFTHEIGHT):
        """Create an instance of the display using SPI communication. Must
        provide the GPIO pin number for the RS pin and the SPI driver. Can
        optionally provide the GPIO pin number for the reset pin as the rst
        parameter.
        """
        self._rs = rs
        self._rst = rst
        self._spi = spi
        self._gpio = gpio
        self.width = width
        self.height = height

        if self._gpio is None:
            self._gpio = GPIO.get_platform_gpio()

        # set rs as output
        self._gpio.setup(rs, GPIO.OUT)

        # setup reset as output (if provided)
        if rst is not None:
            self._gpio.setup(rst, GPIO.OUT)

        # set spi to mode 0, msb first.
        spi.set_mode(0)
        spi.set_bit_order(SPI.MSBFIRST)
        spi.set_clock_hz(64000000)

        # create an image buffer.
        self.buffer = Image.new('RGB', (width, height))

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or command
        data (False).  Chunk_size is an optional size of bytes to write in a
        single SPI transaction, with a default of 4096.
        """
        # Set RS low for command, high for data.
        self._gpio.output(self._rs, is_data)

        # convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]

        # write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start+chunk_size, len(data))
            self._spi.write(data[start:end])

        return self

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        return self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        return self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            self._gpio.set_high(self._rst)
            time.sleep(0.005)
            self._gpio.set_low(self._rst)
            time.sleep(0.02)
            self._gpio.set_high(self._rst)
            time.sleep(0.150)

    def _init(self):
        # initialize the display.  broken out as a separate function so it can
        # be overridden by other displays in the future.

        # set SS bit and direction output from S528 to S1
        self.command(ILI9225_POWER_CTRL1).data([0x00, 0x00]); # set SAP,DSTB,STB
        self.command(ILI9225_POWER_CTRL2).data([0x00, 0x00]); # set APON,PON,AON,VCI1EN,VC
        self.command(ILI9225_POWER_CTRL3).data([0x00, 0x00]); # set BT,DC1,DC2,DC3
        self.command(ILI9225_POWER_CTRL4).data([0x00, 0x00]); # set GVDD
        self.command(ILI9225_POWER_CTRL5).data([0x00, 0x00]); # set VCOMH/VCOML voltage
        time.sleep(0.04);

        # power-on sequence
        self.command(ILI9225_POWER_CTRL2).data([0x00, 0x18]); # set APON, PON, AON, VCI1EN, VC
        self.command(ILI9225_POWER_CTRL3).data([0x61, 0x21]); # set BT, DC1, DC2, DC3
        self.command(ILI9225_POWER_CTRL4).data([0x00, 0x6F]); # set GVDD   /*007F 0088 */
        self.command(ILI9225_POWER_CTRL5).data([0x49, 0x5F]); # set VCOMH/VCOML voltage
        self.command(ILI9225_POWER_CTRL1).data([0x08, 0x00]); # set SAP, DSTB, STB
        time.sleep(0.01);
        self.command(ILI9225_POWER_CTRL2).data([0x10, 0x3B]); # set APON, PON, AON, VCI1EN, VC
        time.sleep(0.05);

        self.command(ILI9225_DRIVER_OUTPUT_CTRL).data([0x01, 0x1C]);  # set the display line number and display direction
        self.command(ILI9225_LCD_AC_DRIVING_CTRL).data([0x01, 0x00]); # set 1 line inversion
        self.command(ILI9225_ENTRY_MODE).data([0x10, 0x30]);          # set GRAM write direction and BGR=1.
        self.command(ILI9225_DISP_CTRL1).data([0x00, 0x00]);          # Display off
        self.command(ILI9225_BLANK_PERIOD_CTRL1).data([0x08, 0x08]); # set the back porch and front porch
        self.command(ILI9225_FRAME_CYCLE_CTRL).data([0x11, 0x00]);    # set the clocks number per line
        self.command(ILI9225_INTERFACE_CTRL).data([0x00, 0x00]);      # CPU interface
        self.command(ILI9225_OSC_CTRL).data([0x0D, 0x01]);            # set Osc  /*0e01*/
        self.command(ILI9225_VCI_RECYCLING).data([0x00, 0x20]);       # set VCI recycling
        self.command(ILI9225_RAM_ADDR_SET1).data([0x00, 0x00]);       # RAM Address
        self.command(ILI9225_RAM_ADDR_SET2).data([0x00, 0x00]);       # RAM Address

        # get GRAM area
        self.command(ILI9225_GATE_SCAN_CTRL).data([0x00, 0x00]);
        self.command(ILI9225_VERTICAL_SCROLL_CTRL1).data([0x00, 0xDB]);
        self.command(ILI9225_VERTICAL_SCROLL_CTRL2).data([0x00, 0x00]);
        self.command(ILI9225_VERTICAL_SCROLL_CTRL3).data([0x00, 0x00]);
        self.command(ILI9225_PARTIAL_DRIVING_POS1).data([0x00, 0xDB]);
        self.command(ILI9225_PARTIAL_DRIVING_POS2).data([0x00, 0x00]);
        self.command(ILI9225_HORIZONTAL_WINDOW_ADDR1).data([0x00, 0xAF]);
        self.command(ILI9225_HORIZONTAL_WINDOW_ADDR2).data([0x00, 0x00]);
        self.command(ILI9225_VERTICAL_WINDOW_ADDR1).data([0x00, 0xDB]);
        self.command(ILI9225_VERTICAL_WINDOW_ADDR2).data([0x00, 0x00]);

        # set GAMMA curve
        self.command(ILI9225_GAMMA_CTRL1).data([0x00, 0x00]);
        self.command(ILI9225_GAMMA_CTRL2).data([0x08, 0x08]);
        self.command(ILI9225_GAMMA_CTRL3).data([0x08, 0x0A]);
        self.command(ILI9225_GAMMA_CTRL4).data([0x00, 0x0A]);
        self.command(ILI9225_GAMMA_CTRL5).data([0x0A, 0x08]);
        self.command(ILI9225_GAMMA_CTRL6).data([0x08, 0x08]);
        self.command(ILI9225_GAMMA_CTRL7).data([0x00, 0x00]);
        self.command(ILI9225_GAMMA_CTRL8).data([0x0A, 0x00]);
        self.command(ILI9225_GAMMA_CTRL9).data([0x07, 0x10]);
        self.command(ILI9225_GAMMA_CTRL10).data([0x07, 0x10]);

        self.command(ILI9225_DISP_CTRL1).data([0x00, 0x12]);
        time.sleep(0.05);
        self.command(ILI9225_DISP_CTRL1).data([0x10, 0x17]);

 #       setBacklight(true);
 #       setOrientation(0);

 #       setBackgroundColor( COLOR_BLACK );

        self.clear();

    def begin(self):
        """Initialize the display.  Should be called once before other calls that
        interact with the display are called.
        """
        self.reset()
        self._init()

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to 239,319.
        """

        if x1 is None:
            x1 = self.width-1
        if y1 is None:
            y1 = self.height-1

#        self.command(ILI9225_CASET)        # Column addr set
#        self.data(x0 >> 8)
#        self.data(x0)                    # XSTART
#        self.data(x1 >> 8)
#        self.data(x1)                    # XEND
#        self.command(ILI9225_PASET)        # Row addr set
#        self.data(y0 >> 8)
#        self.data(y0)                    # YSTART
#        self.data(y1 >> 8)
#        self.data(y1)                    # YEND
#
#       self.command(ILI9225_RAMWR)        # write to RAM

	self.command(ILI9225_HORIZONTAL_WINDOW_ADDR1).data(x1);
	self.command(ILI9225_HORIZONTAL_WINDOW_ADDR2).data(x0);

	self.command(ILI9225_VERTICAL_WINDOW_ADDR1).data(y1);
	self.command(ILI9225_VERTICAL_WINDOW_ADDR2).data(y0);

	self.command(ILI9225_RAM_ADDR_SET1).data(x0);
	self.command(ILI9225_RAM_ADDR_SET2).data(y0);

	self.command([0x00, 0x22]);

    def display(self, image=None):
        """Write the display buffer or provided image to the hardware.  If no
        image parameter is provided the display buffer will be written to the
        hardware.  If an image is provided, it should be RGB format and the
        same dimensions as the display hardware.
        """
        # By default write the internal buffer to the display.
        if image is None:
            image = self.buffer
        # Set address bounds to entire display.
        self.set_window()
        # Convert image to array of 16bit 565 RGB data bytes.
        # Unfortunate that this copy has to occur, but the SPI byte writing
        # function needs to take an array of bytes and PIL doesn't natively
        # store images in 16-bit 565 RGB format.
        pixelbytes = list(image_to_data(image))
        # Write data to hardware.
        self.data(pixelbytes)

    def clear(self, color=(0,0,0)):
        """Clear the image buffer to the specified RGB color (default black)."""
        width, height = self.buffer.size
        self.buffer.putdata([color]*(width*height))

    def draw(self):
        """Return a PIL ImageDraw instance for 2D drawing on the image buffer."""
        return ImageDraw.Draw(self.buffer)
