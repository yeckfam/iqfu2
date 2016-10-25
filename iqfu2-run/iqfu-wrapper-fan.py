#!/usr/bin/env python
import json
import os
import time
import glob
from tempchamber import TempChamber
from iqfu import iqfact

IQFACT_DIR = "/LitePoint/IQfact_plus/IQfact+_QCA_AP145_3.3.0.Eng3_Lock"
TESTER_IP = "192.168.1.120"
DUT_ID = "E6181847"
DUT_IP = "192.168.1.1"
TESTER_PORT = "RF1A"
OUTPUT_DIR = os.path.expanduser("C:/Test_Results/")
STOP_ON_ERROR = False


PATH_LOSS_DIR = "C:/path-loss/"
PATH_LOSS = os.path.join(PATH_LOSS_DIR, "path_loss.csv")

TEST_FLOWS = []
TEST_FLOWS.append((PATH_LOSS, "C:/test-flows/rx/rx-verification_simple.txt"))
# flows = glob.glob("C:/projects/test-flows/tx/txmulti*")
# flows = glob.glob("C:/Users/lab-1/litepoint/test-flows/rx/rx-full*")

# for flow in flows:
# 	TEST_FLOWS.append((PATH_LOSS, flow))

for f in TEST_FLOWS:
	print f

time.sleep(5)

TAGS = ["conducted", "DUT", 'Int10Ch6attenuation20real']
for (PATH_LOSS, test_flow) in TEST_FLOWS:
	        iqfact.run_test_flow(IQFACT_DIR, TESTER_IP, DUT_ID, DUT_IP,
	                             TESTER_PORT, PATH_LOSS, test_flow,
	                             OUTPUT_DIR, STOP_ON_ERROR, TAGS)