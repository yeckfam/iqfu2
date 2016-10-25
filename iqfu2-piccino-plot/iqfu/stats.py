"""
stats
-----
Compute stats and parse test result files.
"""
import json
import logging
import pandas as pd
import os

from . import utils

log = logging.getLogger(__name__)

SUPPORTED_TESTS = (
    "WIFI_11AC_RX_SWEEP_PER",
    "WIFI_11AC_TX_EVM_VS_GAIN",
    "WIFI_11AC_TX_MULTI_VERIFICATION",
    "WIFI_11AC_TX_POWER_VS_LEVELS"
)

def aggregate(dirs, output_dir):
    """Returns an aggregated CSV of all of the included tests."""
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    results = {}
    for test_dir in test_dirs(dirs):
        for kind, result in test_results(test_dir).iteritems():
            print 'Aggregating: ' + str(test_dir)
            if kind not in results:
                results[kind] = result
            else:
                results[kind] = results[kind].append(result)
    
    for kind, result in results.iteritems():

        result.to_csv(os.path.join(output_dir, kind + ".csv"), index=False)

def test_dirs(globbed_paths):
    """Return all of the test directories.

    Assumes that a test directory is defined by having a top-level
    "info.json" file.
    """
    return [os.path.dirname(p) for p in utils.expand_paths(globbed_paths)
            if os.path.basename(p) == "info.json"]

def test_results(test_dir):
    """Parse the results from a test directory.

    Returns a dict of test result data frames, indexed by test type (e.g.,
    WIFI_11AC_RX_SWEEP_PER, WIFI_11AC_TX_MULTI_VERIFICATION)
    """
    results_dir = os.path.join(test_dir, "results")
    if not os.path.isdir(results_dir):
        log.warn("No results for test %s!", os.path.basename(test_dir))
        return {}

    # build dict of test results by test type
    results = {}
    for kind, tests in tests_by_type(results_dir).iteritems():
        if kind not in SUPPORTED_TESTS:
            continue
        results[kind] = pd.DataFrame()
        for test in tests:
            result = test_result(test)
            if results[kind].empty:
                results[kind] = result
            else:
                results[kind] = results[kind].append(result)

    # add in information from the test's info.json
    with open(os.path.join(test_dir, "info.json")) as f:
        info = json.load(f)
    for kind, result in results.iteritems():
    	try:
    		test_dut_id = info["dut_id"]
    	except:
    		test_dut_id = info["dut"]["id"]
        result["DUT_ID"] = test_dut_id
        try:
            for i, tag in enumerate(info["tags"]):
                result["TAG_" + str(i)] = tag            	
        except:
            pass
        result["TEST_FLOW"] = info["test_flow"]
        result["TEST_NAME"] = os.path.basename(test_dir)
        result["START_TIME"] = info["start_time"]
        result["END_TIME"] = info["end_time"]
        result["HOST"] = info["host"]
        
    
    return results

def tests_by_type(results_dir):
    """Get a single test flow's result files broken down by test type."""
    tests = {}
    for filename in os.listdir(results_dir):
        path = os.path.join(results_dir, filename)
        name = test_name(path)
        if name is not None:
            kind = test_type(path)
            if kind not in tests:
                tests[kind] = set()
            tests[kind].add(os.path.join(results_dir, name))
    return tests

def test_name(test_file):
    """Get the name of a test from an input or results CSV.

    The "name" of a test is just the basename minus the suffix.
    """
    basename = os.path.basename(test_file)
    for suffix in ("_input.csv", "_result.csv"):
        if basename.endswith(suffix):
            return basename[:-len(suffix)]
    return None

def test_type(test_file):
    """Get the type of a test from an input or results CSV.

    The type is given by the first line of the file.
    """
    with open(test_file) as f:
        return f.readline().strip()

def test_result(test):
    """Merge test input and result files.

    In most cases, LitePoint obnoxiously returns two separate files for each
    test run, one with the test inputs, and one with the test results. Both are
    needed to fully understand what happened in the test.
    """
    # set header = 1 to throw away test type row
    # set skiprows = (2, 3) to throw away units and data type rows
    try:
        input = pd.read_csv(test + "_input.csv", header=1, skiprows=(2, 3))
        result = pd.read_csv(test + "_result.csv", header=1, skiprows=(2, 3))
    except:
        return pd.DataFrame()
    if os.path.basename(test).startswith("WIFI_11AC_TX_EVM_VS_GAIN"):
        result = _fixup_tx_evm_vs_gain(result)
    return pd.merge(
        input, result, on=("EXECUTION_NUM", "STEP_NUM")
    ).dropna(axis=1, how='all')

def _fixup_tx_evm_vs_gain(data_frame):
    max_power_levels = data_frame["NUMBER_OF_POWER_LEVELS"].max()
    for num_power_levels in data_frame["NUMBER_OF_POWER_LEVELS"].unique():
        df = data_frame[
            data_frame["NUMBER_OF_POWER_LEVELS"] == num_power_levels
        ]
        if num_power_levels != max_power_levels:
            columns = (
                "EVM_VALUES_AVG_DB",
                "POWER_LEVELS_AVG_DBM"
            )
            end = columns[-1] + "_" + str(max_power_levels - 1)
            for column in columns:
                start = column + "_" + str(num_power_levels)
                df.ix[:, start:end] = df.ix[:, start:end].shift(
                    max_power_levels - num_power_levels, axis=1
                )
            data_frame[
                data_frame["NUMBER_OF_POWER_LEVELS"] == num_power_levels
            ] = df
    return data_frame
