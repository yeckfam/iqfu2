"""
rx_sweep_per
------------
Make an Rx Packet Error Rate graph.

We make one graph for each combination of bandwidth, 802.11 standard,
and data rate, as 10% PER limits are defined in terms of those values.

But then for completeness, we break it down by frequency and by test
name, so that we get to see a bunch of comparisons.
"""
import matplotlib.pyplot as plt
import os
import pandas as pd

LIMITS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "limits", "rx_per.csv"
)

GROUPINGS = (
    (
        ("STANDARD", "DATA_RATE", "BSS_BANDWIDTH", "RADIO","BAND"),
        ("CHAIN", "TEST_NAME")
    ),
)

def graph(data_csv, output_dir):
    data_frame = pd.read_csv(data_csv)
    limits = pd.read_csv(LIMITS)

    # add in radio information
    data_frame["RADIO"] = map(
        lambda f: "Radio " + str(0) if f < 5100 else "Radio " + str(1),
        data_frame["BSS_FREQ_MHZ_PRIMARY"]
    )
    # data_frame["RADIO"] = map(
#         lambda f: "Radio " + str(int((f < 5180 or f > 5240))),
#         data_frame["BSS_FREQ_MHZ_PRIMARY"]
#     )

    # add in band information
    data_frame = data_frame.assign(
        BAND = lambda x: (
            (data_frame["BSS_FREQ_MHZ_PRIMARY"] / 1000).astype(int).astype(str) + " GHz"
        )
    )

    # add in chain information
    data_frame = data_frame.assign(
        CHAIN = lambda x: "Chain " + (data_frame["RX1"] + 2 * data_frame["RX2"]).astype(str)
    )

    for (graph_grouping, line_grouping) in GROUPINGS:
        for graph_name, graph_data in data_frame.groupby(graph_grouping, sort=False):
            # hack to make the graph title look good
            graph_title = "Rx Sensitivity ("
            if "TEST_NAME" in graph_grouping:
                graph_title += ", ".join(graph_name[0:3]) + ")\n" + graph_name[3]
            else:
                graph_title += ", ".join([str(s) for s in graph_name]) + ")"
            figure = plt.figure(figsize=(20, 10))
            ax = figure.add_subplot(111)
            graph_data.sort("BSS_FREQ_MHZ_PRIMARY", inplace=True)
            for line_name, line_data in graph_data.groupby(line_grouping, sort=False):
                chain = line_data["CHAIN"].values[0]
                color = "blue"
                if chain == "Chain 2":
                    color = "green"
                ax.plot(
                    line_data["BSS_FREQ_MHZ_PRIMARY"],
                    line_data["SENS_POWER_LEVEL_DBM"],
                    color=color,
                    label=line_name,
                    marker="d"
                )
            # call out the limit in red
            limit = limits[
                (limits["STANDARD"] == graph_name[0]) &
                (limits["DATA_RATE"] == graph_name[1]) &
                (limits["BANDWIDTH"] == int(graph_name[2][3:])) &
                (limits["SPATIAL_STREAMS"] == 1)
            ]["EERO_SPEC"].values
            ax.grid("on")
            if graph_name[3] == "Radio 0":
                xlim = [2400, 2500]
            elif graph_name[3] == "Radio 1":
            	xlim = [5150, 5850]
            ax.set_xlim(*xlim)
            #ax.plot(xlim, [limit, limit], color="r")
            ax.set_ylim(-95, -80)
            ax.set_title(graph_title)
            ax.set_xlabel("Frequency (MHz)")
            ax.set_ylabel("10% Rx Sensitivity Power (dBm)")
            handles, labels = ax.get_legend_handles_labels()
            legend = ax.legend(handles, labels, loc="upper center",
                               bbox_to_anchor=(0.5,-0.1))
            filename = "rx-sensitivity-" + "-".join([str(s) for s in graph_name])
            figure.savefig(os.path.join(output_dir, filename + ".png"),
                           bbox_extra_artists=(legend,), bbox_inches="tight")
            figure.clear()
            plt.close(figure)
