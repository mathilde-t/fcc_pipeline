"""
Plotting script using awkward array and the comparison option of MPL HEP to display the histograms 
level-wise with the respective ratio plot below. Plots are made per final state particle.
"""

import ROOT
import awkward as ak
import os

import matplotlib.pyplot as plt
import numpy as np
import hist
import mplhep as mh
mh.style.use('CMS')
import matplotlib.patches as patches

from utils_cli.path_utils import make_norm_dir_name, print_out_doubleline, print_out_line
from scripts.lep_list import LEP_LIST,OBJECT_LEVEL_HISTS 
from scripts.plot_config import hists
from scripts.config import get_config
print("Available hists:", list(hists.keys()))

def get_central_config(cfg_name):
    # Find the central reference config corresponding the loaded local config

    if "_gen" in cfg_name:
        level = "gen"
    elif "_reco" in cfg_name:
        level = "reco"
    else:
        raise ValueError(f"Cannot determine level from {cfg_name}")

    central_cfg_name = f"central_prod_ee_mumu_{level}"
    return central_cfg_name, level


def match_processes_by_fs(local_cfg, central_cfg):

    local_groups = {}
    central_groups = {}

    # Group local processes by final state
    for local_proc, local_info in local_cfg.processList.items():

        fs = local_info["fs"]
        if fs not in local_groups:
            local_groups[fs] = []

        local_groups[fs].append(local_proc)


    # Group central processes by final state
    for central_proc, central_info in central_cfg.processList.items():

        fs = central_info["fs"]
        if fs not in central_groups:
            central_groups[fs] = []

        central_groups[fs].append(central_proc)

    matches = []

    # Match groups with same final state
    for fs, local_procs in local_groups.items():

        if fs not in central_groups:
            raise RuntimeError(f"No central processes found for final state {fs}")

        matches.append((local_procs, central_groups[fs]))

    return matches


def root_to_mpl_label(label):

    replacements = {}

    # First: complete variable names
    for coord in ["x", "y", "z"]:
        replacements[f"p{coord}__wo__n_lep_cut"] = (
            rf"p_{{{coord}}}\ \mathrm{{w/o\ cut}}_{{n_{{lep}}}}"
        )

    # Then: individual symbols
    replacements.update({
        " ": r"\ ",
        "#eta": r"\eta",
        "#phi": r"\phi",
        "#theta": r"\theta",
        "#mu": r"\mu",
        "#pi": r"\pi",
        "#sqrt": r"\sqrt",
        "n_lep": r"n_{lep}",
        "#ell": r"\ell",
    })

    for root, mpl in replacements.items():
        label = label.replace(root, mpl)

    if any(sym in label for sym in ["\\", "_", "^"]):
        label = f"${label}$"

    return label


def run_ak_plots(cfg, cfg_name):

    normalisationTag = cfg.lumi_scaling["normalisation"]

    plot_meta = cfg.plotting

    lumi_tex = plot_meta["intLumiLabel"]
    ana_tex = plot_meta["ana_tex"]
    energy = plot_meta["energy"]
    gen_or_reco = plot_meta["gen_or_reco"]
    delphesVersion = plot_meta["delphesVersion"]
    prodTag = cfg.prodTag
    sample_type = cfg.sample_type

    formats = ["png", "pdf"]

    central_cfg_name, level = get_central_config(cfg_name)
    print("Local config name :", cfg_name)
    print("Central config name :", central_cfg_name)
    central_cfg = get_config(central_cfg_name)

    comparisons = match_processes_by_fs(cfg, central_cfg)
    print("\nProcess matching :")
    for local_procs, central_procs in comparisons:
        print("Comparing:", "  ", " + ".join(local_procs), " <--> ", " + ".join(central_procs))
    print("\n")


    inputDir_local = os.path.join(
        "./output/treemaker/",
        cfg.outputDir if not normalisationTag else make_norm_dir_name(cfg.outputDir),
        cfg_name
    )

    inputDir_central = os.path.join(
        "./output/treemaker/",
        central_cfg.outputDir if not normalisationTag else make_norm_dir_name(central_cfg.outputDir),
        central_cfg_name
    )

    outdir = os.path.join(
        "./output/plots_ak/",
        level if not normalisationTag else make_norm_dir_name(level)
    )
    os.makedirs(outdir, exist_ok=True)

    print("inputDir_local", inputDir_local)
    print("inputDir_central", inputDir_central)
    print("outdir", outdir)

    print("\n##############################################\n")

    ### open files & trees
    arrays_local = {}
    arrays_central = {}

    cols = [f"{lep}_{hist}" for lep in LEP_LIST for hist in hists.keys() ] + ["weight"]

    for proc in cfg.processList.keys():
        path = os.path.join(inputDir_local, f"{proc}.root")

        if not os.path.exists(path):
            print("[ERROR] Cannot find local path :", path)
            continue

        rdf = ROOT.RDataFrame("events", path)

        arrays_local[proc] = ak.from_rdataframe(
            rdf,
            columns=cols
        )


    for proc in central_cfg.processList.keys():
        path = os.path.join(inputDir_central, f"{proc}.root")

        if not os.path.exists(path):
            print("[ERROR] Cannot find central path :", path)
            continue

        rdf = ROOT.RDataFrame("events", path)

        arrays_central[proc] = ak.from_rdataframe(
            rdf,
            columns=cols
        )

    lep_to_fs = {
        "Electron": "e",
        "Muon": "mu",
    }

    for lep in LEP_LIST:
        for name_hist, cfg_hist in hists.items():

            print("Histogram:", cfg_hist["xtitle"], " ", lep)

            h1 = hist.Hist.new.Reg(
                cfg_hist["bins"] if "bins" in cfg_hist else 50,
                cfg_hist["xmin"],
                cfg_hist["xmax"],
                name=name_hist,
                label=cfg_hist["xtitle"],
            ).Weight()

            h2 = hist.Hist.new.Reg(
                cfg_hist["bins"] if "bins" in cfg_hist else 50,
                cfg_hist["xmin"],
                cfg_hist["xmax"],
                name=name_hist,
                label=cfg_hist["xtitle"],
            ).Weight()

            for local_procs, central_procs in comparisons:
                branch = f"{lep}_{name_hist}"

                for local_proc in local_procs:

                    # final state matching to proccess
                    # not to add up all the 0s for muon_var in ee and vice versa
                    fs = cfg.processList[local_proc]["fs"]
                    if fs != lep_to_fs[lep]:
                        continue

                    local_values = getattr(arrays_local[local_proc], branch)

                    weights = getattr(arrays_local[local_proc], "weight")
                    
                    if name_hist in OBJECT_LEVEL_HISTS:
                        weights = ak.flatten(ak.broadcast_arrays(local_values, weights)[1])
                        local_values = ak.flatten(local_values)

                    # print("proc:", local_proc)
                    # print("branch", branch)
                    # print(local_values[:20])
                    # print(ak.type(local_values))
                    # print("None:", ak.sum(ak.is_none(local_values)))

                    # arr = arrays_local[local_proc]

                    # print(
                    #     ak.mean(arr["Electron_lep0_p"]), "\t",
                    #     ak.min(arr["Electron_lep0_p"]), "\t",
                    #     ak.max(arr["Electron_lep0_p"])
                    # )
                    # print("")

                    h1.fill(**{name_hist: local_values}, weight=weights)

                for central_proc in central_procs:

                    # final state matching to proccess
                    # not to add up all the 0s for muon_var in ee and vice versa
                    fs = central_cfg.processList[central_proc]["fs"]
                    if fs != lep_to_fs[lep]:
                        continue

                    central_values = getattr(arrays_central[central_proc],branch)

                    weights = getattr(arrays_central[central_proc], "weight")

                    if name_hist in OBJECT_LEVEL_HISTS:
                        weights = ak.flatten(ak.broadcast_arrays(central_values, weights)[1])
                        central_values = ak.flatten(central_values)

                    h2.fill(**{name_hist: central_values}, weight=weights)


            fig, ax_main, ax_comp = mh.comp.hists(
                h1,
                h2,
                comparison='ratio',
                xlabel=root_to_mpl_label(cfg_hist["xtitle"]),
                ylabel='Events',
                h1_label='local',
                h2_label='central',
            )

            #fig.set_size_inches(8.5, 9)
            fig.subplots_adjust(hspace=0.1)
            #fig.tight_layout()

            # ax_main.set_xlabel(ax_main.get_xlabel(), fontsize=26)
            # ax_main.set_ylabel(ax_main.get_ylabel(), fontsize=26)


            # mh.cms.label(
            #     label="Private Work",
            #     data=False,
            #     com=False,
            #     lumi=False,
            #     ax=ax_main,
            # )

            fig.subplots_adjust(top=0.84)
            
            ax_comp.set_ylim(0.5, 1.5)

            ax_main.text(
                0.0, 1.05,
                "FCC-ee",
                transform=ax_main.transAxes,
                fontsize=32,
                fontweight="bold",
                clip_on=False,
            )

            ax_main.text(
                0.215, 1.05,
                "Private Work",
                transform=ax_main.transAxes,
                fontsize=32,
                style="italic",
                clip_on=False,
            )
            
            normtag = cfg.lumi_scaling["normalisation"]
            lumi = cfg.lumi_scaling["intLumi"]

            if normtag:
                ax_main.text(
                    1.0, 1.062,
                    rf"$\mathcal{{L}}={lumi / 1000.0:.1f}\,\mathrm{{ab}}^{{-1}}$",
                    transform=ax_main.transAxes,
                    ha="right",
                    fontsize=22,
                    clip_on=False,
                )
                
                ax_main.text(
                    1.0, 1.01,
                    r"$\sqrt{s}=91.2\,\mathrm{GeV}$",
                    transform=ax_main.transAxes,
                    ha="right",
                    fontsize=22,
                    clip_on=False,
                )
            else:
                ax_main.text(
                    1.0, 1.05,
                    r"$\sqrt{s}=91.2\,\mathrm{GeV}$",
                    transform=ax_main.transAxes,
                    ha="right",
                    fontsize=28,
                    clip_on=False,
                )
            ax_main.text(
                0.5, 0.924,
                f"level: {level}",
                transform=ax_main.transAxes,
                fontsize=22,
                clip_on=False,
            )

            lep_latex = {
                "Electron" : r"e",
                "Muon" : r"\mu",
            }
            ax_main.text(
                0.5, 0.863,
                fr"fs type: ${lep_latex[lep]}$",
                transform=ax_main.transAxes,
                fontsize=22,
                clip_on=False,
            )

            for fmt in formats:
                fig.savefig(os.path.join(outdir, f"{lep}_{name_hist}_comparison.{fmt}"), 
                            dpi=300, bbox_inches="tight")

            ax_main.set_yscale("log")

            for fmt in formats:
                fig.savefig(os.path.join(outdir, f"{lep}_{name_hist}_comparison_log.{fmt}"),
                            dpi=300,bbox_inches="tight")
            
            plt.close(fig)

            #from IPython import embed; embed()