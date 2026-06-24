'''
run with : python 3_plotmakers/plot_nTuple.py

This script makes analougous plots to the ones in 1_histmakers/hists_ee_mumu.py, 
but using the flat nTuples created with 2_treemakers/tree.py.
'''

import uproot
import matplotlib.pyplot as plt
import numpy as np

# open ROOT file
file_ee = uproot.open("./output/2_treemakers/convertEDMtoNanoAODlike/ee_ee_ecm91_delphes.root")
file_mumu = uproot.open("./output/2_treemakers/convertEDMtoNanoAODlike/ee_mumu_ecm91_delphes.root")

axis_mapping = {"dilepton_m" : {"xmin":     0,
                                "xmax":     100,
                                "ymin":     0,
                                "ymax":     2000,
                                "bins":     150,
                                "rebin":     5,},
                "dilepton_p" : {"xmin":     0,
                                "xmax":     60,
                                "ymin":     0,
                                "ymax":     2000,
                                "bins":     200,
                                "rebin":     8,},
                "lep0_p" : {"xmin":     0,
                            "xmax":     100,
                            "ymin":     0,
                            "ymax":     2000,
                            "bins":     200,
                            "rebin":     5,},
                "lep1_p" : {"xmin":     0,
                            "xmax":     100,
                            "ymin":     0,
                            "ymax":     2000,
                            "bins":     200,
                            "rebin":     5,},
                "lep0_pt" : {"xmin":     0,
                            "xmax":     70,
                            "ymin":     0,
                            "ymax":     300,
                            "bins":     200,
                            "rebin":     7,},
                "lep1_pt" : {"xmin":     0,
                            "xmax":     70,
                            "ymin":     0,
                            "ymax":     300,
                            "bins":     200,
                            "rebin":     7,},
                "lep0_eta" : {"xmin":     -3,
                            "xmax":     3,
                            "ymin":     0,
                            "ymax":     60,
                            "bins":     600,
                            "rebin":     5,},
                "lep1_eta" : {"xmin":     -3,
                            "xmax":     3,
                            "ymin":     0,
                            "ymax":     60,
                            "bins":     600,
                            "rebin":     5,},
                "lep0_phi" : {"xmin":     -5,
                            "xmax":     5,
                            "ymin":     0,
                            "ymax":     60,
                            "bins":     500,
                            "rebin":     5,},
                "lep1_phi" : {"xmin":     -5,
                            "xmax":     5,
                            "ymin":     0,
                            "ymax":     60,
                            "bins":     500,
                            "rebin":     5,}, 
            }

# access tree
tree_ee = file_ee["events"]
tree_mumu = file_mumu["events"]

variables = tree_ee.keys()
print("Available variables:", variables)

# load branch as numpy array
for var in variables:
    print(f"{var}: {tree_ee[var].array(library='np').shape}")
    var_ee_array = tree_ee[var].array(library="np")
    var_mumu_array = tree_mumu[var].array(library="np")

    # create figure
    fig, ax = plt.subplots(figsize=(8, 8))

    bins = np.linspace(
        axis_mapping[var]["xmin"],
        axis_mapping[var]["xmax"],
        axis_mapping[var]["bins"] // axis_mapping[var]["rebin"] + 1,
    )

    # histogram
    # ax.hist(var_ee_array, bins=axis_mapping[var]["bins"]//axis_mapping[var]["rebin"], 
    #         label="ee", color="red", histtype="step")
    # ax.hist(var_mumu_array, bins=axis_mapping[var]["bins"]//axis_mapping[var]["rebin"], 
    #         label="mumu", color="blue", histtype="step")

    ax.hist(
        [var_ee_array, var_mumu_array],
        bins=bins,
        label=["ee", "mumu"],
        color=["red", "blue"],
        histtype="step",
        stacked=True,
    )

    ax.set_xlim(axis_mapping[var]["xmin"], axis_mapping[var]["xmax"])
    ax.set_ylim(axis_mapping[var]["ymin"], axis_mapping[var]["ymax"])

    # title
    ax.set_title(f"{var} distribution for created flat nTuple", fontsize=16, pad=16)

    # labels
    ax.set_xlabel(f"{var}")
    ax.set_ylabel("Events")
    ax.legend()

    ax.grid(alpha=0.3)

    # save
    plt.savefig(f"output/plots/nTuples/{var}_flat_nTuple.pdf")
    plt.savefig(f"output/plots/nTuples/{var}_flat_nTuple.png")
    plt.close()