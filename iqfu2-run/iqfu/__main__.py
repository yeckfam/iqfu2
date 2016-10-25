"""
main
----
Entry point for the iqfu command.
"""
from __future__ import print_function
import argparse
import os
import sys

from . import iqfact

def import_error(lib):
    print("Please install {lib}".format(lib=lib), file=sys.stderr)
    return 1

def aggregate_cmd(args):
    try:
        from . import stats
        return stats.aggregate(args.results, args.output_dir)
    except ImportError as e:
        return import_error(e.message.split()[-1])

def graph_cmd(args):
    try:
        from . import graph
        return graph.graph(args.results, args.output_dir)
    except ImportError as e:
        return import_error(e.message.split()[-1])

def test_cmd(args):
    return iqfact.run_test_flow(args.iqfact_dir, args.tester_ip,
                                args.dut_id, args.dut_ip, args.tester_port,
                                args.path_loss, args.test_flow,
                                args.output_dir, args.stop_on_error, args.tags)

def main(args=None):
    parser = argparse.ArgumentParser(prog="iqfu",
                                     description="LitePoint IQfact+ tool")
    subparsers = parser.add_subparsers(title="subcommands")
    test_parser = subparsers.add_parser("test",
                                        help="Run LitePoint test flow")
    test_parser.add_argument("iqfact_dir",
                             help="Path to the IQfact+ install directory")
    test_parser.add_argument("tester_ip",
                             help="IP address of the LitePoint tester")
    test_parser.add_argument("dut_id",
                             help="The serial number of the DUT")
    test_parser.add_argument("dut_ip",
                             help="IP address of the DUT")
    test_parser.add_argument("tester_port",
                             choices=sorted(iqfact.RF_PORT_MAPPING.keys()),
                             help="RF port on the tester that the device "
                                  "is connected to")
    test_parser.add_argument("path_loss",
                             help="CSV file of path losses by frequency")
    test_parser.add_argument("test_flow",
                             help="LitePoint test flow file to run")
    test_parser.add_argument("-o", "--output_dir",
                             default=os.getcwd(),
                             help="Output directory for files")
    test_parser.add_argument("--stop_on_error",
                             action="store_true",
                             help="Stop test flow on error")
    test_parser.add_argument("-t", "--tags",
                             nargs="+",
                             default=(),
                             help="Tags for this test")
    test_parser.set_defaults(func=test_cmd)

    stats_parser = subparsers.add_parser("aggregate",
                                         help="Aggregate test results")
    stats_parser.add_argument("results",
                              nargs="+",
                              help="Results to aggregate")
    stats_parser.add_argument("-o", "--output_dir",
                              default=os.getcwd(),
                              help="Output directory for files")
    stats_parser.set_defaults(func=aggregate_cmd)

    graph_parser = subparsers.add_parser("graph", help="Graph test results")
    graph_parser.add_argument("results", help="Result CSVs to graph")
    graph_parser.add_argument("-o", "--output_dir",
                              default=os.getcwd(),
                              help="Output directory for files")
    graph_parser.set_defaults(func=graph_cmd)

    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
