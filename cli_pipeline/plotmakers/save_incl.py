"""
Run with:
python plotmakers/plots_inclusive_fs__pyroot.py
"""

import ROOT
import os
from scripts.config import get_config

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def run_inclusive_plots(cfg):

    sample_label = cfg.outputDir.split("/")[-1]
    inputDir = cfg.outputDir
    outdir = f"./output/plots/{sample_label}"
    os.makedirs(outdir, exist_ok=True)

    plot_meta = cfg.plotting

    ana_tex = plot_meta["ana_tex"]
    energy = plot_meta["energy"]
    delphesVersion = plot_meta["delphesVersion"]
    prodTag = cfg.prodTag

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

    for proc, info in cfg.processList.items():

        path = f"{inputDir}/{proc}.root"
        f = ROOT.TFile.Open(path)
        files[proc] = f

        if not f or f.IsZombie():
            print(f"[ERROR] cannot open {path}")
            continue

        tree = f.Get("events")
        if not tree:
            print(f"[ERROR] no tree in {path}")
            continue

        print_out_doubleline("proc \t\t\t\t lep \t\t\t tree.GetEntries()")
        print(proc, "\t\t", cfg.processList[proc]["lep"], "\t\t", tree.GetEntries())
        print_out_line()

        trees[proc] = tree

        if info["lep"] == "Electron":
            legend["ee"] = info["plot"]["legend"]
        elif info["lep"] == "Muon":
            legend["mumu"] = info["plot"]["legend"]

    ### histogram maker (local samples) and histgram taker (central samples)
    def make_hist(tree, var, nbins, xmin, xmax, hname,
                    xtitle=None, ytitle=None, ymin=None, ymax=None,
                    ):

        h = ROOT.TH1F(hname, var, nbins, xmin, xmax)
        h.Sumw2()

        tree.Draw(f"{var} >> {hname}", "", "goff")

        if xtitle is not None:
            h.GetXaxis().SetTitle(xtitle)

        if ytitle is not None:
            h.GetYaxis().SetTitle(ytitle)

        if ymin is not None:
            h.SetMinimum(ymin)

        if ymax is not None:
            h.SetMaximum(ymax)

        ### debug
        # n = tree.Draw(f"{var}>>{hname}", "", "goff")
        # print_out_doubleline("Draw returned / Tree entries / Hist entries")
        # print(n, "\t\t", tree.GetEntries(), "\t\t", h.GetEntries())
        # print_out_line()

        return h


    ### plotting config
    from scripts.plot_config import hists

    print("Available hists:", list(hists.keys()))

    ### plot loop
    for name, cfg_hist in hists.items():

        var = cfg_hist["output"]

        c = ROOT.TCanvas(f"c_{name}", "c", 800, 600)

        h_ee = None
        h_mu = None

        ### build histograms per channel
        #for proc, tree in trees.items():
        for proc, f in files.items():

            lep = cfg.processList[proc]["lep"]
            hname = f"h_{var}_{proc}"
            print("histogram : ",name)

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


            if lep == "Electron":
                #cut = "abs(lepton_pdgId)==11"
                if h_ee is None:
                    h_ee = h.Clone("h_ee")
                    #print("clone ee", h_ee.GetEntries(), hex(ROOT.addressof(h_ee)))
                else:
                    h_ee.Add(h)

            elif lep == "Muon":
                #cut = "abs(lepton_pdgId)==13"
                if h_mu is None:
                    h_mu = h.Clone("h_mu")
                    #print("clone mu", h_mu.GetEntries(), hex(ROOT.addressof(h_mu)))
                else:
                    h_mu.Add(h)

        ### safety check
        if not h_ee or not h_mu:
            print(f"[WARNING] missing channel for {var}")
            continue

        ### styling
        h_ee.SetLineColor(ROOT.kRed)
        h_mu.SetLineColor(ROOT.kBlue)

        h_ee.SetLineWidth(2)
        h_mu.SetLineWidth(2)

        h_ee.GetXaxis().SetTitle(cfg_hist["xtitle"])
        h_ee.GetYaxis().SetTitle(cfg_hist["ytitle"])

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
        leg = ROOT.TLegend(0.72, 0.75, 0.88, 0.88)
        leg.AddEntry(h_ee, legend.get("ee", "e channel"), "l")
        leg.AddEntry(h_mu, legend.get("mumu", "#mu channel"), "l")
        leg.Draw()

        ### labels
        level = (
            f"Reco-level ({plot_meta['delphesVersion']})"
            if cfg.prodTag is None
            else "Gen-level"
        )

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)

        latex.DrawLatex(0.12, 0.96, sample_label)
        latex.DrawLatex(0.12, 0.92, ana_tex)
        latex.DrawLatex(0.68, 0.92, f"#sqrt{{s}} = {energy} GeV")
        latex.DrawLatex(0.68, 0.96, level)

        ### save
        for fmt in formats:
            c.SaveAs(f"{outdir}/{name}_{sample_label}.{fmt}")

        print(f"[OK] saved {name}")
