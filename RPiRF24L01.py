# RPiRF24L01 - Module TX/RX Communication for Raspberry Pi in Python
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
#/* RPiRF24L01 - Module TX/RX Communication for Raspberry Pi in Python.      */
#/* ------------------------------------------------------------------------ */
#/* V1.00 - 2019-08-28 - Jason Birch                                         */
#/* ------------------------------------------------------------------------ */
#/* Library for RPiRF24L01 module communication on the Raspberry Pi using    */
#/* Python.                                                                  */
#/****************************************************************************/



import time
import RPi.GPIO
import RPiSPI



# Define base transmit and receive address.
BASE_ADDRESS = [0x1C, 0x93, 0xB5, 0xFE, 0xD2]


# Define GPIO pin allocation.
GPIO_RF24L01_CSN = 25
GPIO_RF24L01_INT = 24


#/************************/
#/* RF24L01 SPI COMMANDS */
#/************************/
# Read registers, OR 5 bit Memory Map Address
RF24L01_R_REGISTER = 0x00
# Write registers. OR 5 bit Memory Map Address. Executable in power down or standby modes only.
RF24L01_W_REGISTER = 0x20
# Read RX-payload: 1 - 32 bytes. A read operation will always start at byte 0. Payload will be deleted from FIFO after it is read. Used in RX mode.
RF24L01_R_RX_PAYLOAD = 0x61
# Used in TX mode. Write TX-payload: 1 - 32 bytes. A write operation will always start at byte 0.
RF24L01_W_TX_PAYLOAD = 0xA0
# Flush TX FIFO, used in TX mode.
RF24L01_FLUSH_TX = 0xE1
# Flush RX FIFO, used in RX mode. Should not be executed during transmission of acknowledge, i.e. acknowledge package will not be completed.
RF24L01_FLUSH_RX = 0xE2
# Used for a PTX device. Reuse last sent payload. Packets will be repeatedly resent as long as CE is high. TX payload reuse is active until W_TX_PAYLOAD or FLUSH TX is executed. TX payload reuse must not be activated or deactivated during package transmission.
RF24L01_REUSE_TX_PL = 0xE3
# No Operation, get the device status.
RF24L01_NOP = 0xFF


#/*********************/
#/* RF24L01 REGISTERS */
#/*********************/
RF24L01_CONFIG = 0x00
# Power TX and RX circuits to enable transmission and reception.
RF24L01_CONFIG_EN_CRC = 0x08
RF24L01_CONFIG_CRCO = 0x04
RF24L01_CONFIG_PWR_UP = 0x02
RF24L01_CONFIG_PRX = 0x01
RF24L01_CONFIG_PTX = 0x00

# Enable Auto Acknowledgment
RF24L01_EN_AA = 0x01

# Enabled RX Addresses.
RF24L01_EN_RXADDR = 0x02

# Setup of Address Widths (common for all data pipes)
RF24L01_SETUP_AW = 0x03

# Setup of Automatic Retransmission
RF24L01_SETUP_RETR = 0x04
RF24L01_SETUP_RETR_ARD = 0xF0
RF24L01_SETUP_RETR_ARC = 0x0F

# RF Channel
RF24L01_RF_CH = 0x05

RF24L01_RF_SETUP = 0x06
# Data Rate '0' - 1 Mbps, '1' - 2 Mbps.
RF24L01_RF_SETUP_1MBPS = 0x00
RF24L01_RF_SETUP_2MBPS = 0x08
# Set RF output power in TX mode. '00' - -18 dBm, '01' - -12 dBm, ,'10' - -6 dBm, '11' - 0 dBm.
RF24L01_RF_SETUP_18DBM = 0x00
RF24L01_RF_SETUP_12DBM = 0x02
RF24L01_RF_SETUP_10DBM = 0x04
RF24L01_RF_SETUP_0DBM = 0x06
# Setup LNA gain.
RF24L01_RF_SETUP_LNA_GAIN = 0x01

RF24L01_STATUS = 0x07
# Data Ready RX FIFO interrupt. Set high when new data arrives RX FIFO.
# Write 1 to clear bit.
RF24L01_STATUS_RX_DR = 0x40
# Data Sent TX FIFO interrupt. Set high when packet sent on TX.
# If AUTO_ACK is activated, this bit will be set high only when ACK is received.
# Write 1 to clear bit.
RF24L01_STATUS_TX_DS = 0x20
# Maximum number of TX retries interrupt.
# Write 1 to clear bit.
# If MAX_RT is set it must be cleared to enable further communication.
RF24L01_STATUS_MAX_RT = 0x10
# Data pipe number for the payload.
RF24L01_STATUS_RX_P_NO = 0x0E
# TX FIFO full flag. 1: TX FIFO full. 0: Available locations in TX FIFO.
RF24L01_STATUS_TX_FULL = 0x01

# Count lost packets. The counter is overflow protected to 15, and discontinue at max until reset.
# The counter is reset by writing to RF_CH.
RF24L01_OBSERVE_TX = 0x08
RF24L01_OBSERVE_TX_PLOS_CNT =0xF0 
RF24L01_OBSERVE_TX_ARC_CNT = 0x0F

# Carrier Detect.
RF24L01_CD = 0x09

# Receive address data pipe 0. 5 Bytes maximum length. (LSByte is written first. Write the number of bytes defined by SETUP_AW)
RF24L01_RX_ADDR_P0 = 0x0A
# Receive address data pipe 1. 5 Bytes maximum length. (LSByte is written first. Write the number of bytes defined by SETUP_AW)
RF24L01_RX_ADDR_P1 = 0x0B
# Receive address data pipe 2. Only LSB. MSBytes will be equal to RX_ADDR_P1[39:8]
RF24L01_RX_ADDR_P2 = 0x0C
# Receive address data pipe 3. Only LSB. MSBytes will be equal to RX_ADDR_P1[39:8]
RF24L01_RX_ADDR_P3 = 0x0D
# Receive address data pipe 4. Only LSB. MSBytes will be equal to RX_ADDR_P1[39:8]
RF24L01_RX_ADDR_P4 = 0x0E
# Receive address data pipe 5. Only LSB. MSBytes will be equal to RX_ADDR_P1[39:8]
RF24L01_RX_ADDR_P5 = 0x0F
# Transmit address. Used for a PTX device only. (LSByte is written first)
# Set RX_ADDR_P0 equal to this address to handle automatic acknowledge if this is a PTX device with Enhanced ShockBurstTM enabled.
RF24L01_TX_ADDR = 0x10

# Number of bytes in RX payload in data pipe 0 (1 to 32 bytes). 0 Pipe not used.
RF24L01_RX_PW_P0 = 0x11
# Number of bytes in RX payload in data pipe 1 (1 to 32 bytes). 0 Pipe not used.
RF24L01_RX_PW_P1 = 0x12
# Number of bytes in RX payload in data pipe 2 (1 to 32 bytes). 0 Pipe not used.
RF24L01_RX_PW_P2 = 0x13
# Number of bytes in RX payload in data pipe 3 (1 to 32 bytes). 0 Pipe not used.
RF24L01_RX_PW_P3 = 0x14
# Number of bytes in RX payload in data pipe 4 (1 to 32 bytes). 0 Pipe not used.
RF24L01_RX_PW_P4 = 0x15
# Number of bytes in RX payload in data pipe 5 (1 to 32 bytes). 0 Pipe not used.
RF24L01_RX_PW_P5 = 0x16

RF24L01_FIFO_STATUS = 0x17
# Reuse last sent data packet if set high.
# The packet will be repeatedly resent as long as CE is high.
# TX_REUSE is set by the SPI instruction REUSE_TX_PL, and is reset by the SPI instructions W_TX_PAYLOAD or FLUSH TX.
RF24L01_FIFO_STATUS_TX_REUSE = 0x40
# TX FIFO full flag. 1: TX FIFO full. 0: Available locations in TX FIFO.
RF24L01_FIFO_STATUS_TX_FULL = 0x20
# TX FIFO empty flag. 1: TX FIFO empty. 0: Data in TX FIFO.
RF24L01_FIFO_STATUS_TX_EMPTY = 0x10
# RX FIFO full flag. 1: RX FIFO full. 0: Available locations in RX FIFO.
RF24L01_FIFO_STATUS_RX_FULL = 0x02
# RX FIFO empty flag. 1: RX FIFO empty. 0: Data in RX FIFO.
RF24L01_FIFO_STATUS_RX_EMPTY = 0x01



#/****************************/
#/* Initialise RF24L01 GPIO. */
#/****************************/
def Init():
   RPiSPI.SpiInit()
   RPi.GPIO.setup(GPIO_RF24L01_INT, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
   RPi.GPIO.setup(GPIO_RF24L01_CSN, RPi.GPIO.OUT, initial=0)



#/********************************************/
#/* Send a single SPI command to the RF24L01 */
#/* device and receive the response.         */
#/********************************************/
def SendCommand(Command):
   RPi.GPIO.output(GPIO_RF24L01_CSN, 0)
   Response = []
   for ThisWord in Command:
      Response.append(RPiSPI.SpiSendReceiveWord(ThisWord))
   RPi.GPIO.output(GPIO_RF24L01_CSN, 1)
   return Response



#/***************************************************************************/
#/* Read the specified number of bytes from the specified RF24L01 register. */
#/***************************************************************************/
def ReadRegister(RegisterAddress, DataWordCount):
   Command = [(RF24L01_R_REGISTER | RegisterAddress)]
   for Count in range(DataWordCount):
      Command.append(0x00)
   Response = SendCommand(Command)
   return Response



#/*********************************************************************/
#/* Write the specified data array to the specified RF24L01 register. */
#/*********************************************************************/
def WriteRegister(RegisterAddress, WriteData):
   Command = [(RF24L01_W_REGISTER | RegisterAddress)]
   for Data in WriteData:
      Command.append(Data)
   Response = SendCommand(Command)
   return Response



#/************************/
#/* Flush the TX buffer. */
#/************************/
def FlushTxBuffer():
   # Flush old transmit data.
   Command = [RF24L01_FLUSH_TX]
   Response = SendCommand(Command)   



#/************************/
#/* Flush the RX buffer. */
#/************************/
def FlushRxBuffer():
   # Flush old received data.
   Command = [RF24L01_FLUSH_RX]
   Response = SendCommand(Command)   



#/*******************************************/
#/* Standard initial general configuration. */
#/*******************************************/
def Configure():
   # Configure local transmit address.
   Response = WriteRegister(RF24L01_TX_ADDR, [BASE_ADDRESS[0], BASE_ADDRESS[1], BASE_ADDRESS[2], BASE_ADDRESS[3], BASE_ADDRESS[4]])
   # Configure local receive base address.
   Response = WriteRegister(RF24L01_RX_ADDR_P0, [BASE_ADDRESS[0], BASE_ADDRESS[1], BASE_ADDRESS[2], BASE_ADDRESS[3], BASE_ADDRESS[4]])

   # Configure local receive address 1.
   Response = WriteRegister(RF24L01_RX_ADDR_P1, [BASE_ADDRESS[0] + 1, BASE_ADDRESS[1], BASE_ADDRESS[2], BASE_ADDRESS[3], BASE_ADDRESS[4]])
   # Configure local receive address 2.
   Response = WriteRegister(RF24L01_RX_ADDR_P2, [BASE_ADDRESS[0] + 2])
   # Configure local receive address 3.
   Response = WriteRegister(RF24L01_RX_ADDR_P3, [BASE_ADDRESS[0] + 3])
   # Configure local receive address 4.
   Response = WriteRegister(RF24L01_RX_ADDR_P4, [BASE_ADDRESS[0] + 4])
   # Configure local receive address 5.
   Response = WriteRegister(RF24L01_RX_ADDR_P5, [BASE_ADDRESS[0] + 5])
   # Configure 1Mb/s and 0 DBm.
   Response = WriteRegister(RF24L01_RF_SETUP, [(RF24L01_RF_SETUP_1MBPS | RF24L01_RF_SETUP_0DBM | RF24L01_RF_SETUP_LNA_GAIN)])
   # Power off module radio.
   Response = WriteRegister(RF24L01_CONFIG, [RF24L01_CONFIG_EN_CRC])



#/**************************************/
#/* Configure the current mode for TX. */
#/**************************************/
def ConfigureTx(Channel):
   # Set RF channel, resets bad packet counts back to zero.
   Response = WriteRegister(RF24L01_RF_CH, [Channel])
   # Power on module radio for transmitting.
   Response = WriteRegister(RF24L01_CONFIG, [(RF24L01_CONFIG_PWR_UP | RF24L01_CONFIG_EN_CRC | RF24L01_CONFIG_PTX)])
   RPi.GPIO.output(GPIO_RF24L01_CSN, 0)



#/**************************************/
#/* Configure the current mode for RX. */
#/**************************************/
def ConfigureRx(Channel, Pipeline, ByteCount):
   # Set RF channel, resets bad packet counts back to zero.
   Response = WriteRegister(RF24L01_RF_CH, [Channel])
   # Set byte count being received, must be exact size of data arriving.
   Response = WriteRegister(RF24L01_RX_PW_P0 + Pipeline, [ByteCount])
   # Power on module radio for receiving.
   Response = WriteRegister(RF24L01_CONFIG, [(RF24L01_CONFIG_PWR_UP | RF24L01_CONFIG_EN_CRC | RF24L01_CONFIG_PRX)])
   Response = WriteRegister(RF24L01_EN_RXADDR, [(1 | (1 << Pipeline))])
   RPi.GPIO.output(GPIO_RF24L01_CSN, 1)



#/***************************************************/
#/* Configure the current mode for off (low power). */
#/***************************************************/
def ConfigureOff():
   # Power off module radio.
   Response = WriteRegister(RF24L01_CONFIG, [RF24L01_CONFIG_EN_CRC])
   RPi.GPIO.output(GPIO_RF24L01_CSN, 0)



#/*************************************************************************/
#/* Clear the TX and RX buffers of the RF24L01 and reset interupt status. */
#/*************************************************************************/
def Reset():
   # Flush old transmit data.
   FlushTxBuffer()
   # Flush old received data.
   FlushRxBuffer()
   # Reset max retries flag, TX data sent flag, RX data ready flag.
   Response = WriteRegister(RF24L01_STATUS, [RF24L01_STATUS_MAX_RT | RF24L01_STATUS_TX_DS | RF24L01_STATUS_RX_DR])



#/*************************************************************/
#/* Return interupt flags, and reset ready for next interupt. */
#/*************************************************************/
def GetIntFlags():
   IntFlags = ReadRegister(RF24L01_FIFO_STATUS, 1)[0]
   if IntFlags & RF24L01_STATUS_MAX_RT:
      # Reset max retries flag.
      Response = WriteRegister(RF24L01_STATUS, [RF24L01_STATUS_MAX_RT])
   if IntFlags & RF24L01_STATUS_TX_DS:
      # Reset TX data sent flag.
      Response = WriteRegister(RF24L01_STATUS, [RF24L01_STATUS_TX_DS])
   if IntFlags & RF24L01_STATUS_RX_DR:
      # Reset RX data ready flag.
      Response = WriteRegister(RF24L01_STATUS, [RF24L01_STATUS_RX_DR])

   return IntFlags



#/***************************************************************************/
#/* Send the specified data packet on the RF channel and pipeline provided. */
#/***************************************************************************/
def SendData(Channel, Pipeline, Data):
   # Configure local transmit address.
   Response = WriteRegister(RF24L01_TX_ADDR, [BASE_ADDRESS[0] + Pipeline, BASE_ADDRESS[1], BASE_ADDRESS[2], BASE_ADDRESS[3], BASE_ADDRESS[4]])
   # Configure local receive base address.
   Response = WriteRegister(RF24L01_RX_ADDR_P0, [BASE_ADDRESS[0] + Pipeline, BASE_ADDRESS[1], BASE_ADDRESS[2], BASE_ADDRESS[3], BASE_ADDRESS[4]])

   # Set RF channel, resets bad packet counts back to zero.
   Response = WriteRegister(RF24L01_RF_CH, [Channel])

   # Flush old transmit data.
   FlushTxBuffer()

   # Configure to transmit.
   Response = WriteRegister(RF24L01_CONFIG, [(RF24L01_CONFIG_PWR_UP | RF24L01_CONFIG_EN_CRC | RF24L01_CONFIG_PTX)])

   # Load data to be transmitted.
   Command = [RF24L01_W_TX_PAYLOAD]
   for Char in Data:
      Command.append(ord(Char))
   Response = SendCommand(Command)   

   # Start transmit.
   RPi.GPIO.output(GPIO_RF24L01_CSN, 1)
   time.sleep(0.000001)
   RPi.GPIO.output(GPIO_RF24L01_CSN, 0)



#/**************************************/
#/* Retreive the received data packet. */
#/**************************************/
def GetData():
   RxData = []
   # Turn off radio.
   RPi.GPIO.output(GPIO_RF24L01_CSN, 0)
   # Get the RX pipeline number.
   ThisStatus = ReadRegister(RF24L01_FIFO_STATUS, 1)
   RxPipeline = (ThisStatus[0] & RF24L01_STATUS_RX_P_NO) >> 1
   if RxPipeline < 7:
      # Get the RX buffer data size.
      RxBytes = ReadRegister(RF24L01_RX_PW_P0 + RxPipeline, 1)[1]
      # Read the RX data.
      Command = [0] * (RxBytes + 1)
      Command[0] = RF24L01_R_RX_PAYLOAD
      RxData = SendCommand(Command)
   # Flush old received data.
   FlushRxBuffer()
   return RxData[1:]



#/**********************************************/
#/* Convert the RF24L01 status values to text. */
#/**********************************************/
def DisplayStatus():
   ThisStatus = ReadRegister(RF24L01_FIFO_STATUS, 1)
   Response = "RF24L01 STATUS:\n"
   if ThisStatus[0] & RF24L01_STATUS_RX_DR:
      Response += "RX FIFO Data Ready\n"
   if ThisStatus[0] & RF24L01_STATUS_TX_DS:
      Response += "TX FIFO Data Sent\n"
   if ThisStatus[0] & RF24L01_STATUS_MAX_RT:
      Response += "MAX TX Retrys Exceeded\n"
   RxPipeline = (ThisStatus[0] & RF24L01_STATUS_RX_P_NO) >> 1
   if RxPipeline != 7:
      Response += "RX Pipeline: {:d}\n".format(RxPipeline)
   if ThisStatus[0] & RF24L01_STATUS_TX_FULL:
      Response += "TX FIFO Full\n"
   if ThisStatus[0] & RF24L01_CONFIG_EN_CRC:
      Response += "CRC [" + str((((ThisStatus[0] & RF24L01_CONFIG_CRCO) >> 2) + 1)) + " bytes]\n"

   if ThisStatus[1] & RF24L01_FIFO_STATUS_TX_REUSE:
      Response += "Reuse Last Sent Data Packet\n"
   if ThisStatus[1] & RF24L01_FIFO_STATUS_TX_FULL:
      Response += "TX FIFO FULL\n"
   if ThisStatus[1] & RF24L01_FIFO_STATUS_TX_EMPTY:
      Response += "TX FIFO EMPTY\n"
   if ThisStatus[1] & RF24L01_FIFO_STATUS_RX_FULL:
      Response += "RX FIFO FULL\n"
   if ThisStatus[1] & RF24L01_FIFO_STATUS_RX_EMPTY:
      Response += "RX FIFO EMPTY\n"

   return Response



#/*****************************************************/
#/* Convert the RF24L01 configured addresses to text. */
#/*****************************************************/
def DisplayAddresses():
   Result = "RF24L01 ADDRESSES:\n"
   Result += "                   [>>> - Channel Enabled]\n"
   Result += "                   [ *  - Auto Acknowledgement Enabled]\n"
   AddressWidth = ReadRegister(RF24L01_SETUP_AW, 1)[1] + 2
   AutoAckEnabled = ReadRegister(RF24L01_EN_AA, 1)[1]
   RxEnabled = ReadRegister(RF24L01_EN_RXADDR, 1)[1]
   TxAddress = ReadRegister(RF24L01_TX_ADDR, 5)[1:]
   Result += "RF24L01 TRANSMIT ADDRESS: " + str(TxAddress) + "\n"
   for Count in range(2):
      if RxEnabled & (1 << Count):
         Result += ">>> "
      else:
         Result += "    "
      if AutoAckEnabled & (1 << Count):
         Result += "* "
      else:
         Result += "  "
      RxAddress = ReadRegister(RF24L01_RX_ADDR_P0 + Count, 5)[1:]
      Result += "RF24L01 RECEIVE ADDRESS PIPELINE [" + str(Count) + "]: " + str(RxAddress[:AddressWidth])
      RxBytes = ReadRegister(RF24L01_RX_PW_P0 + Count, 1)[1]
      Result += " [" + str(RxBytes) + " RXb]\n"
   for Count in range(2, 6):
      if RxEnabled & (1 << Count):
         Result += ">>> "
      else:
         Result += "    "
      if AutoAckEnabled & (1 << Count):
         Result += "* "
      else:
         Result += "  "
      Response = ReadRegister(RF24L01_RX_ADDR_P0 + Count, 1)
      ThisAddress = RxAddress
      ThisAddress[0] = Response[1]
      Result += "RF24L01 RECEIVE ADDRESS PIPELINE [" + str(Count) + "]: " + str(ThisAddress[:AddressWidth])
      RxBytes = ReadRegister(RF24L01_RX_PW_P0 + Count, 1)[1]
      Result += " [" + str(RxBytes) + " RXb]\n"

   return Result



#/***************************************************************/
#/* Convert the RF24L01 configured Radio configuration to text. */
#/***************************************************************/
def DisplayRfChannel():
   Result = "RF CHANNEL: "
   RfSetup = ReadRegister(RF24L01_RF_SETUP, 1)[1]
   RfChannel = ReadRegister(RF24L01_RF_CH, 1)[1]
   CarrierDetect = ReadRegister(RF24L01_CD, 1)[1]
   if RfSetup & RF24L01_RF_SETUP_2MBPS:
      Result += "2Mbps "
      Rf = 2400 + 2 * RfChannel
   else:
      Result += "1Mbps "
      Rf = 2400 + 1 * RfChannel
   Result += str(Rf) + "MHz "
   if RfSetup & RF24L01_RF_SETUP_0DBM:
      Result += "0dBm "
   elif RfSetup & RF24L01_RF_SETUP_10DBM:
      Result += "10dBm "
   elif RfSetup & RF24L01_RF_SETUP_12DBM:
      Result += "12dBm "
   else:
      Result += "0dBm "
   if CarrierDetect == 0:
      Result += " !!! NO CARRIER DETECT !!!"
   else:
      Result += " *** CARRIER DETECT ***"
   Result += "\n"

   DataPacketCounts = ReadRegister(RF24L01_OBSERVE_TX, 1)[1]
   DataPacketsLost = ((DataPacketCounts & RF24L01_OBSERVE_TX_PLOS_CNT) >> 4)
   DataPacketsResent = (DataPacketCounts & RF24L01_OBSERVE_TX_ARC_CNT)
   Result += "Data Packets Lost: " + str(DataPacketsLost) + "\n"
   Result += "Data Packets Resent: " + str(DataPacketsResent) + "\n"

   AutoRetransmit = ReadRegister(RF24L01_SETUP_RETR, 1)[1]
   AutoRetransmitDelay = (250 * ((AutoRetransmit & RF24L01_SETUP_RETR_ARD) >> 4)) + 86
   AutoRetransmitCount = (AutoRetransmit & RF24L01_SETUP_RETR_ARC)
   Result += "Auto Retransmit Delay: " + str(AutoRetransmitDelay) + "uS\n"
   Result += "Auto Retransmit Count: " + str(AutoRetransmitCount) + "\n"

   return Result

