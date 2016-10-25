#!/usr/bin/env python
import json
import os
import time
import glob
from tempchamber import TempChamber
from iqfu import alerts
from iqfu import iqfact
import logging
import telnetlib

IQFACT_DIR = "/LitePoint/IQfact_plus/IQfact+_QCA_99xx_3.3.2.6_Lock"
TESTER_IP = "192.168.1.120"
DUT_ID = "G0000000"
DUT_IP = "192.168.1.1"
TESTER_PORT = "RF1A"
OUTPUT_DIR = os.path.expanduser("C:/iqfu2_run/test_results")
STOP_ON_ERROR = False


PATH_LOSS_DIR = "C:/projects/path-loss/"
PATH_LOSS = os.path.join(PATH_LOSS_DIR, "path_loss.csv")

TEST_FLOWS = []
TEST_FLOWS.append((PATH_LOSS, "C:/projects/test-flows/gen2-test-1.txt"))

for f in TEST_FLOWS:
	print f

time.sleep(1)


TAGS = ["conducted", "test", 'test']
for (PATH_LOSS, test_flow) in TEST_FLOWS:
	        iqfact.run_test_flow(IQFACT_DIR, TESTER_IP, DUT_ID, DUT_IP,
	                             TESTER_PORT, PATH_LOSS, test_flow,
	                             OUTPUT_DIR, STOP_ON_ERROR, TAGS)




