"""
Pyroot plotting script to plot all samples from the treemaker output for central samples, where a 
categorisation of the inclusive sample to signal-like and background-like is performed in addition 
to the usual normalisation and co.

Run with:
python plotmakers/plots_categorisation.py
"""

import ROOT
import os
from utils_cli.path_utils import make_norm_dir_name, print_out_doubleline, print_out_line
from scripts.lep_list import LEP_LIST, branch_name, fill_weight

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTitleX(0.6)
ROOT.gStyle.SetTitleY(0.85)

categories = {
    "inclusive": "weight",
    "signal_like": "weight*(%s_event_category == 1)",
    "background_like": "weight*(%s_event_category == 0)",
}

def run_category_plots(cfg, cfg_name):

    normalisationTag = cfg.lumi_scaling["normalisation"]

    inputDir = os.path.join(
        "./output/treemaker/",
        cfg.outputDir if not normalisationTag else make_norm_dir_name(cfg.outputDir),
        cfg_name
    )

    outdir = os.path.join(
        "./output/plots_root/",
        cfg.outputDir if not normalisationTag else make_norm_dir_name(cfg.outputDir),
        cfg_name
    )
    os.makedirs(outdir, exist_ok=True)

    plot_meta = cfg.plotting

    lumi_tex = plot_meta["intLumiLabel"]
    ana_tex = plot_meta["ana_tex"]
    energy = plot_meta["energy"]
    gen_or_reco = plot_meta["gen_or_reco"]
    delphesVersion = plot_meta["delphesVersion"]
    prodTag = cfg.prodTag
    sample_type = cfg.sample_type

    formats = ["png", "pdf"]

    ### open files & trees
    files = {}
    trees = {}
    legend = {}
    colors = {}

    for proc, info in cfg.processList.items():

        path = f"{inputDir}/{proc}.root"
        f = ROOT.TFile.Open(path)

        if not f or f.IsZombie():
            print("[ERROR] Cannot open:", path)
            continue

        tree = f.Get("events")
        if not tree:
            print(f"[ERROR] no tree in {path}")
            continue

        files[proc] = f
        trees[proc] = tree

        legend = {
            "Electron": "e^{+}e^{-}",
            "Muon": "#mu^{+}#mu^{-}"
        }

        colors = {
            "Electron": ROOT.kRed,
            "Muon": ROOT.kBlue
        }

    ### histogram maker
    def make_hist(tree, var, nbins, xmin, xmax, hname,
                    selection="weight",
                    xtitle=None, ytitle=None, ymin=None, ymax=None,
                    ):

        h = ROOT.TH1F(hname, "", nbins, xmin, xmax)
        h.Sumw2()

        #tree.Draw(
        #    f"{var}>>{hname}",
        #    selection,
        #    "goff"
        #)

        n = tree.Draw(
            f"{var}>>{hname}",
            selection,
            "goff"
        )

        print("Entries filled:", n)

        if xtitle is not None:
            h.GetXaxis().SetTitle(xtitle)

        if ytitle is not None:
            h.GetYaxis().SetTitle(ytitle)

        if ymin is not None:
            h.SetMinimum(ymin)
            
        if ymax is not None:
            h.SetMaximum(ymax)

        return h


    ### plotting config
    from scripts.plot_config import hists

    print("Available hists:", list(hists.keys()))

    ### plot loop
    for name, cfg_hist in hists.items():

        print("Now plotting:", name)

        if "xmin" not in cfg_hist:
            print("Missing xmin in:", name)
            print(cfg_hist)
            continue

        var = cfg_hist["output"]

        c = ROOT.TCanvas(f"c_{name}", "c", 800, 600)
        c.SetLeftMargin(0.12)
        c.SetRightMargin(0.15)
        c.SetTopMargin(0.12)

        hists_per_category = {
            cat: {lep: None for lep in LEP_LIST}
            for cat in categories
        }

        for proc in files:
            tree = trees[proc]

            if "mumu" in proc.lower():
                lep = "Muon"
            elif "ee" in proc.lower():
                lep = "Electron"
            else:
                raise ValueError(f"Cannot determine lepton type from process '{proc}'")

            branch = branch_name(lep, var)

            for category, selection in categories.items():

                if category == "inclusive":
                    cut = selection
                else:
                    cut = selection % lep

                cut = fill_weight(var, cut)

                h = make_hist(
                    tree,
                    branch,
                    cfg_hist["bins"] if "bins" in cfg_hist else 50,
                    cfg_hist["xmin"],
                    cfg_hist["xmax"],
                    f"h_{branch}_{proc}_{category}",
                    selection=cut,
                    xtitle=cfg_hist["xtitle"],
                    ytitle=cfg_hist["ytitle"],
                    ymin=cfg_hist["ymin"],
                    ymax=cfg_hist["ymax"],
                )

                if hists_per_category[category][lep] is None:
                    hists_per_category[category][lep] = h.Clone(
                        f"h_{lep}_{category}"
                    )
                else:
                    hists_per_category[category][lep].Add(h)

            
        for category in categories:
            h_ee = hists_per_category[category]["Electron"]
            h_mu = hists_per_category[category]["Muon"]

            #### safety check
            if not h_ee or not h_mu:
                print(f"[WARNING] missing channel for {var}")
                continue

            ### styling
            h_ee.SetLineColor(colors["Electron"])
            h_mu.SetLineColor(colors["Muon"])

            h_ee.SetLineWidth(2)
            h_mu.SetLineWidth(2)

            if cfg_hist["logy"]:
                c.SetLogy()

            ### draw
            if h_ee.GetMaximum() >= h_mu.GetMaximum():
                h_ee.Draw("hist")
                h_mu.Draw("hist same")
            else:
                h_mu.Draw("hist")
                h_ee.Draw("hist same")
            
            ### legend
            #leg = ROOT.TLegend(0.79, 0.74, 0.88, 0.85) #legend inside
            leg = ROOT.TLegend(1.0, 0.75, 0.87, 0.86) #legend outside
            leg.AddEntry(h_ee, legend["Electron"], "l")
            leg.AddEntry(h_mu, legend["Muon"], "l")
            leg.Draw()

            ### labels
            level = (
                "Gen-level"
                if gen_or_reco != "reco"
                else f"Reco-level{f' (delphes {delphesVersion})' if delphesVersion else ''}"
            )

            latex = ROOT.TLatex()
            latex.SetNDC()                              # Normalized Device Coordinates
            latex.SetTextSize(0.033)

            latex.DrawLatex(0.12, 0.96, cfg_name)
            latex.DrawLatex(0.12, 0.92, ana_tex)
            latex.DrawLatex(0.68, 0.92, f"#sqrt{{s}} = {energy} GeV")
            latex.DrawLatex(0.15, 0.82, level)
            latex.DrawLatex(0.15, 0.77, category)
            if normalisationTag:
                #latex.SetTextSize(0.028)
                #latex.DrawLatex(0.15, 0.78, "Luminosity scaled")
                latex.DrawLatex(0.69, 0.96, lumi_tex)

            ### save
            file_name = f"{name}__{category}__{cfg_name}"
            file_name_norm = file_name if not normalisationTag else make_norm_dir_name(file_name)
            file_name_norm = f"{file_name_norm}"

            for fmt in formats:
                c.SaveAs(f"{outdir}/{file_name_norm}.{fmt}")

            print(f"[OK] saved {name}")
