"""
Gen2
----
Module for Dakota-specific tasks.
"""
import logging
import os
import re
import shutil
import socket
import telnetlib

log = logging.getLogger(__name__)

# TODO: refactor to use pkg_resources
CONF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "conf")
# ATHEROS_SETUP = os.path.join(CONF_DIR, "Atheros_Setup.ini")
# GENERIC_RADIO_INIT = os.path.join(CONF_DIR, "generic.art")
# RADIO_0_INIT = os.path.join(CONF_DIR, "radio-0.art")
# RADIO_1_INIT = os.path.join(CONF_DIR, "radio-1.art")

DUT_LOGIN_PROMPT = "root@OpenWrt:/#"

class AtherosSetup(object):
    """Simple model of an Atheros_Setup.ini file for templating."""
    def __init__(self, filename):
        with open(filename, "rU") as f:
            self._data = f.read()

    @property
    def initialization_setting_file_r1(self):
        return self._get("INITIALIZATION_SETTING_FILE_R1")

    @initialization_setting_file_r1.setter
    def initialization_setting_file_r1(self, value):
        self._set("INITIALIZATION_SETTING_FILE_R1", value)

    @property
    def initialization_setting_file_r2(self):
        return self._get("INITIALIZATION_SETTING_FILE_R2")

    @initialization_setting_file_r2.setter
    def initialization_setting_file_r2(self, value):
        self._set("INITIALIZATION_SETTING_FILE_R2", value)

    def _get(self, key):
        match = re.search(key + r"\s*=([^\n]+)\n", self._data)
        if match is None:
            return None
        return match.group(1).strip()

    def _set(self, key, value):
        # because of how we're using regexes, we need to be sure to escape
        # all backslashes (as in Windows paths) to escape regex wrath...
        value = str(value).replace("\\", "\\\\")
        self._data = re.sub(key + r"\s*=[^\n]+\n",
                            r"{k} = {v}\n".format(k=key, v=value),
                            self._data)

    def to_file(self, filename):
        with open(filename, "w") as f:
            f.write(self._data)

def prepare_for_test(iqfact_dir, test_dir, test_flow):
    """Prepare a Vega DUT for a test flow run.

    Vega uses an Atheros radio, so we have to set up the IQfact directory with
    a special Atheros_Setup.ini configuration file. We also restart ART while
    we're at it, since it tends to crash regularly.
    """
    # adjust the Atheros_Setup.ini file based on whether or not we're
    # doing calibration as part of the test flow.
    atheros_setup = AtherosSetup(ATHEROS_SETUP)
    radio_0_init = os.path.join(test_dir, "radio-0.art")
    radio_1_init = os.path.join(test_dir, "radio-1.art")
    if test_flow.has_calibration:
        shutil.copy(RADIO_0_INIT, radio_0_init)
        shutil.copy(RADIO_1_INIT, radio_1_init)
    else:
        shutil.copy(GENERIC_RADIO_INIT, radio_0_init)
        shutil.copy(GENERIC_RADIO_INIT, radio_1_init)
    atheros_setup.initialization_setting_file_r1 = radio_0_init
    atheros_setup.initialization_setting_file_r2 = radio_1_init

    # put a copy in the IQfact+ dir (needed for LitePoint), and save one
    atheros_setup.to_file(os.path.join(iqfact_dir, "Atheros_Setup.ini"))
    atheros_setup.to_file(os.path.join(test_dir, "Atheros_Setup.ini"))

    restart_art(test_flow.dut_ip)

def connect(ip):
    """Connect to a Dakota device."""
    log.info("Logging into Dakota at %s..." % ip)
    try:
        conn = telnetlib.Telnet(ip, timeout=5)
    except socket.timeout:
        log.error("Couldn't reach Dakota at %s" % ip)
        raise
    print "Reading until logging"
    conn.read_until(DUT_LOGIN_PROMPT)
    print "Finished printing"
    return conn

def disconnect(conn):
    """Disconnect from Vega."""
    conn.write("exit\n")
    conn.close()

def run_command(ip, cmd):
    """Run a command on the Vega.

    The command should just be a raw string, with whitespace and all.
    """
    conn = connect(ip)
    conn.write(cmd + "\n")
    conn.read_until(DUT_LOGIN_PROMPT)
    disconnect(conn)

def restart_art(ip):
    """Restarts the ART daemon running on the Vega.

    ART periodically crashes, so telnet in to restart it from time to time,
    especially when running multiple test flows.
    """
    log.info("Restarting qcmbr...")
    run_command(ip, "/etc/init.d/qcmbr restart")
    log.info("qcmbr restarted")
