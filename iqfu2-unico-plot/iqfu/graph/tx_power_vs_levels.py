"""
tx_power_vs_levels
------------------
"""
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

log = logging.getLogger(__name__)

def graph(data_csv, output_dir):
    data_frame = pd.read_csv(data_csv)

    data_frame["id"] = data_frame.index

    data_frame = pd.wide_to_long(data_frame,
                                 ("POWER_LEVELS_DBM_", "TARGET_POWER_LIST_"),
                                 i="id", j="idx")
    data_frame.reset_index(level=1, inplace=True)

    # add in chain information
    data_frame = data_frame.assign(
        CHAIN = lambda x: data_frame["TX1"] + 2 * data_frame["TX2"])

    # make sure to sort by POWER_LEVELS_DBM and TARGET_POWER_LIST index
    data_frame.sort("idx", inplace=True)
    data_frame.to_csv("foobar.csv")

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
            graph_title = "Tx Output Power ("
            if "TEST_NAME" in graph_grouping:
                graph_title +=  ", ".join(graph_name[0:3]) + ")\n" + graph_name[3]
            else:
                graph_title +=  ", ".join([str(s) for s in graph_name]) + ")"
            figure = plt.figure(figsize=(20, 10))
            ax = figure.add_subplot(111)
            for line_name, line_data in graph_data.groupby(line_grouping, sort=False):
                ax.plot(line_data["TARGET_POWER_LIST_"],
                        line_data["POWER_LEVELS_DBM_"] - line_data["TARGET_POWER_LIST_"].astype(float),
                        label=line_name)
            ax.plot([10, 30], [2, 2], color="r")
            ax.plot([10, 30], [-2, -2], color="r")
            ax.grid("on")
            ax.set_xlim(10, 30)
            ax.set_ylim(-10, 10)
            ax.set_title(graph_title)
            ax.set_xlabel("Output Power (dBm)")
            ax.set_ylabel("Delta Expected / Actual (dBm)")
            handles, labels = ax.get_legend_handles_labels()
            legend = ax.legend(handles, labels, loc="upper center",
                               bbox_to_anchor=(0.5,-0.1))
            filename = "tx-power-" + "-".join([str(s) for s in graph_name])
            figure.savefig(os.path.join(output_dir, filename + ".png"),
                           bbox_extra_artists=(legend,), bbox_inches="tight")
            figure.clear()
            plt.close(figure)
