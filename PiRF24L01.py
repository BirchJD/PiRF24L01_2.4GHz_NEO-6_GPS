#!/usr/bin/python

#/****************************************************************************/
#/* PiRF24L01 - 2.4GHz Data Transceiver.                                     */
#/* ------------------------------------------------------------------------ */
#/* V1.00 - 2019-08-03 - Jason Birch                                         */
#/* ------------------------------------------------------------------------ */
#/* Script for configuring and using RF24L01 to transmit and receive on SPI. */
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



import sys
import time
import RPi.GPIO



# Define GPIO pin allocation.
GPIO_RF24L01_CSN = 25
GPIO_RF24L01_INT = 24
GPIO_RF24L01_SPI_CE = 8
GPIO_RF24L01_SPI_MOSI = 10
GPIO_RF24L01_SPI_MISO = 9
GPIO_RF24L01_SPI_SCK = 11

# Number of bits per word for SPI.
SPI_WORD_BITS = 8
SPI_CLOCK_PERIOD = 0.000001

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



def SpiSendReceiveWord(DataWord):
   ReceiveDataWord = 0

   BitMask = (1 << (SPI_WORD_BITS - 1))
   for Count in range(SPI_WORD_BITS):
      if (DataWord & BitMask) == 0:
         sys.stdout.write("0")
         RPi.GPIO.output(GPIO_RF24L01_SPI_MOSI, 0)
      else:
         sys.stdout.write("1")
         RPi.GPIO.output(GPIO_RF24L01_SPI_MOSI, 1)
      BitMask = BitMask / 2

      RPi.GPIO.output(GPIO_RF24L01_SPI_SCK, 1)
      time.sleep(SPI_CLOCK_PERIOD)

      SpiReadBit = RPi.GPIO.input(GPIO_RF24L01_SPI_MISO)
      ReceiveDataWord = ReceiveDataWord * 2 + SpiReadBit

      RPi.GPIO.output(GPIO_RF24L01_SPI_SCK, 0)
      time.sleep(SPI_CLOCK_PERIOD)

   return ReceiveDataWord



#  /*******************************************/
# /* Configure Raspberry Pi GPIO interfaces. */
#/*******************************************/
RPi.GPIO.setwarnings(False)
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(GPIO_RF24L01_INT, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(GPIO_RF24L01_SPI_MISO, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(GPIO_RF24L01_CSN, RPi.GPIO.OUT, initial=1)
RPi.GPIO.setup(GPIO_RF24L01_SPI_CE, RPi.GPIO.OUT, initial=1)
RPi.GPIO.setup(GPIO_RF24L01_SPI_MOSI, RPi.GPIO.OUT, initial=0)
RPi.GPIO.setup(GPIO_RF24L01_SPI_SCK, RPi.GPIO.OUT, initial=0)

while True:
   RPi.GPIO.output(GPIO_RF24L01_SPI_CE, 0)
   RPi.GPIO.output(GPIO_RF24L01_CSN, 0)

   Command = RF24L01_NOP
#   Command = [(RF24L01_R_REGISTER[0] | 5), 0x00]
   for ThisWord in Command:
      Response = SpiSendReceiveWord(ThisWord)
      sys.stdout.write(" = {:2X} ".format(Response))
   sys.stdout.write("\n")
   sys.stdout.flush()

   RPi.GPIO.output(GPIO_RF24L01_CSN, 1)
   RPi.GPIO.output(GPIO_RF24L01_SPI_CE, 1)

   time.sleep(0.1)

