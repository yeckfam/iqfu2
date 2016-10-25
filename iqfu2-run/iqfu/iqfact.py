"""
iqfact
------
Module for running LitePoint tests.

TODO:
    * figure out what's needed to support multi-DUT
"""
import getpass
import json
import logging
import os
import re
import shutil
import socket
import subprocess
import time

#from . import dakota

log = logging.getLogger(__name__)

ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

RF_PORT_MAPPING = {
    "RF1A": {
        "port": 2,
        "route": 1
    },
    "RF1B": {
        "port": 2,
        "route": 2,
    },
    "RF2A": {
        "port": 3,
        "route": 1,
    },
    "RF2B": {
        "port": 3,
        "route": 2
    },
    "RF3A": {
        "port": 4,
        "route": 1
    },
    "RF3B": {
        "port": 4,
        "route": 2
    },
    "RF4A": {
        "port": 5,
        "route": 1
    },
    "RF4B": {
        "port": 5,
        "route": 2
    }
}

# IQTESTER_IP01 and IQTESTER_IP02 for MIMO, but need special WIFI_11AC_MIMO test flow

class TestFlow(object):
    """Simple wrapper around a LitePoint test flow file for templating.

    This is a crude hack, but we want to keep the test flow files readable
    by IQfact+ Studio, so we don't want to turn them into Jinja templates
    or anything like that.
    """
    def __init__(self, filename):
        self.name = os.path.splitext(os.path.basename(filename))[0]
        with open(filename, "rU") as f:
            self._data = f.read()

    @property
    def has_calibration(self):
        return re.search(r"CALIBRATION", self._data) is not None

    #@property
    #def dut_ip(self):
    #    return self._get("CONNECTION_STRING")

    #@dut_ip.setter
    #def dut_ip(self, value):
    #    self._set("CONNECTION_STRING", value)

    @property
    def tester_ip(self):
        return self._get("IQTESTER_IP01")

    @tester_ip.setter
    def tester_ip(self, value):
        self._set("IQTESTER_IP01", value)

    @property
    def rx_path_loss_file(self):
        return self._get("RX_PATH_LOSS_FILE")

    @rx_path_loss_file.setter
    def rx_path_loss_file(self, value):
        self._set("RX_PATH_LOSS_FILE", value)

    @property
    def tx_path_loss_file(self):
        return self._get("TX_PATH_LOSS_FILE")

    @tx_path_loss_file.setter
    def tx_path_loss_file(self, value):
        self._set("TX_PATH_LOSS_FILE", value)

    @property
    def route(self):
        return self._get("IQXEL_CONNECTION_TYPE")

    @route.setter
    def route(self, value):
        self._set("IQXEL_CONNECTION_TYPE", value)

    @property
    def vsa_port(self):
        return self._get("VSA_PORT")

    @vsa_port.setter
    def vsa_port(self, value):
        self._set("VSA_PORT", value)

    @property
    def vsg_port(self):
        return self._get("VSG_PORT")

    @vsg_port.setter
    def vsg_port(self, value):
        self._set("VSG_PORT", value)

    def _get(self, key):
        match = re.search(key + r"(\s+\[\w+\]\s+)=([^\n]+)\n", self._data)
        if match is None:
            return None
        return match.group(2).strip()

    def _set(self, key, value):
        # just as above
        value = str(value).replace("\\", "\\\\")
        self._data = re.sub(key + r"(\s+\[\w+\]\s+)=[^\n]+\n",
                            r"{k}\1= {v}\n".format(k=key, v=value),
                            self._data)

    def to_file(self, filename):
        with open(filename, "w") as f:
            f.write(self._data)

def run_test_flow(iqfact_dir, tester_ip, dut_id, dut_ip, tester_port,
                  path_loss, test_flow, output_dir=os.getcwd(),
                  stop_on_error=True, tags=None):
    """Run a LitePoint test flow.

    For tracking purposes, will create a directory structure like the
    following (big when unzipped, but compresses nicely):

        dut_id-test_flow-tag1-tag2-...-date_time/
            info.json
            path_loss.csv
            Atheros_Setup.ini
            radio-0.art
            radio-1.art
            test_flow.txt
            results/
    """
    start_time = time.gmtime()

    # get the absolute path to the IQfact+ directory
    iqfact_dir = os.path.join(os.path.realpath(iqfact_dir), "bin-" + tester_port)

    # record a bunch of stuff about this run
    info = {
        "start_time": time.strftime(ISO8601_FORMAT, start_time),
        "user": getpass.getuser(),
        "host": socket.gethostname(),
        "iqfact_dir": iqfact_dir,
        "dut_id": dut_id,
        "tester_ip": tester_ip,
        "dut_ip": dut_ip,
        "tester_port": tester_port,
        "test_flow": os.path.realpath(test_flow),
        "tags": tags
    }

    # make sure we get an absolute path
    output_dir = os.path.realpath(output_dir)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # create a test_flow object for templating
    test_flow = TestFlow(test_flow)

    # we're going to store all our output for this run here
    output_subdirname = dut_id + "-"
    output_subdirname += test_flow.name + "-"
    if tags:
        output_subdirname += "-".join(tags) + "-"
    output_subdirname += time.strftime("%m_%d_%y_%H%M%S", start_time)
    output_subdir = os.path.join(output_dir, output_subdirname)
    os.mkdir(output_subdir)

    # store the path loss being used
    shutil.copy(path_loss, os.path.join(output_subdir, "path_loss.csv"))
    path_loss = os.path.join(output_subdir, "path_loss.csv")

    test_flow_path = os.path.join(output_subdir, "test_flow.txt")

    # rewrite the test flow file with provided values
    test_flow.tester_ip = tester_ip
    test_flow.dut_ip = dut_ip
    test_flow.rx_path_loss_file = path_loss
    test_flow.tx_path_loss_file = path_loss
    test_flow.route = RF_PORT_MAPPING[tester_port]["route"]
    test_flow.vsa_port = RF_PORT_MAPPING[tester_port]["port"]
    test_flow.vsg_port = RF_PORT_MAPPING[tester_port]["port"]
    test_flow.to_file(test_flow_path)

    # run the test flow
    log.info("Running test flow %s" % test_flow.name)
    try:
        # do DUT-specific work to prepare for the test
        # vega.prepare_for_test(iqfact_dir, output_subdir, test_flow)
        iqrun_console(iqfact_dir, test_flow_path, stop_on_error)
    except subprocess.CalledProcessError:
        log.exception("IQrun_Console FAILED")
        if stop_on_error:
            raise
    finally:
        info["end_time"] = time.strftime(ISO8601_FORMAT, time.gmtime())
        results = os.path.join(iqfact_dir, "Result")
        if os.path.isdir(results):
            shutil.move(results, os.path.join(output_subdir, "results"))
        with open(os.path.join(output_subdir, "info.json"), "a") as f:
            json.dump(info, f, indent=4, sort_keys=True)
    return output_subdir

def iqrun_console(iqfact_dir, test_flow, stop_on_error=False):
    """Run the IQrun_Console.exe binary with appropriate args.

    Lean wrapper around the core IQfact+ test flow runner. The runner
    expects the current working directory to be the same as the binary,
    so change in there to start and back out again at the finish.
    """
    curdir = os.getcwd()
    os.chdir(iqfact_dir)
    cmd = (
        "IQrun_Console.exe",
        "-RUN", test_flow,
        "-ONFAIL", str(int(stop_on_error)),
        "-EXIT"
    )
    log.info(cmd)
    try:
        subprocess.check_call(cmd)
    finally:
        os.chdir(curdir)

def iqfactrun_console(iqfact_dir, test_flow, stop_on_error=False):
    """Run the IQfactRun_Console.exe binary with appropriate args.

    This binary is helpful for debugging, as it will output good logs
    indicating all of the traffic back and forth between it and the
    NART server running on the DUT. But it should not be used for
    running tests, as it is unreliable and spits out bad result files.
    """
    curdir = os.getcwd()
    os.chdir(iqfact_dir)
    cmd = (
        "IQfactRun_Console.exe",
        "-RUN", test_flow,
        "-FLOWCONTROL", str(int(stop_on_error)),
        "-LOG", "INFORMATION",
        "-LIMIT", "1",
        "-EXIT"
    )
    log.info(cmd)
    try:
        subprocess.check_call(cmd)
    finally:
        os.chdir(curdir)
