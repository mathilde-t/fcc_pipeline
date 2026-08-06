"""
Plot closure test for the categorisation by generation for the local samples. 

It should always be given the unity of:

(signal + complementary) / inclusive
"""

import os
import ROOT

from utils_cli.path_utils import make_norm_dir_name
from scripts.config import DATACONFS, get_config
from scripts.lep_list import LEP_LIST

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

ROOT.gStyle.SetGridColor(ROOT.kGray + 2)
ROOT.gStyle.SetGridStyle(3)
ROOT.gStyle.SetGridWidth(1)


closure_configs = {
    "gen": {},
    "reco": {},
}

for cfg_name in DATACONFS:
    cfg = get_config(cfg_name)

    # Closure test only exists for local samples
    if cfg.sample_type != "local":
        continue
    level = cfg.plotting["gen_or_reco"]

    if "_ee_mumu_" in cfg_name:
        sample = "inclusive"

    elif "_ee_z_mumu_minus_z_res_" in cfg_name:
        sample = "complementary"

    elif "_ee_z_mumu_" in cfg_name:
        sample = "signal"

    else:
        continue

    closure_configs[level][sample] = (cfg_name, cfg)

formats = ["png", "pdf"]

# histogram helper
def make_hist(tree, var, nbins, xmin, xmax, hname, selection):

    h = ROOT.TH1F(
        hname,
        "",
        nbins,
        xmin,
        xmax,
    )

    h.Sumw2()

    tree.Draw(
        f"{var}>>{hname}",
        selection,
        "goff"
    )

    return h

### plotting config
from scripts.plot_config import hists

# open trees per level
for level in ("gen", "reco"):

    print(f"Running closure test for {level}")

    files = {}
    trees = {
        "inclusive": {},
        "signal": {},
        "complementary": {},
    }

    # open the three local configurations
    for category, (cfg_name, cfg) in closure_configs[level].items():

        normalisationTag = cfg.lumi_scaling["normalisation"]

        inputDir = os.path.join(
            "./output/treemaker",
            cfg.outputDir if not normalisationTag else make_norm_dir_name(cfg.outputDir),
            cfg_name,
        )

        for proc in cfg.processList:

            path = os.path.join(inputDir, f"{proc}.root")
            f = ROOT.TFile.Open(path)

            if not f or f.IsZombie():
                print("[ERROR]", path)
                continue

            tree = f.Get("events")

            if not tree:
                print("[ERROR] no events tree")
                continue

            files[(category, proc)] = f
            trees[category][proc] = tree

            print(category, proc, tree.GetEntries())

    outdir = os.path.join(
        "./output/plots_root/closure_tests",
        level if not normalisationTag else make_norm_dir_name(level),
    )
    os.makedirs(outdir, exist_ok=True)


    for hist_name, hist_cfg in hists.items():
        var = hist_cfg["output"]
        print("Plotting:", hist_name)

        # store categories
        hists_local = {

            "inclusive": {
                lep: None for lep in LEP_LIST
            },
            "signal": {
                lep: None for lep in LEP_LIST
            },
            "complementary": {
                lep: None for lep in LEP_LIST
            }
        }

        # fill histograms
        for category, proc_trees in trees.items():
            for proc, tree in proc_trees.items():

                if "mumu" in proc.lower():
                    lep = "Muon"

                elif "ee" in proc.lower():
                    lep = "Electron"

                else:
                    continue

                branch = f"{lep}_{var}"

                h = make_hist(
                    tree,
                    branch,
                    hist_cfg.get("bins", 50),
                    hist_cfg["xmin"],
                    hist_cfg["xmax"],
                    f"h_{hist_name}_{category}_{lep}_{proc}",
                    "weight",
                )

                if hists_local[category][lep] is None:
                    hists_local[category][lep] = h.Clone(f"h_{category}_{lep}")
                else:
                    hists_local[category][lep].Add(h)


        # make closure ratio
        for lep in LEP_LIST:

            h_inclusive = hists_local["inclusive"][lep]
            h_signal = hists_local["signal"][lep]
            h_background = hists_local["complementary"][lep]

            if not h_inclusive or not h_signal or not h_background:
                print("[WARNING] missing", lep)
                continue

            h_sum = h_signal.Clone(f"h_signal_plus_background_{lep}")
            h_sum.Add(h_background)

            print("signal+bkg:", h_sum.Integral())

            ratio = h_sum.Clone(f"h_closure_{lep}")

            ratio.Divide(h_inclusive)
            ratio.SetLineColor(ROOT.kBlue)
            ratio.SetLineWidth(2)
            ratio.SetMinimum(0.5)
            ratio.SetMaximum(1.5)

            ratio.GetXaxis().SetTitle(hist_cfg["xtitle"])
            ratio.GetYaxis().SetTitle("(Signal + Background) / Inclusive")

            c = ROOT.TCanvas(
                f"c_{lep}",
                "",
                800,
                600
            )

            c.SetLeftMargin(0.12)
            c.SetRightMargin(0.05)
            c.SetTopMargin(0.10)

            c.SetGridx(True)
            c.SetGridy(True)

            ratio.Draw("PE")

            # unity line
            line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1.0, ratio.GetXaxis().GetXmax(), 1.0)

            line.SetLineStyle(2)
            line.SetLineWidth(2)
            line.SetLineColor(ROOT.kBlack)
            line.Draw("same")

            for fmt in formats:
                c.SaveAs(f"{outdir}/{hist_name}_{lep}_closure.{fmt}")

            c.Close()