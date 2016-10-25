"""
tx_multi_verify
---------------
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

GRAPHS = [
    {
        "title": "EVM vs. Actual Output Power",
        "location": 221,
        "x": lambda df: df["POWER_AVG_DBM"],
        "y": lambda df: df["EVM_AVG_DB"],
        "xlabel": "Actual Output Power (dBm)",
        "ylabel": "EVM (dB)",
        "xlim": [10, 30],
        "ylim": [-40, 0],
        "limits": lambda limits: [[limits["EVM_LIMIT"] for i in range(2)]]
    },
    {
        "title": "Requested vs. Actual Output Power",
        "location": 222,
        "x": lambda df: df["TX_POWER_DBM"],
        "y": lambda df: df["POWER_AVG_DBM"] - df["TX_POWER_DBM"],
        "xlabel": "Requested Output Power (dBm)",
        "ylabel": "Delta Actual to Requested (dB)",
        "xlim": [10, 30],
        "ylim": [-5, 5],
        "limits": lambda _: [[-2, -2], [2, 2]]
    },
    {
        "title": "EVM vs. Requested Output Power",
        "location": 223,
        "x": lambda df: df["TX_POWER_DBM"],
        "y": lambda df: df["EVM_AVG_DB"],
        "xlabel": "Requested Output Power (dBm)",
        "ylabel": "EVM (dB)",
        "xlim": [10, 30],
        "ylim": [-40, 0],
        "limits": lambda limits: [[limits["EVM_LIMIT"] for i in range(2)]]
    },
    {
        "title": "Spectral Mask Margin vs. Output Power",
        "location": 224,
        "xlabel": "Output Power (dBm)",
        "ylabel": "Margin to IEEE Spec (dB)",
        "xlim": [10, 30],
        "ylim": [-5, 20],
        "limits": lambda _: [[0, 0]]
    }
]

GROUPINGS = (
    (
        ("STANDARD", "DATA_RATE", "BSS_BANDWIDTH", "RADIO","BAND"),
        ("CHAIN", "BSS_FREQ_MHZ_PRIMARY", "TEST_NAME")
    ),
)

LIMITS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "limits"
)

def graph_evm(data_frame, output_dir):
    limits = pd.read_csv(os.path.join(LIMITS, "tx_evm.csv"))

    for (graph_grouping, line_grouping) in GROUPINGS:
        for graph_name, graph_data in data_frame.groupby(graph_grouping, sort=False):
            if graph_name[1] == "CCK-11":
                continue

            # hacks to make the graph title look good
            if "TEST_NAME" in graph_grouping:
                graph_title =  " ".join(graph_name[0:3]) + "\n" + graph_name[3]
            else:
                graph_title =  " ".join([str(s) for s in graph_name])
            if "BSS_FREQ_MHZ_PRIMARY" in graph_grouping:
                graph_title += " MHz"

            graph_data.sort("TX_POWER_DBM", inplace=True)

            figure = plt.figure(figsize=(20, 10))
            for graph in GRAPHS:
                graph["subplot"] = figure.add_subplot(graph["location"])

            labels = set()
            for line_name, line_data in graph_data.groupby(line_grouping, sort=False):
                chain = line_data["CHAIN"].values[0]
                color = "blue"
                if chain == "Chain 2":
                    color = "green"
                label = "_nolegend_"
                if chain not in labels:
                    labels.add(chain)
                    label = chain
                for graph in GRAPHS:
                    if graph["title"].startswith("Spectral"):
                        continue
                    graph["subplot"].plot(
                        graph["x"](line_data),
                        graph["y"](line_data),
                        marker=".",
                        label=label,
                        color=color
                    )
#                 for i in ("LOWER", "UPPER"):
#                     for j in xrange(4):
#                         GRAPHS[3]["subplot"].plot(
#                             line_data["POWER_AVG_DBM"],
#                             line_data["MASK_MARGIN_DB_" + i + "_" + str(j + 1)],
#                             marker=".",
#                             label=label,
#                             color=color
#                         )

            # call out the limits in red
            limit = limits[
                (limits["STANDARD"] == graph_name[0]) &
                (limits["DATA_RATE"] == graph_name[1]) &
                ("BW-" + limits["BANDWIDTH"].astype(str) == graph_name[2])
            ]

            for graph in GRAPHS:
                graph["subplot"].grid("on")
                graph["subplot"].set_title(graph["title"])
                graph["subplot"].set_xlim(*graph["xlim"])
                graph["subplot"].set_ylim(*graph["ylim"])
                graph["subplot"].set_xlabel(graph["xlabel"])
                graph["subplot"].set_ylabel(graph["ylabel"])
                
                # graph["subplot"].plot(
#                     [limit["EERO_TARGET_POWER"] for i in range(2)],
#                     graph["ylim"],
#                     color="g",
#                     linestyle="--"
#                 )
#                 for l in graph["limits"](limit):
#                     graph["subplot"].plot(
#                         graph["xlim"], l, color="r", linestyle="--"
#                     )



            handles, labels = GRAPHS[2]["subplot"].get_legend_handles_labels()
            legend = GRAPHS[2]["subplot"].legend(
                handles, labels, loc="upper center", bbox_to_anchor=(1.0, -0.2)
            )
            filename = "tx-multi-verify-" + "-".join(
                [str(s).replace(" ", "-") for s in graph_name]
            )
            figure.suptitle(
                graph_title, fontsize=18, fontweight="bold", y=0.52
            )
            figure.tight_layout(pad=5, h_pad=6)
            figure.savefig(
                os.path.join(output_dir, filename + ".png"),
                bbox_extra_artists=(legend,),
                bbox_inches="tight"
            )
            figure.clear()
            plt.close(figure)

def graph(data_csv, output_dir):
    data_frame = pd.read_csv(data_csv)

    # only take successful runs
    data_frame = data_frame[
        (data_frame["ERROR_MESSAGE"] == "[Info] Function completed.")
    ]

    # add in radio information
    data_frame["RADIO"] = map(
        lambda f: "Radio " + str(0) if f < 5100 else "Radio " + str(1),
        data_frame["BSS_FREQ_MHZ_PRIMARY"]
    )

    # add in chain information
    data_frame = data_frame.assign(
        BAND = lambda x: (
            (data_frame["BSS_FREQ_MHZ_PRIMARY"] / 1000).astype(int).astype(str) + " GHz"
        )
    )

    # add in chain information
    data_frame = data_frame.assign(
        CHAIN = lambda x: (
            "Chain " + (data_frame["TX1"] + 2 * data_frame["TX2"]).astype(str)
        )
    )

    # fix up data
    data_frame["DATA_RATE"] = data_frame["DATA_RATE_x"]
    data_frame["TX_POWER_DBM"] = data_frame["TX_POWER_DBM_x"]

    data_frame.sort(["BSS_FREQ_MHZ_PRIMARY", "CHAIN"], inplace=True)
    data_frame.sort(
        ["DATA_RATE", "BSS_BANDWIDTH"], ascending=False, inplace=True
    )
    data_frame.sort("STANDARD", inplace=True)
    graph_evm(data_frame, output_dir)
