"""
PyROOT plotting script to compare the local and central pipelines and produce Local/Central ratio plots.

Run with:
python plotmakers/plots_ratio_local_to_central.py
"""

import os
import ROOT

from utils_cli.path_utils import make_norm_dir_name
from scripts.lep_list import LEP_LIST, branch_name, fill_weight
from scripts.config import DATACONFS, get_config

from pprint import pprint

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

# grid style settings
ROOT.gStyle.SetGridColor(ROOT.kGray + 2)
ROOT.gStyle.SetGridStyle(3) #dotted
ROOT.gStyle.SetGridWidth(1)

category_map = {
    "inclusive": ("inclusive", "weight"),
    "signal": ("signal_like", "weight*(%s_event_category == 1)"),
    "complementary": ("background_like", "weight*(%s_event_category == 0)"),
}


### build configuration pairs
ratio_configs = {
    "inclusive": {
        "gen": {},
        "reco": {},
    },
    "signal": {
        "gen": {},
        "reco": {},
    },
    "complementary": {
        "gen": {},
        "reco": {},
    },
}


for cfg_name in DATACONFS:

    cfg = get_config(cfg_name)

    level = cfg.plotting["gen_or_reco"]
    sample_type = cfg.sample_type

    if "_ee_mumu_" in cfg_name:
        sample = "inclusive"

    elif "_ee_z_mumu_minus_z_res_" in cfg_name:
        sample = "complementary"

    elif "_ee_z_mumu_" in cfg_name:
        sample = "signal"

    else:
        continue

    ratio_configs[sample][level][sample_type] = (cfg_name, cfg)


# add central reference for all categories
for level in ["gen", "reco"]:

    central_cfg_name = f"central_prod_ee_mumu_{level}"

    try:
        central_cfg = get_config(central_cfg_name)

    except Exception:
        continue

    for sample in ratio_configs:

        ratio_configs[sample][level]["central"] = (
            central_cfg_name,
            central_cfg,
        )


### debug
# print("ratio_configs:")
# pprint(ratio_configs, sort_dicts=False)
# print(cfg_name, "->", sample)

### main plotting loop

for sample, levels in ratio_configs.items():
    for level, configs in levels.items():

        if not configs:
            continue

        print(f"Running closure test for {level}")

        if "local" not in configs or "central" not in configs:
            continue

        local_cfg_name, local_cfg = configs["local"]
        central_cfg_name, central_cfg = configs["central"]

        ### use local configuration for metadata

        cfg = local_cfg
        cfg_name = local_cfg_name

        normalisationTag = cfg.lumi_scaling["normalisation"]

        inputDir_local = os.path.join(
            "./output/treemaker/",
            cfg.outputDir if not normalisationTag else make_norm_dir_name(cfg.outputDir),
            cfg_name,
        )

        inputDir_central = os.path.join(
            "./output/treemaker/",
            central_cfg.outputDir if not normalisationTag else make_norm_dir_name(central_cfg.outputDir),
            central_cfg_name,
        )

        outdir = os.path.join(
            "./output/plots_root/ratios",
            level,          # gen / reco
            sample,         # inclusive / signal / complementary
        )
        outdir = outdir if not normalisationTag else make_norm_dir_name(outdir)


        os.makedirs(outdir, exist_ok=True)

        ### metadata
        plot_meta = cfg.plotting

        ana_tex = plot_meta["ana_tex"]
        sample_type = cfg.sample_type
        gen_or_reco = plot_meta["gen_or_reco"]
        energy = plot_meta["energy"]
        lumi_tex = plot_meta["intLumiLabel"]
        delphesVersion = plot_meta["delphesVersion"]

        legend = {
            "Electron": "e^{+}e^{-}",
            "Muon": "#mu^{+}#mu^{-}",
        }

        colors = {
            "Electron": ROOT.kRed,
            "Muon": ROOT.kBlue,
        }

        formats = ["png", "pdf"]

        ### plotting variables
        from scripts.plot_config import hists
        print("Available hists:", list(hists.keys()))

        ### open files
        local_files = {}
        central_files = {}
        
        local_trees = {}
        central_trees = {}

        for proc in cfg.processList:
            path = os.path.join(inputDir_local, f"{proc}.root")

            f = ROOT.TFile.Open(path)

            if not f or f.IsZombie():
                print("[ERROR] Cannot open:", path)
                continue

            tree = f.Get("events")
            if not tree:
                print(f"[ERROR] No tree in {path}")
                continue

            local_files[proc] = f
            local_trees[proc] = tree

        for proc in central_cfg.processList:
            path = os.path.join(inputDir_central, f"{proc}.root")

            f = ROOT.TFile.Open(path)

            if not f or f.IsZombie():
                print("[ERROR] Cannot open:", path)
                continue

            tree = f.Get("events")
            if not tree:
                print(f"[ERROR] No tree in {path}")
                continue

            central_files[proc] = f
            central_trees[proc] = tree

        #### debug
        #print("LOCAL INPUT:", inputDir_local)
        #
        #for proc, tree in local_trees.items():
        #    print(
        #        "LOCAL",
        #        proc,
        #        "entries:",
        #        tree.GetEntries()
        #    )
        #
        #print("CENTRAL INPUT:", inputDir_central)
        #
        #for proc, tree in central_trees.items():
        #    print(
        #        "CENTRAL",
        #        proc,
        #        "entries:",
        #        tree.GetEntries()
        #    )

        ### helper
        def make_hist(tree, var, nbins, xmin, xmax, hname, selection):

            h = ROOT.TH1F(hname, "", nbins, xmin, xmax)
            h.Sumw2()

            n = tree.Draw(
                f"{var}>>{hname}",
                selection,
                "goff",
            )

            return h

        ### histogram loop
        for hist_name, hist_cfg in hists.items():

            hist_cfg = hists[hist_name]
            var = hist_cfg["output"]
            print(f"Plotting {hist_name}")

            ### loop over event categories
            central_category, selection = category_map[sample]

            h_local = {lep: None for lep in LEP_LIST}
            h_central = {lep: None for lep in LEP_LIST}

            ### local
            for proc, tree in local_trees.items():

                if "mumu" in proc.lower():
                    lep = "Muon"
                else:
                    lep = "Electron"

                branch = branch_name(lep, var)

                cut = fill_weight(var)

                h = make_hist(
                    tree,
                    branch,
                    hist_cfg.get("bins", 50),
                    hist_cfg["xmin"],
                    hist_cfg["xmax"],
                    f"h_local_{branch}_{proc}_{sample}",
                    cut,
                )

                if h_local[lep] is None:
                    h_local[lep] = h.Clone(f"h_local_{lep}")
                else:
                    h_local[lep].Add(h)

            ### central
            for proc, tree in central_trees.items():
                if "mumu" in proc.lower():
                    lep = "Muon"
                elif "ee" in proc.lower():
                    lep = "Electron"
                else:
                    continue

                branch = branch_name(lep, var)

                if central_category == "inclusive":
                    cut = "weight"
                else:
                    cut = selection % lep

                cut = fill_weight(var, cut)

                h = make_hist(
                    tree,
                    branch,
                    hist_cfg.get("bins", 50),
                    hist_cfg["xmin"],
                    hist_cfg["xmax"],
                    f"h_central_{branch}_{proc}_{sample}",
                    cut,
                )

                if h_central[lep] is None:
                    h_central[lep] = h.Clone(f"h_central_{lep}")
                else:
                    h_central[lep].Add(h)

            ### make ratios
            for lep in LEP_LIST:
                if h_local[lep] is None or h_central[lep] is None:
                    print(f"[WARNING] Missing {lep} histogram.")
                    continue

                ratio = h_local[lep].Clone(f"h_ratio_{lep}")
                ratio.Divide(h_central[lep])

                ratio.SetLineColor(colors[lep])
                ratio.SetLineWidth(2)

                ratio.SetTitle("")
                ratio.GetXaxis().SetTitle(hist_cfg["xtitle"])
                ratio.GetYaxis().SetTitle("Local / Central")

                if "ymin" in hist_cfg:
                    ratio.SetMinimum(0.0)

                if "ymax" in hist_cfg:
                    ratio.SetMaximum(2.0)

                c = ROOT.TCanvas(
                    f"c_{hist_name}_{lep}_{sample}",
                    "",
                    800,
                    600,
                )

                c.SetLeftMargin(0.12)
                c.SetRightMargin(0.05)
                c.SetTopMargin(0.10)

                # grid
                c.SetGridx(True)
                c.SetGridy(True)

                ratio.Draw("PE")

                line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1.0, ratio.GetXaxis().GetXmax(), 1.0)
                line.SetLineStyle(2)
                line.Draw("same")

                leg = ROOT.TLegend(0.70, 0.80, 0.88, 0.88)
                leg.AddEntry(ratio, lep, "l")
                leg.Draw()

                latex = ROOT.TLatex()
                latex.SetNDC()
                latex.SetTextSize(0.033)

                latex.DrawLatex(0.12, 0.92, ana_tex)
                latex.DrawLatex(0.15, 0.86, f"Local: {sample}")
                latex.DrawLatex(0.15, 0.81, f"Central: {central_category}")

                level = (
                    "Gen-level"
                    if gen_or_reco == "gen"
                    else f"Reco-level{f' (Delphes {delphesVersion})' if delphesVersion else ''}"
                )

                latex.DrawLatex(0.15, 0.76, level)
                latex.DrawLatex(0.68, 0.92, f"#sqrt{{s}} = {energy} GeV")

                if normalisationTag:
                    latex.DrawLatex(0.70, 0.96, lumi_tex)

                file_name = (
                    f"{hist_name}"
                    f"__{lep}"
                    f"__{sample}"
                    "__local_vs_central"
                )

                if normalisationTag:
                    file_name = make_norm_dir_name(file_name)

                for fmt in formats:
                    c.SaveAs(os.path.join(outdir, f"{file_name}.{fmt}"))

                c.Close()

