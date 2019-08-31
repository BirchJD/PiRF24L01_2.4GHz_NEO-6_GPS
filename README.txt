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



Measuring Tx/Rx Range of RF24L01 Using NEO6 GPS Receiver on Raspberry Pi
with Python

Using Python on two Raspberry Pi computers to measure the transmission range of
RF24L01 modules with long antennas. A NEO-6 GPS module is used to measure the
distance of valid transmissions. The data will be collected and viewed in
Google Maps, in the next video to be posted.



Patreon, donations help produce more OpenSource projects:
https://www.patreon.com/_DevelopIT

Videos of this project:
https://youtu.be/3Tr1x5budC0

Source Code on GitHub:
https://github.com/BirchJD/



Applications
============
RPiSPI.py         - SPI interface communication.

RPiRF24L01.py     - RF24L01 RF transiver contol interface.

GPS_NEO_6.py      - NEO-6 GPS receiver control interface.

PiRF24L01_Rx.py   - Receiving application for the Raspberry Pi which receives
                    and logs GPS data.

PiRF24L01_Tx.py   - Transmitting application for the Raspberry Pi which obtains
                    it's GPS location from the NEO-6 GPS receiver and transmits
                    the data to the receiving Raspberry Pi.

LOG               - Directory for Google Maps compatible 



Modules
=======
NEO-6 GPS
RF24L01 Transiver

