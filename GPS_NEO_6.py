# NEO-6 GPS - Module Communication for Raspberry Pi in Python
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
#/* NEO-6 GPS - Module Communication for Raspberry Pi in Python.             */
#/* ------------------------------------------------------------------------ */
#/* V1.00 - 2019-08-28 - Jason Birch                                         */
#/* ------------------------------------------------------------------------ */
#/* Library for NEO-6 GPS module communication on the Raspberry Pi using     */
#/* Python.                                                                  */
#/****************************************************************************/



import time
import serial



# UART Read buffer size.
BUFF_SIZE = 65535

# Satellite data structure.
SATELLITE_ELEMENT_COUNT = 4

SATELLITE_ID = 0
SATELLITE_ELEVATION = 1
SATELLITE_AZIMUTH = 2
SATELLITE_CNO = 3

# This applications GPS Data structure element position data types.
GPS_STRUCT_DISCARD = -2
GPS_STRUCT_STATUS = -1

GPS_STRUCT_ELEMENT_COUNT = 8

GPS_STRUCT_TIME = 0
GPS_STRUCT_DATE = 1
GPS_STRUCT_SPEED = 2
GPS_STRUCT_CORSE = 3
GPS_STRUCT_N_S = 4
GPS_STRUCT_LAT = 5
GPS_STRUCT_E_W = 6
GPS_STRUCT_LONG = 7



# GPS Module GPS data protocol element position data types.
GpsDataProtocol = {
   "$GPRMC" : [ GPS_STRUCT_DISCARD,
                GPS_STRUCT_TIME, GPS_STRUCT_STATUS, GPS_STRUCT_LAT, GPS_STRUCT_N_S, GPS_STRUCT_LONG, GPS_STRUCT_E_W, 
                GPS_STRUCT_SPEED, GPS_STRUCT_CORSE, GPS_STRUCT_DATE,
                GPS_STRUCT_DISCARD, GPS_STRUCT_DISCARD, GPS_STRUCT_DISCARD, GPS_STRUCT_DISCARD ]
}



#/*********************************************/
#/* Open a UART connection to the GPS module. */
#/*********************************************/
def OpenGPS(SerialPort):
   ThisGps = serial.Serial(SerialPort, timeout = 0)
   return ThisGps



#/******************************************/
#/* Retreive raw data from the GPS module. */
#/******************************************/
def GetGpsData(ThisGPS):
   # Read GPS data.
   GpsData = ""
   ThisGpsData = "."
   while ThisGpsData != "":
      ThisGpsData = ThisGPS.read(BUFF_SIZE)
      # Not using interupt pin to syncronise data, so manually syncronise.
      if len(ThisGpsData) > 0 and ThisGpsData[0] != "$":
         time.sleep(0.1)
         GpsData = ""
         break
      elif len(ThisGpsData) > 0 and ThisGpsData[0] != ".":
         GpsData += ThisGpsData
   return GpsData



#/*************************************************************************/
#/* Before valid data aquisition, get satellite availability information. */
#/*************************************************************************/
def GetSatelliteData(GpsData):
   SatelliteData = []
   # Process each GPS data line from GPS module.
   for DataLine in GpsData.split("\n"):
      DataLine = DataLine[:-4]
      DataElements = DataLine.split(",")
      # Process satellite data.
      if DataElements[0] == "$GPGSV":
         SatelliteCount = int(DataElements[3])
         Count = 4
         while Count <= 4 * SATELLITE_ELEMENT_COUNT:
            if len(DataElements) > Count + 3:
               SatelliteData.append([])
               ThisElement = len(SatelliteData) - 1
               SatelliteData[ThisElement] = [0] * SATELLITE_ELEMENT_COUNT
               SatelliteData[ThisElement][SATELLITE_ID] = DataElements[Count + 0]
               SatelliteData[ThisElement][SATELLITE_ELEVATION] = DataElements[Count + 1]
               SatelliteData[ThisElement][SATELLITE_AZIMUTH] = DataElements[Count + 2]
               SatelliteData[ThisElement][SATELLITE_CNO] = DataElements[Count + 3]

            Count += SATELLITE_ELEMENT_COUNT
   return SatelliteData



#/************************************************/
#/* Convert satellite data to a summary display. */
#/************************************************/
def DisplaySatelliteData(SatelliteData):
   Result = "OBTAINING SATELLITES: [" + str(len(SatelliteData)) + "]\n"
   Count = 0
   for Satellite in SatelliteData:
      Count += 1
      Result += str(Satellite) + " "
      if (Count % 3) == 0:
         Result += "\n"
   Result += "\n\n"
   return Result



#/****************************************************************************/
#/* Move raw data from the GPS module into this applications data structure. */
#/****************************************************************************/
def GetGpsDecode(GpsData):
   # Start with empty data.
   ValidDataFlag = False
   GpsStruct = [0] * GPS_STRUCT_ELEMENT_COUNT
   # Process each GPS data line from GPS module.
   for DataLine in GpsData.split("\n"):
      DataElements = DataLine.split(",")
      # If the protocol has been defined for this GPS protocol type.
      if DataElements[0] in GpsDataProtocol:
         # Place the element types defined by the protocol into this applications data structure.
         ThisGpsDataProtocol = GpsDataProtocol[DataElements[0]]
         for Count in range(len(DataElements)):
            ProtocolElement = ThisGpsDataProtocol[Count]
            # If the protocol element indicates the data is valid, flag the data as valid.
            if ProtocolElement == GPS_STRUCT_STATUS and DataElements[Count] == "A":
               ValidDataFlag = True
            elif ProtocolElement >= 0 and ProtocolElement < GPS_STRUCT_ELEMENT_COUNT:
               GpsStruct[ProtocolElement] = DataElements[Count]
   # Ensure data received has been flagged as valid.
   if ValidDataFlag == False:
      GpsStruct = [0] * GPS_STRUCT_ELEMENT_COUNT
   return GpsStruct

