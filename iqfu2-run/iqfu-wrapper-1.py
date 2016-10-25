#!/usr/bin/env python
import json
import os
import time
import glob
from tempchamberF4T import TempChamber
from iqfu import alerts
from iqfu import iqfact

IQFACT_DIR = "/LitePoint/IQfact_plus/IQfact+_QCA_AP145_3.3.0.Eng3_Lock"
TESTER_IP = "192.168.1.120"
DUT_ID = "E59A0160"
DUT_IP = "192.168.1.1"
TESTER_PORT = "RF1A"
OUTPUT_DIR = os.path.expanduser("C:/Users/eero/Dropbox (eero)/eero Hardware/26. Test Results")
STOP_ON_ERROR = False

SOAK_TIME_MINUTES = 10


PATH_LOSS_DIR = "C:/projects/path-loss/"
PATH_LOSS = os.path.join(PATH_LOSS_DIR, "path_loss.csv")

TEST_FLOWS = []

# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht80_w0_c1_5ghz.txt"))
# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht80_w0_c2_5ghz.txt"))
# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht80_w1_c1_5ghz.txt"))
# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht80_w1_c2_5ghz.txt"))

#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht40_w0_c1_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht40_w0_c2_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht40_w1_c1_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht40_w1_c2_5ghz.txt"))

# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht20_w0_c1_5ghz.txt"))
# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht20_w0_c2_5ghz.txt"))
# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht20_w1_c1_5ghz.txt"))
# TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_vht20_w1_c2_5ghz.txt"))

#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht40_w0_c1_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht40_w0_c2_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht40_w1_c1_2ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht40_w1_c2_2ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht40_w1_c1_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht40_w1_c2_5ghz.txt"))

#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht20_w0_c1_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht20_w0_c2_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht20_w1_c1_2ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht20_w1_c2_2ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht20_w1_c1_5ghz.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_ht20_w1_c2_5ghz.txt"))


#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_legacy_w1_c1.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_legacy_w1_c2.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_legacy_w0_c1.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/tx/txmulti_legacy_w0_c2.txt"))





# flows = glob.glob("C:/projects/test-flows/rx/rx*")
# flows = glob.glob("C:/projects/test-flows/tx/txmulti*")

# for flow in flows:
	# TEST_FLOWS.append((PATH_LOSS, flow))

#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/fan/tx-tempcomp-combine.txt"))
#TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/calibrate.txt"))

for f in TEST_FLOWS:
	print f
	
time.sleep(5)

#Connect to temp chamber
tc = TempChamber('192.168.1.222')
temps = [0,20,70]

for temperature in temps:
	TAGS = ["conducted", str(temperature), 'fancomp3']
	#OUTPUT_DIR = os.path.expanduser("C:/Users/eero/Dropbox (eero)/eero Hardware/26. Test Results/DVT2/TempComp/%s/%sC/" %(DUT_ID, str(temperature)))
	#set the temperature chamber and wait to stabilize
	print 'Output directory: ' + OUTPUT_DIR
	print 'Setting temp chamber to: ' + str(temperature)
	tc.set_temp_and_soak(temperature,10)

	try:
		for (PATH_LOSS, test_flow) in TEST_FLOWS:
				iqfact.run_test_flow(IQFACT_DIR, TESTER_IP, DUT_ID, DUT_IP,
									 TESTER_PORT, PATH_LOSS, test_flow,
									 OUTPUT_DIR, STOP_ON_ERROR, TAGS)

		message = "Test {0} complete on {1}".format(test_flow, DUT_ID)
	except:
		message = "Error running {0} on {1}".format(test_flow, DUT_ID)
		raise
	finally:
		alerts.sms("+14157307356", message)
		
		
	
	