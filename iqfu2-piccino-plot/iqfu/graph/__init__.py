"""
graph
-----
Package for graphing aggregated LitePoint test results.

TODO:
    * add in support for other test types
    * add in limits for each test (both IEEE and eero)
"""
import logging
import os

from .. import utils
from . import rx_sensitivity
from . import rx_sensitivity_piccino
from . import rx_sensitivity_unico
from . import rx_sweep_per
from . import tx_evm_vs_gain
from . import tx_multi_verify
from . import tx_multi_verify_unico
from . import tx_multi_verify_piccino
from . import tx_power_vs_levels

log = logging.getLogger(__name__)

SUPPORTED_TESTS = {
    "WIFI_11AC_RX_SWEEP_PER": [rx_sensitivity_piccino.graph],
    "WIFI_11AC_TX_EVM_VS_GAIN": [tx_evm_vs_gain.graph],
    "WIFI_11AC_TX_MULTI_VERIFICATION": [tx_multi_verify_piccino.graph],
    "WIFI_11AC_TX_POWER_VS_LEVELS": [tx_power_vs_levels.graph]
}

def graph(results, output_dir):
    utils.mkdir(output_dir)
    if os.path.isdir(results):
        for filename in os.listdir(results):
            _graph_results(os.path.join(results, filename), output_dir)
    else:
        _graph_results(results, output_dir)

def _graph_results(filename, output_dir):
    test_name = os.path.splitext(os.path.basename(filename))[0]
    if test_name not in SUPPORTED_TESTS:
        log.info("Test %s is not supported", test_name)
    for graph_fn in SUPPORTED_TESTS[test_name]:
        graph_fn(filename, output_dir)
