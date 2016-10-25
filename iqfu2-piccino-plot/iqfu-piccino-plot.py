"""
iqfu
"""
from __future__ import print_function
import argparse
import os
import sys

def import_error(lib):
    print("Please install {lib}".format(lib=lib), file=sys.stderr)
    return 1

def aggregate_cmd(args):
    try:
        from iqfu import stats
        return stats.aggregate(args.results, args.output_dir)
    except ImportError as e:
        return import_error(e.message.split()[-1])

def graph_cmd(args):
    try:
        from iqfu import graph
        return graph.graph(args.results, args.output_dir)
    except ImportError as e:
        return import_error(e.message.split()[-1])

def main(args=None):
    parser = argparse.ArgumentParser(
        prog="iqfu", description="LitePoint IQfact+ tool"
    )

    subparsers = parser.add_subparsers(title="subcommands")

    stats_parser = subparsers.add_parser(
        "aggregate", help="Aggregate test results"
    )
    stats_parser.add_argument(
        "results", nargs="+", help="Results to aggregate"
    )
    stats_parser.add_argument(
        "-o", "--output_dir",
        default=os.getcwd(),
        help="Output directory for files"
    )
    stats_parser.set_defaults(func=aggregate_cmd)

    graph_parser = subparsers.add_parser("graph", help="Graph test results")
    graph_parser.add_argument("results", help="Result CSVs to graph")
    graph_parser.add_argument(
        "-o", "--output_dir",
        default=os.getcwd(),
        help="Output directory for files"
    )
    graph_parser.set_defaults(func=graph_cmd)

    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
