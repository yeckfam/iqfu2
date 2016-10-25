	
import pyvisa
import time

DEFAULT_SOAK_TIME_MINUTES = 15
SET_TEMP_THRESHOLD = 1

class TempChamber:

	def __init__(self, ip):
		self.ip ='TCPIP::' + str(ip) #+ '::INSTR'
		print [self.ip]

	def get_temp(self):
		rm = pyvisa.ResourceManager()
		#modbus = rm.open_resource('TCPIP::192.168.1.254::INSTR')
		#print rm.list_resources()
		modbus = rm.open_resource(self.ip)
		#print "HERE"
		response = modbus.query('R? 100,1')
		temp = float(response)/10
		print "Temp Chamber is %.1f degrees" % temp
		modbus.close()
		rm.close()
		return temp

	def set_temp(self, temp):
		rm = pyvisa.ResourceManager()
		modbus = rm.open_resource(self.ip)
		time.sleep(1)
		temp = temp * 10
		temp = int(temp)
		temp_string = str(temp)
		tup = ('W ', '300, ', temp_string)
		out_string = "".join(tup)
		modbus.write(out_string)
		rm.close()


	def set_temp_and_soak(self, temp, soak_time_minutes=DEFAULT_SOAK_TIME_MINUTES):
		self.set_temp(temp)

		#wait until I get to the right temp
		current_temp = float(self.get_temp())
		while ((abs(current_temp - temp) > SET_TEMP_THRESHOLD)):
			print "Current temp is: " + str(current_temp)
			print "Target temp is: " + str(temp)
			time.sleep(60)
			current_temp = float(self.get_temp())

		#then soak at this temp to make sure DUT is at correct temp
		for i in range(soak_time_minutes):
			print "Remaining soak time: ", str(soak_time_minutes - i), " minutes."
			time.sleep(60)



