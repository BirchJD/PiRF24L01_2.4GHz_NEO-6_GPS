#!/usr/bin/python

# RPiRF24L01_Rx - Receive Current GPS Location From RF24L01
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
#/* RPiRF24L01_Rx - Receive Current GPS Location From RF24L01.               */
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



import os
import time
import datetime
import RPi.GPIO
import RPiRF24L01



# Define GPIO pin allocation.
GPIO_LED_RED = 27
GPIO_LED_GREEN = 17

# RF24L01 RF Channel.
RF_CHANNEL = 100
# Must receive data packets of exactly this byte size.
DATA_PACKET_SIZE = 30
# Conversion from Knots to MPH.
KNOTS_TO_MPH = 1.15078



# Track when RF24L01 is experiancing errors.
RF24L01_ErrorFlag = False
# Remember the time of the last received data.
RF24L01_ReceiveTime = datetime.datetime.now()



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
   ValidData = True
   # Convert data recevied to Google Maps compatible format.
   ThisDataValue = float(LogLine[:7]) * KNOTS_TO_MPH
   LogData = "{:3.2f}MPH,".format(ThisDataValue)
   if LogLine[7:8] == "S":
      LogData += "-"
   elif LogLine[7:8] != "N":
      ValidData = False
   if LogLine[8:10].strip() == "":
      ValidData = False
   else:
      LogData += LogLine[8:10]
   if LogLine[10:18].strip() == "":
      ValidData = False
   else:
      ThisDataValue = float(LogLine[10:18]) / 60
      LogData += "{:5.5f},".format(ThisDataValue).lstrip('0')
   if LogLine[18:19] == "W":
      LogData += "-"
   elif LogLine[18:19] != "E":
      ValidData = False
   if LogLine[19:22].strip() == "":
      ValidData = False
   else:
      LogData += LogLine[19:22]
   if LogLine[22:30].strip() == "":
      ValidData = False
   else:
      ThisDataValue = float(LogLine[22:30]) / 60
      LogData += "{:5.5f}\n".format(ThisDataValue).lstrip('0')
   # Open a daily log file.
   if ValidData == True:
      Now = datetime.datetime.now()
      Filename = "LOG/{:s}_RF24L01_NEO6.csv".format(Now.strftime("%Y-%m-%d"))
      if os.path.exists(Filename):
         WriteHeader = False
      else:
         WriteHeader = True
      LogFile = open(Filename, 'a', 0)
      if WriteHeader == True:
         LogFile.write("Label,Latitude,Longitude\n")
      LogFile.write(LogData)
      LogFile.close()



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
# Configure the RF24L01 device for receiving and power on.
RPiRF24L01.ConfigureRx(RF_CHANNEL, 1, DATA_PACKET_SIZE)
# Display configured addresses.
Response = RPiRF24L01.DisplayAddresses()
print(Response)
# Display configured RF channel.
Response = RPiRF24L01.DisplayRfChannel()
print(Response)
# Clear the TX and RX buffers of the RF24L01 and reset interupt status.
RPiRF24L01.Reset()

# Switch LED to Red as default.
RPi.GPIO.output(GPIO_LED_RED, 1)
RPi.GPIO.output(GPIO_LED_GREEN, 0)
while True:
   time.sleep(1)
   # If data not received in the last ten seconds, light the Red LED.
   if RF24L01_ReceiveTime + datetime.timedelta(seconds = 10) < datetime.datetime.now():
      RPi.GPIO.output(GPIO_LED_RED, 1)
      RPi.GPIO.output(GPIO_LED_GREEN, 0)

   # Display current RF24L01 status.
   # Response = RPiRF24L01.DisplayStatus()
   # print(Response)

