#!/usr/bin/env python
import json
import os
import time
import glob
from tempchamberF4T import TempChamber
from iqfu import alerts
from iqfu import iqfact
import telnetlib
import logging


IQFACT_DIR = "/LitePoint/IQfact_plus/IQfact+_QCA_AP145_3.3.0.Eng3_Lock"
TESTER_IP = "192.168.1.120"
DUT_ID = "E6220861"
DUT_IP = "192.168.1.1"
TESTER_PORT = "RF1A"
OUTPUT_DIR = os.path.expanduser("C:/Users/eero/Dropbox (eero)/eero Hardware/26. Test Results")
STOP_ON_ERROR = False

SOAK_TIME_MINUTES = 2
TRANSMIT_TIME = 2

PATH_LOSS_DIR = "C:/projects/path-loss/"
PATH_LOSS = os.path.join(PATH_LOSS_DIR, "path_loss_chamber_new.csv")

#open a file to log data in
logfile = open('C:/templog.txt', 'a')
logfile.write("\n\n\nStarting test\n\n\n")

#Connect to temp chamber
tc = TempChamber('192.168.1.222')
#temps = range(-20,81,5)
temps = [30,0,70]


for temperature in temps:
	TAGS = ["conducted", str(temperature)]
	
	#set the temperature chamber and wait to stabilize
	print 'Setting temp chamber to: ' + str(temperature)
	logfile.write("\n\n======================================================================\n")
	logfile.write('Setting temp chamber to: ' + str(temperature) + '\n\n')
	tc.set_temp_and_soak(temperature,SOAK_TIME_MINUTES)
	
	result = None
	while result is None:
	
		try:
			
			#log into the device and reset art
			print 'connecting to vega and resetting art'
			vega = telnetlib.Telnet()
			vega.open('192.168.1.1')
			time.sleep(1)
			vega.write("/etc/init.d/art restart\n")
			time.sleep(10)
			a = vega.read_very_eager()
			print a
			logfile.write(a)
			vega.close()

			#log into both radios, load devid and have them transmit for 10mins
			
			#do 2.4GHz first
			print 'logging into radio 1 and running temp soak'
			radio1 = telnetlib.Telnet()
			radio1.open('192.168.1.1', '2391')
			time.sleep(1)
			radio1.write('load devid=3c; memory=flash\n')
			time.sleep(5)
			radio1.write('tx cf=2437;tx100=1;r=vt7;ch=3;tp=19\n')
			radio1.write('start\n')
			time.sleep(TRANSMIT_TIME)

			radio1.write('stop\n')
			time.sleep(1)
			radio1.write('fr a=BB_therm_adc_4.latest_therm_value\n')
			time.sleep(2)
			a = radio1.read_very_eager()
			print a
			logfile.write('\n+++++++++++++++++++++++++++++++++++++++++++++\n')
			logfile.write('Radio1-2GHz: \n')
			logfile.write('\n+++++++++++++++++++++++++++++++++++++++++++++\n')
			logfile.write(a)
			result = "done"
	
		except:
			pass	

	iqfact.run_test_flow(IQFACT_DIR, TESTER_IP, DUT_ID, DUT_IP,
	                             TESTER_PORT, PATH_LOSS, "C:/projects/test-flows/tx-power-verify2p4.txt",
	                             OUTPUT_DIR, STOP_ON_ERROR, TAGS)

	radio1.close()
	
	result = None
	while result is None:
	
		try:
			
			#log into the device and reset art
			print 'connecting to vega and resetting art'
			vega = telnetlib.Telnet()
			vega.open('192.168.1.1')
			time.sleep(1)
			vega.write("/etc/init.d/art restart\n")
			time.sleep(10)
			a = vega.read_very_eager()
			print a
			logfile.write(a)
			vega.close()

			#log into both radios, load devid and have them transmit for 10mins
			
			#do 5GHz last
			
			print 'logging into radio 0 and running temp soak'
			radio0 = telnetlib.Telnet()
			radio0.open('192.168.1.1', '2390')
			time.sleep(1)
			radio0.write('load devid=3c; memory=flash\n')
			time.sleep(5)
			radio0.write('tx cf=5180;tx100=1;r=vt7;ch=3;tp=19;\n')
			radio0.write('start\n')

			print 'logging into radio 1 and running temp soak'
			radio1 = telnetlib.Telnet()
			radio1.open('192.168.1.1', '2391')
			time.sleep(1)
			radio1.write('load devid=3c; memory=flash\n')
			time.sleep(5)
			radio1.write('tx cf=5805;tx100=1;r=vt7;ch=3;tp=19;\n')
			radio1.write('start\n')


			print 'transmitting for this many seconds: ' + str(TRANSMIT_TIME)
			time.sleep(TRANSMIT_TIME)
			
			#now stop the radios and save the data	
			radio0.write('stop\n')
			radio1.write('stop\n')
			time.sleep(1)
			radio0.write('fr a=BB_therm_adc_4.latest_therm_value\n')
			radio1.write('fr a=BB_therm_adc_4.latest_therm_value\n')
			time.sleep(2)
			
			logfile.write('\n+++++++++++++++++++++++++++++++++++++++++++++\n')
			logfile.write('Radio0-5GHz: ')
			logfile.write('\n+++++++++++++++++++++++++++++++++++++++++++++\n')
			a = radio0.read_very_eager()
			print a
			logfile.write(a)
			
			logfile.write('\n+++++++++++++++++++++++++++++++++++++++++++++\n')
			logfile.write('Radio1-5GHz: ')
			logfile.write('\n+++++++++++++++++++++++++++++++++++++++++++++\n')
			a = radio1.read_very_eager()
			print a
			logfile.write(a)
			
			result = "done"
	
		except:
			pass	

	radio0.close()
	radio1.close()

	iqfact.run_test_flow(IQFACT_DIR, TESTER_IP, DUT_ID, DUT_IP,
	                             TESTER_PORT, PATH_LOSS, "C:/projects/test-flows/tx-power-verify5.txt",
	                             OUTPUT_DIR, STOP_ON_ERROR, TAGS)


