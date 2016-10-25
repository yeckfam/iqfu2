"""
tx_evm_vs_gain
--------------
"""
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

GRAPHS = [
    {
        "title": "Power vs. Analog Gain Index",
        "location": 221,
        "x": lambda df: df["GAIN_INDEX"],
        "y": lambda df: df["POWER_LEVELS_AVG_DBM"],
        "xlabel": "Analog Gain Index (Digital Gain = -10)",
        "ylabel": "Output Power (dBm)",
        "xlim": [0, 31],
        "ylim": [-30, 40],
        "limits": lambda limits: []
    },
    {
        "title": "Power vs. Digital Gain",
        "location": 222,
        "x": lambda df: df["DAC_GAIN"],
        "y": lambda df: df["POWER_LEVELS_AVG_DBM"],
        "xlabel": "Digital Gain (Analog Gain Index = 10)",
        "ylabel": "Output Power (dBm)",
        "xlim": [-16, 6],
        "ylim": [-30, 40],
        "limits": lambda limits: []
    },
    {
        "title": "EVM vs. Analog Gain Index",
        "location": 223,
        "x": lambda df: df["GAIN_INDEX"],
        "y": lambda df: df["EVM_VALUES_AVG_DB"],
        "xlabel": "Analog Gain Index (Digital Gain = -10)",
        "ylabel": "EVM (dB)",
        "xlim": [0, 31],
        "ylim": [-40, 0],
        "limits": lambda limits: [[limits["EVM_LIMIT"] for i in range(2)]]
    },
    {
        "title": "EVM vs. Digital Gain",
        "location": 224,
        "x": lambda df: df["DAC_GAIN"],
        "y": lambda df: df["EVM_VALUES_AVG_DB"],
        "xlabel": "Digital Gain (Analog Gain Index = 10)",
        "ylabel": "EVM (dB)",
        "xlim": [-16, 6],
        "ylim": [-40, 0],
        "limits": lambda limits: [[limits["EVM_LIMIT"] for i in range(2)]]
    }
]

GROUPINGS = (
    (
        ("STANDARD", "DATA_RATE", "BSS_BANDWIDTH", "RADIO", "BAND"),
        ("CHAIN", "BSS_FREQ_MHZ_PRIMARY", "TEST_NAME")
    ),
)

WIDE_TO_LONG = (
    "DAC_GAIN", "EXPECTING_TX_POWER_LEVELS_DBM", "GAIN_INDEX",
    "EVM_VALUES_AVG_DB", "POWER_LEVELS_AVG_DBM"
)

LIMITS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "resources", "limits"
)

def graph_gain(data_frame, output_dir):
    limits = pd.read_csv(os.path.join(LIMITS, "tx_evm.csv"))
    for (graph_grouping, line_grouping) in GROUPINGS:
        for graph_name, graph_data in data_frame.groupby(graph_grouping, sort=False):
            # hack to make the graph title look good
            graph_title = "Tx EVM vs. Gain ("
            if "TEST_NAME" in graph_grouping:
                graph_title +=  ", ".join(graph_name[0:3]) + ")\n" + graph_name[3]
            else:
                graph_title +=  ", ".join([str(s) for s in graph_name]) + ")"

            figure = plt.figure(figsize=(20, 10))
            for graph in GRAPHS:
                graph["subplot"] = figure.add_subplot(graph["location"])

            for step_num, step_data in graph_data.groupby("STEP_NUM", sort=False):
                data = step_data.sort(["DAC_GAIN", "GAIN_INDEX"])
                # figure out if this is the analog or digital sweep
                if data["DAC_GAIN"].values[0] == -10:
                    graphs = [0, 2]
                else:
                    graphs = [1]


                GRAPHS[2]["labels"] = set()
                for line_name, line_data in data.groupby(line_grouping, sort=False):
                    chain = line_data["CHAIN"].values[0]
                    color = "blue"
                    if chain == "Chain 2":
                        color = "green"
                    if 1 in graphs:
                        GRAPHS[3]["subplot"].plot(
                            np.gradient(
                                line_data["GAIN_INDEX"],
                                line_data["POWER_LEVELS_AVG_DBM"]
                            ),
                            marker=".",
                            color=color
                        )
                    for graph_idx in graphs:
                        graph = GRAPHS[graph_idx]
                        label = "_nolegend"
                        if graph_idx == 2 and chain not in graph["labels"]:
                            graph["labels"].add(chain)
                            label = chain
                        graph["subplot"].plot(
                            graph["x"](line_data),
                            graph["y"](line_data),
                            marker=".",
                            label=label,
                            color=color
                        )

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
                graph["subplot"].plot(
                    graph["xlim"],
                    [limit["EERO_TARGET_POWER"] for _ in range(2)],
                    color="g",
                    linestyle="--"
                )
                for l in graph["limits"](limit):
                    graph["subplot"].plot(
                        graph["xlim"], l, color="r", linestyle="--"
                    )

            handles, labels = GRAPHS[2]["subplot"].get_legend_handles_labels()
            legend = GRAPHS[2]["subplot"].legend(
                handles, ["Chain 1", "Chain 2"], loc="upper center", bbox_to_anchor=(1.0, -0.2)
            )
            filename = "tx-evm-vs-gain-" + "-".join(
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

    # skip failed tests
    data_frame = data_frame[data_frame["EVM_VALUES_AVG_DB_0"] != -99999.99]

    # deal with nasty string columns
    max_power_levels = data_frame["NUMBER_OF_POWER_LEVELS"].max()
    for column in ("DAC_GAIN", "EXPECTING_TX_POWER_LEVELS_DBM", "GAIN_INDEX"):
        df = data_frame[column].str.split(" ", expand=True).astype(float)
        df.rename(
            columns={i: column + "_" + str(i) for i in range(max_power_levels)},
            inplace=True
        )
        data_frame = pd.concat((data_frame, df), axis=1)
    data_frame.to_csv("fixed.csv")


    # transform wide to long
    data_frame["id"] = data_frame.index
    data_frame = pd.wide_to_long(
        data_frame,
        [column + "_" for column in WIDE_TO_LONG],
        i="id", j="idx"
    )
    data_frame.reset_index(level=1, inplace=True)
    data_frame.sort("idx", inplace=True)

    # remove underscores from flipped column names
    for column in WIDE_TO_LONG:
        data_frame[column] = data_frame[column + "_"]

    # add in radio information
    data_frame["RADIO"] = map(
        lambda f: "Radio " + str(int((f < 5180 or f > 5240))),
        data_frame["BSS_FREQ_MHZ_PRIMARY"]
    )

    # add in band information
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

    # normalize data rate column
    data_frame["DATA_RATE"] = data_frame["DATA_RATE_x"]
    data_frame.to_csv("foobar.csv")

    graph_gain(data_frame, output_dir)
