#!/usr/bin/python

#/****************************************************************************/
#/* PiRF24L01 - 2.4GHz Data Transceiver.                                     */
#/* ------------------------------------------------------------------------ */
#/* V1.00 - 2019-08-03 - Jason Birch                                         */
#/* ------------------------------------------------------------------------ */
#/* Script for configuring and using RF24L01 to transmit and receive on SPI. */
#/* Using SPI port on the Raspberry Pi currently Python SPI protocol not     */
#/* working so using manual SPI manipulation in PiRF24L01.py.                */  
#/*                                                                          */
#/* RF24L01 Module pins:                                                     */
#/*                     ---                                                  */
#/* (Pin25)         GND|0 O|3V3  (Pin17)                                     */
#/* (Pin24/GPIO8)    CE|O O|CSN  (Pin22/GPIO25)                              */
#/* (Pin23/GPIO11)  SCK|O O|MOSI (Pin21/GPIO9)                               */
#/* (Pin19/GPIO10) MISO|O O|INT  (Pin18/GPIO24)                              */
#/*                     ---                                                  */
#/*                                                                          */
#/****************************************************************************/



import time
import spidev
import RPi.GPIO



# Define GPIO pin allocation.
GPIO_RF24L01_CSN = 25
GPIO_RF24L01_INT = 24

# SPI interface to use.
SPI_BUS = 0
# SPI CS pin to use.
SPI_CS = 0
# SPI interface speed 8MHz.
#SPI_BUS_SPEED = 8000000
SPI_BUS_SPEED = 50000
# SPI mode.
SPI_BUS_MODE = 0
# SPI bits.
SPI_BITS_PER_WORD = 8

# Read registers, OR 5 bit Memory Map Address
RF24L01_R_REGISTER = [ 0x00 ]
# Write registers. OR 5 bit Memory Map Address. Executable in power down or standby modes only.
RF24L01_W_REGISTER = [ 0x20 ]
# Read RX-payload: 1 - 32 bytes. A read operation will always start at byte 0. Payload will be deleted from FIFO after it is read. Used in RX mode.
RF24L01_R_RX_PAYLOAD = [ 0x61 ]
# Used in TX mode. Write TX-payload: 1 - 32 bytes. A write operation will always start at byte 0.
RF24L01_W_TX_PAYLOAD = [ 0xA0 ]
# Flush TX FIFO, used in TX mode.
RF24L01_FLUSH_TX = [ 0xE1 ]
# Flush RX FIFO, used in RX mode. Should not be executed during transmission of acknowledge, i.e. acknowledge package will not be completed.
RF24L01_FLUSH_RX = [ 0xE2 ]
# Used for a PTX device. Reuse last sent payload. Packets will be repeatedly resent as long as CE is high. TX payload reuse is active until W_TX_PAYLOAD or FLUSH TX is executed. TX payload reuse must not be activated or deactivated during package transmission.
RF24L01_REUSE_TX_PL = [ 0xE3 ]
# No Operation, get the device status.
RF24L01_NOP = [ 0xFF ]



#  /*******************************************/
# /* Configure Raspberry Pi GPIO interfaces. */
#/*******************************************/
RPi.GPIO.setwarnings(False)
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(GPIO_RF24L01_INT, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(GPIO_RF24L01_CSN, RPi.GPIO.OUT, initial=1)

#  /*****************************************/
# /* Configure Raspberry Pi SPI interface. */
#/*****************************************/
ThisSPI = spidev.SpiDev()
ThisSPI.open(SPI_BUS, SPI_CS)
ThisSPI.max_speed_hz = SPI_BUS_SPEED
ThisSPI.mode = SPI_BUS_MODE
ThisSPI.bits_per_word = SPI_BITS_PER_WORD
ThisSPI.lsbfirst = False
#ThisSPI.no_cs = False
ThisSPI.cshigh = False
ThisSPI.threewire = False

while True:
   RPi.GPIO.output(GPIO_RF24L01_CSN, 0)

   time.sleep(0.1)

   Response = ThisSPI.xfer(RF24L01_NOP)
   print(str(Response))

   time.sleep(0.1)

   RPi.GPIO.output(GPIO_RF24L01_CSN, 1)

   time.sleep(0.1)


ThisSPI.close()
