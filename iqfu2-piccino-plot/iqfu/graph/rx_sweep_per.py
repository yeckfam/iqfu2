"""
rx_sweep_per
------------
Make an Rx Packet Error Rate graph.

We make one graph for each combination of bandwidth, 802.11 standard,
and data rate, as 10% PER limits are defined in terms of those values.

But then for completeness, we break it down by frequency and by test
name, so that we get to see a bunch of comparisons.
"""
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

log = logging.getLogger(__name__)

LIMITS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "resources", "limits", "rx_per.csv"
)

def graph(data_csv, output_dir):
    data_frame = pd.read_csv(data_csv)
    limits = pd.read_csv(LIMITS)

    # We first need to clean up the data. It's in "wide" format, so we have
    # to turn it into "long" format:
    #
    #     DATA_RATE  PER_VALUES_0  PER_VALUES_1 ... POWER_LEVELS_0 ...
    #     MCS0       0             1                -40
    #
    #     ...turns into...
    #
    #     DATA_RATE  PER_VALUES_  POWER_LEVELS_  idx
    #     MCS0       0            -40            0
    #     MCS0       1            -41            1
    data_frame["id"] = data_frame.index
    data_frame = pd.wide_to_long(data_frame,
                                 ("PER_VALUES_", "POWER_LEVELS_"),
                                 i="id", j="idx")
    data_frame.reset_index(level=1, inplace=True)

    # clean up the data
    data_frame.replace({
        "PER_VALUES_": {
            -99999.99: 100.0, # LitePoint sentinel
            0: 0.1,           # prevent discontinuities in log scale graph
            np.nan: 100.0     # missing data
        },
        "POWER_LEVELS_": {
            np.nan: -100
        }
    }, inplace=True)

    # add in chain information
    data_frame = data_frame.assign(
        CHAIN = lambda x: data_frame["RX1"] + 2 * data_frame["RX2"])

    # make sure to sort by PER_VALUES and POWER_LEVELS index
    data_frame.sort("idx", inplace=True)

    groupings = (
        (
            ("STANDARD", "DATA_RATE", "BSS_BANDWIDTH", "TEST_NAME"),
            ("BSS_FREQ_MHZ_PRIMARY", "CHAIN")
        ),
        (
            ("STANDARD", "DATA_RATE", "BSS_BANDWIDTH", "BSS_FREQ_MHZ_PRIMARY"),
            ("TEST_NAME", "CHAIN")
        )
    )
    for (graph_grouping, line_grouping) in groupings:
        for graph_name, graph_data in data_frame.groupby(graph_grouping, sort=False):
            # hack to make the graph title look good
            graph_title = "Rx Packet Error Rate ("
            if "TEST_NAME" in graph_grouping:
                graph_title +=  ", ".join(graph_name[0:3]) + ")\n" + graph_name[3]
            else:
                graph_title +=  ", ".join([str(s) for s in graph_name]) + ")"
            max_power_level = graph_data["START_POWER_LEVEL_DBM"].max()
            min_power_level = graph_data["STOP_POWER_LEVEL_DBM"].min()
            figure = plt.figure(figsize=(20, 10))
            ax = figure.add_subplot(111)
            for line_name, line_data in graph_data.groupby(line_grouping, sort=False):
                ax.plot(line_data["POWER_LEVELS_"],
                        line_data["PER_VALUES_"], label=line_name)
            # call out the 10% line in red
            ax.plot([max_power_level, min_power_level], [10, 10], color="r")
            # call out the limit in red
            limit = limits[
                (limits["STANDARD"] == graph_name[0]) &
                (limits["DATA_RATE"] == graph_name[1]) &
                (limits["BANDWIDTH"] == int(graph_name[2][3:])) &
                (limits["SPATIAL_STREAMS"] == 1)
            ]["EERO_SPEC"].values
            ax.plot([limit, limit], [0, 100], color="r")
            ax.grid("on")
            ax.set_yscale("log")
            ax.set_xlim(max_power_level, min_power_level)
            ax.set_ylim(0, 100)
            ax.set_title(graph_title)
            ax.set_xlabel("Input Power (dBm)")
            ax.set_ylabel("Packet Error Rate (%)")
            handles, labels = ax.get_legend_handles_labels()
            legend = ax.legend(handles, labels, loc="upper center",
                               bbox_to_anchor=(0.5,-0.1))
            filename = "rx-per-" + "-".join([str(s) for s in graph_name])
            figure.savefig(os.path.join(output_dir, filename + ".png"),
                           bbox_extra_artists=(legend,), bbox_inches="tight")
            figure.clear()
            plt.close(figure)
