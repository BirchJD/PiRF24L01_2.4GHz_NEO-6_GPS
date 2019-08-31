#!/usr/bin/python

# RPiRF24L01_Tx - Transmit Current GPS Location From RF24L01
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
#/* RPiRF24L01_Tx - Transmit Current GPS Location From RF24L01.              */
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



import time
import datetime
import RPi.GPIO
import RPiRF24L01
import GPS_NEO_6



# Define GPIO pin allocation.
GPIO_LED_RED = 27
GPIO_LED_GREEN = 17

# RF24L01 RF Channel.
RF_CHANNEL = 100
# Must receive data packets of exactly this byte size.
DATA_PACKET_SIZE = 30



# Track when RF24L01 is experiancing errors.
RF24L01_ErrorFlag = False



#/*****************************/
#/* RF24L01 interupt routine. */
#/*****************************/
def RF24L01_Interupt_Callback(GpioPin):
   global RF24L01_ErrorFlag
   global RF24L01_ReceiveTime

   print("\n!RF24L01 INTERUPT!")
   IntFlags = RPiRF24L01.GetIntFlags()
   # Display current RF24L01 status.
   if IntFlags & RPiRF24L01.RF24L01_STATUS_MAX_RT:
      print("RF24L01_STATUS_MAX_RT")
      RF24L01_ErrorFlag = True
      # Clear data failed to send.
      RPiRF24L01.FlushTxBuffer()
      # Flash display LEDs on RPiRF24L01 error.
      if RPi.GPIO.input(GPIO_LED_GREEN) == 0:
         RPi.GPIO.output(GPIO_LED_GREEN, 1)
         RPi.GPIO.output(GPIO_LED_RED, 0)
      else:
         RPi.GPIO.output(GPIO_LED_GREEN, 0)
         RPi.GPIO.output(GPIO_LED_RED, 1)
   if IntFlags & RPiRF24L01.RF24L01_STATUS_TX_DS:
      print("RF24L01_STATUS_TX_DS")
      RF24L01_ErrorFlag = False
      # Display Green LED.
      RPi.GPIO.output(GPIO_LED_RED, 0)
      RPi.GPIO.output(GPIO_LED_GREEN, 1)
   if IntFlags & RPiRF24L01.RF24L01_STATUS_RX_DR:
      print("RF24L01_STATUS_RX_DR")
      RF24L01_ErrorFlag = False
      RF24L01_ReceiveTime = datetime.datetime.now()
      # Display Green LED.
      RPi.GPIO.output(GPIO_LED_RED, 0)
      RPi.GPIO.output(GPIO_LED_GREEN, 1)
      # Retreive the RX data.
      Response = RPiRF24L01.GetData()
      LogEntry = "".join(chr(Char) for Char in Response) + "\n"
      WriteLogLine(LogEntry)
      # Configure the RF24L01 device for receiving and power on.
      RPiRF24L01.ConfigureRx(RF_CHANNEL, 1, DATA_PACKET_SIZE)
   print("\n")



#/*********************************/
#/* Write a line to the log file. */
#/*********************************/
def WriteLogLine(LogLine):
   # Not implemented in transmitter code.
   return



#  /*******************************************/
# /* Configure Raspberry Pi GPIO interfaces. */
#/*******************************************/
RPi.GPIO.setwarnings(False)
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(GPIO_LED_RED, RPi.GPIO.OUT, initial=0)
RPi.GPIO.setup(GPIO_LED_GREEN, RPi.GPIO.OUT, initial=0)

# Initialise the RF24L01 device.
RPiRF24L01.Init()
RPi.GPIO.add_event_detect(RPiRF24L01.GPIO_RF24L01_INT, RPi.GPIO.FALLING, callback=RF24L01_Interupt_Callback)

# Configure the RF24L01 device.
RPiRF24L01.Configure()
# Configure the RF24L01 device for transmitting and power on.
RPiRF24L01.ConfigureTx(RF_CHANNEL)
# Display configured addresses.
Response = RPiRF24L01.DisplayAddresses()
print(Response)
# Display configured RF channel.
Response = RPiRF24L01.DisplayRfChannel()
print(Response)
# Clear the TX and RX buffers of the RF24L01 and reset interupt status.
RPiRF24L01.Reset()

# Open GPS UART connection.
ThisGPS = GPS_NEO_6.OpenGPS("/dev/ttyS0")

# Switch LED to Red as default.
RPi.GPIO.output(GPIO_LED_RED, 1)
RPi.GPIO.output(GPIO_LED_GREEN, 0)
ValidGpsStruct = []
while True:
   time.sleep(1)
   # Send GPS position every five seconds.
   if len(ValidGpsStruct) == 0 or RF24L01_ErrorFlag == False:
      ValidGpsStruct = []
      for Count in range(4):
         # Read the GPS position every second.
         time.sleep(1)

         GpsData = GPS_NEO_6.GetGpsData(ThisGPS)
         GpsStruct = GPS_NEO_6.GetGpsDecode(GpsData)
         if GpsStruct[0] != 0:
            ValidGpsStruct = GpsStruct

   # Display current RF24L01 status.
   # Response = RPiRF24L01.DisplayStatus()
   # print(Response)

   if len(ValidGpsStruct) == 0:
      # Display satellite information if no valid GPS data is available.
      RPi.GPIO.output(GPIO_LED_RED, 1)
      RPi.GPIO.output(GPIO_LED_GREEN, 0)
      SatelliteData = GPS_NEO_6.GetSatelliteData(GpsData)
      Response = GPS_NEO_6.DisplaySatelliteData(SatelliteData)
      print(Response)
   else:
      # If valid GPS data is available, transmit to receiver.
      if RF24L01_ErrorFlag == False:
         RPi.GPIO.output(GPIO_LED_GREEN, 1)
      # DataPacket = "{:6.6s},".format(ValidGpsStruct[GPS_NEO_6.GPS_STRUCT_TIME])
      # DataPacket += "{:6.6s},".format(ValidGpsStruct[GPS_NEO_6.GPS_STRUCT_DATE])
      DataPacket = "{:>7s}".format(ValidGpsStruct[GPS_NEO_6.GPS_STRUCT_SPEED])
      DataPacket += "{:1.1s}".format(ValidGpsStruct[GPS_NEO_6.GPS_STRUCT_N_S])
      DataPacket += "{:>10s}".format(ValidGpsStruct[GPS_NEO_6.GPS_STRUCT_LAT])
      DataPacket += "{:1.1s}".format(ValidGpsStruct[GPS_NEO_6.GPS_STRUCT_E_W])
      DataPacket += "{:>11s}".format(ValidGpsStruct[GPS_NEO_6.GPS_STRUCT_LONG])
      RPiRF24L01.SendData(RF_CHANNEL, 1, DataPacket)

