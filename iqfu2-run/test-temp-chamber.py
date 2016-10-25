from tempchamberF4T import TempChamber
import time

a = TempChamber('192.168.1.222')
"""
"a.get_temp()
time.sleep(5)
a.set_temp(74)
time.sleep(5)
a.set_temp_and_soak(76)
print 'done'
"""


for temp in [-30, -20, -10]:
	
	a.set_temp_and_soak(temp,5)
	




