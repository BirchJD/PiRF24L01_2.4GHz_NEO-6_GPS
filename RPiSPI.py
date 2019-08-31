# RPiSPI - SPI Communication for Raspberry Pi in Python
# Copyright (C) 2019 Jason Birch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#/****************************************************************************/
#/* PiSPI - SPI Communication for Raspberry Pi in Python.                    */
#/* ------------------------------------------------------------------------ */
#/* V1.00 - 2019-08-28 - Jason Birch                                         */
#/* ------------------------------------------------------------------------ */
#/* Library for SPI communication on the Raspberry Pi using Python.          */
#/****************************************************************************/



import time
import RPi.GPIO



# Define GPIO pin allocation.
GPIO_SPI_CE = 8
GPIO_SPI_MOSI = 10
GPIO_SPI_MISO = 9
GPIO_SPI_SCK = 11

# Number of bits per word for SPI.
SPI_WORD_BITS = 8
SPI_CLOCK_PERIOD = 0.000001



#/************************/
#/* Initialise SPI GPIO. */
#/************************/
def SpiInit():
   RPi.GPIO.setup(GPIO_SPI_MISO, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
   RPi.GPIO.setup(GPIO_SPI_CE, RPi.GPIO.OUT, initial=1)
   RPi.GPIO.setup(GPIO_SPI_MOSI, RPi.GPIO.OUT, initial=0)
   RPi.GPIO.setup(GPIO_SPI_SCK, RPi.GPIO.OUT, initial=0)



#/************************************************/
#/* Send and receive a data word on the SPI bus. */
#/************************************************/
def SpiSendReceiveWord(DataWord):
   ReceiveDataWord = 0

   BitMask = (1 << (SPI_WORD_BITS - 1))
   for Count in range(SPI_WORD_BITS):
      if (DataWord & BitMask) == 0:
         RPi.GPIO.output(GPIO_SPI_MOSI, 0)
      else:
         RPi.GPIO.output(GPIO_SPI_MOSI, 1)
      BitMask = BitMask / 2

      RPi.GPIO.output(GPIO_SPI_SCK, 1)
      time.sleep(SPI_CLOCK_PERIOD)

      SpiReadBit = RPi.GPIO.input(GPIO_SPI_MISO)
      ReceiveDataWord = ReceiveDataWord * 2 + SpiReadBit

      RPi.GPIO.output(GPIO_SPI_SCK, 0)
      time.sleep(SPI_CLOCK_PERIOD)

   return ReceiveDataWord

