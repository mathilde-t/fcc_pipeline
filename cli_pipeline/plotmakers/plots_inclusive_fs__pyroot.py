"""
Run with:
python plotmakers/plots_inclusive_fs__pyroot.py
"""

import ROOT
import os
from scripts.config import get_config
from utils_cli.path_utils import make_norm_dir_name

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def run_inclusive_plots(cfg):

    normalisationTag = cfg.lumi_scaling["normalisation"]
    outputDir = cfg.outputDir

    sample_label = outputDir.split("/")[-1]
    inputDir = make_norm_dir_name(outputDir) if normalisationTag else outputDir
    outdir = f"./output/plots/{sample_label}"
    outdir = make_norm_dir_name(outdir) if normalisationTag else outdir
    os.makedirs(outdir, exist_ok=True)

    plot_meta = cfg.plotting

    lumi_tex = plot_meta["intLumiLabel"]
    ana_tex = plot_meta["ana_tex"]
    energy = plot_meta["energy"]
    gen_or_reco = plot_meta["gen_or_reco"]
    delphesVersion = plot_meta["delphesVersion"]
    prodTag = cfg.prodTag
    sample_type = cfg.sample_type

    color_map = {
        "red": ROOT.kRed,
        "blue": ROOT.kBlue,
        "green": ROOT.kGreen
    }

    formats = ["png", "pdf"]

    def print_out_doubleline(title):
        print("=" * 80)
        print(title)
        print("-" * 80)

    def print_out_line():
        print("=" * 80)
        print("\n")


    ### open files & trees
    files = {}
    trees = {}
    legend = {}
    colors = {}

    for proc, info in cfg.processList.items():

        path = f"{inputDir}/{proc}.root"
        f = ROOT.TFile.Open(path)
        files[proc] = f

        if not f or f.IsZombie():
            print(f"[ERROR] cannot open {path}")
            continue

        if sample_type == "local":

            tree = f.Get("events")

            if not tree:
                print(f"[ERROR] no tree in {path}")
                continue

            trees[proc] = tree

            print_out_doubleline("proc \t\t\t\t lep \t\t\t tree.GetEntries()")
            print(proc, "\t\t", cfg.processList[proc]["lep"], "\t\t", tree.GetEntries())
            print_out_line()

        elif sample_type == "central":
            # No tree in the file; histograms are stored directly.
            pass

        else:
            raise ValueError(f"Unknown sample type: {sample_type}")


        if info["lep"] == "Electron":
            legend["ee"] = info["plot"]["legend"]
            colors["ee"] = color_map[info["plot"]["color"]]
        elif info["lep"] == "Muon":
            legend["mumu"] = info["plot"]["legend"]
            colors["mumu"] = color_map[info["plot"]["color"]]

    ### histogram maker (local samples) and histgram taker (central samples)
    def make_hist(tree, var, nbins, xmin, xmax, hname,
                    xtitle=None, ytitle=None, ymin=None, ymax=None,
                    ):

        h = ROOT.TH1F(hname, var, nbins, xmin, xmax)
        h.Sumw2()

        tree.Draw(f"{var}>>{hname}", "weight", "goff")

        if xtitle is not None:
            h.GetXaxis().SetTitle(xtitle)

        if ytitle is not None:
            h.GetYaxis().SetTitle(ytitle)

        if ymin is not None:
            h.SetMinimum(ymin)

        #if ymax is not None:
        #    h.SetMaximum(ymax)

        ### debug
        # n = tree.Draw(f"{var}>>{hname}", "", "goff")
        # print_out_doubleline("Draw returned / Tree entries / Hist entries")
        # print(n, "\t\t", tree.GetEntries(), "\t\t", h.GetEntries())
        # print_out_line()

        return h

    def get_hist(rootfile, name,
                xtitle=None,
                ytitle=None,
                ymin=None,
                ymax=None):

        h = rootfile.Get(name)

        if not h:
            print(f"[ERROR] histogram '{name}' not found in {rootfile.GetName()}")
            return None

        # Detach histogram from the file
        h = h.Clone(f"{h.GetName()}_{ROOT.TUUID().AsString()}")
        h.SetDirectory(0)

        if xtitle is not None:
            h.GetXaxis().SetTitle(xtitle)
            title = name.split("_", 1)[1]
            h.SetTitle(title)

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

        var = cfg_hist["output"]

        c = ROOT.TCanvas(f"c_{name}", "c", 800, 600)
        c.SetLeftMargin(0.12)
        c.SetRightMargin(0.15)
        c.SetTopMargin(0.12)

        h_ee = None
        h_mu = None

        ### build histograms per channel
        for proc, f in files.items():

            lep = cfg.processList[proc]["lep"]
            hname = f"h_{var}_{proc}"
            print("histogram : ",name)

            if sample_type == "local":

                tree = trees[proc]

                h = make_hist(
                    tree,
                    var,
                    cfg_hist["bins"] if "bins" in cfg_hist else 50,
                    cfg_hist["xmin"],
                    cfg_hist["xmax"],
                    hname,
                    xtitle=cfg_hist["xtitle"], 
                    ytitle=cfg_hist["ytitle"], 
                    ymin=cfg_hist["ymin"], 
                    ymax=cfg_hist["ymax"]
                )

            elif sample_type == "central":

                lep = cfg.processList[proc]["lep"]
                hname = f"{lep}_{var}"

                h = get_hist(
                    f,
                    hname,
                    xtitle=cfg_hist["xtitle"],
                    ytitle=cfg_hist["ytitle"],
                    ymin=cfg_hist["ymin"],
                    ymax=cfg_hist["ymax"],
                )

                if h is None:
                    continue


            if lep == "Electron":
                #cut = "abs(lepton_pdgId)==11"
                if h_ee is None:
                    h_ee = h.Clone("h_ee")
                else:
                    h_ee.Add(h)

            elif lep == "Muon":
                #cut = "abs(lepton_pdgId)==13"
                if h_mu is None:
                    h_mu = h.Clone("h_mu")
                else:
                    h_mu.Add(h)

        ### safety check
        if not h_ee or not h_mu:
            print(f"[WARNING] missing channel for {var}")
            continue

        ### styling
        h_ee.SetLineColor(colors["ee"])
        h_mu.SetLineColor(colors["mumu"])

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
        leg.AddEntry(h_ee, legend.get("ee", "e channel"), "l")
        leg.AddEntry(h_mu, legend.get("mumu", "#mu channel"), "l")
        leg.Draw()

        ### labels
        level = (
            "Gen-level"
            if gen_or_reco != "reco"
            else f"Reco-level{f' (delphes {delphesVersion})' if delphesVersion else ''}"
        )

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)

        latex.DrawLatex(0.12, 0.96, sample_label)
        latex.DrawLatex(0.12, 0.92, ana_tex)
        latex.DrawLatex(0.68, 0.92, f"#sqrt{{s}} = {energy} GeV")
        if lumi_tex is not None:
            latex.DrawLatex(0.69, 0.96, lumi_tex)
        latex.DrawLatex(0.15, 0.82, level)
        if normalisationTag:
            latex.SetTextSize(0.028)
            latex.DrawLatex(0.15, 0.78, "Luminosity scaled")

        ### save
        file_name = f"{name}_{sample_label}"
        file_name_norm = make_norm_dir_name(file_name) if normalisationTag else file_name

        for fmt in formats:
            c.SaveAs(f"{outdir}/{file_name_norm}.{fmt}")

        print(f"[OK] saved {name}")
