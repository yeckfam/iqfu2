	
import socket
import time

DEFAULT_SOAK_TIME_MINUTES = 15
SET_TEMP_THRESHOLD = 1
F4T_SOCKET = 5025


"""
Interfacing to the temp chamber over SCPI has the temperature units in farenheight.
There is currently no way to change this as of: October 10 2015
"""

class TempChamber:

	def __init__(self, ip):
		self.ip = str(ip)
		
	def farenheight_to_celsius(self, temp):
		f = float(temp)
		c = (f - 32)*5/9
		return format(c,'.2f')
		
	def celsius_to_farenheight(self, temp):
		c = float(temp)
		f = c*9/5 +32
		return format(f,'.2f')
		
	def get_temp(self):
		'''
		Temps from the temp chamber are in farenheight, we set in celsius.
		The connection to the temp chamber seems kinda flakey, so need to try a few times.
		'''
		
		success = False
		while success == False:
			try:
				#open connection
				s = socket.socket()
				s.connect((self.ip, F4T_SOCKET))
				time.sleep(1)
				
				#get temp
				s.send(":SOURCE:CLOOP1:PVALUE?\r\n")
				time.sleep(1)
				temp_f = s.recv(256)
				temp_c = self.farenheight_to_celsius(temp_f)
				print "Temp Chamber is %s degrees celsius" % temp_c
				
				#close connection
				s.close()
				success = True
			except:
				pass
		
		return temp_c

	def set_temp(self, temp_c):
		'''
		Temps from the temp chamber are in farenheight, but we use celsius.
		Need to convert.
		The connection to the temp chamber seems kinda flakey, so need to try a few times.
		'''
		success = False
		while success == False:
			try:
				#open connection
				s = socket.socket()
				s.connect((self.ip, F4T_SOCKET))
				time.sleep(1)
				
				#set temp
				temp_f = self.celsius_to_farenheight(temp_c)
				temp_string = ":SOURCE:CLOOP1:SPOINT " + str(temp_f) + "\r\n"
				
				s.send(temp_string)
				time.sleep(1)
				#s.send(":SOURCE:CLOOP1:SPOINT?\r\n")
				#time.sleep(1)
				#print s.recv(256)
				print "Temp Chamber set to %s degrees celsius" % temp_c
				
				#close connection
				s.close()
				success = True
			except:
				pass


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



