'''    
    run with : python fcc_pipeline/stepwise_pipeline/plotmakers/plots_inclusive_fs__pyroot.py

    Plotting script for the dilepton analysis with real samples using root, not the fcc plotter,
    because we want to overlay the two channels in the same plot.
    
    Is set up for ee and mumu final states only, no ther leptons, quarks. This need to be 
    reflected in the scripts/data_config.json
'''

import ROOT
import os
from scripts.config import get_config

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

cfg = get_config("local_prod_ee_mumu")

sample_label = cfg.outputDir.split("/")[-1]
inputDir = cfg.outputDir
outdir = f"./output/plots/{sample_label}"
os.makedirs(outdir, exist_ok=True)

COLOR_MAP = {
    "red": ROOT.kRed,
    "blue+1": ROOT.kBlue + 1,
    "green+2": ROOT.kGreen + 2,
}
def resolve_color(name):
    return COLOR_MAP.get(name, ROOT.kBlack)

## global plotting metadata
plot_meta = cfg.plotting

intLumiLabel = plot_meta["intLumiLabel"]
ana_tex = plot_meta["ana_tex"]
delphesVersion = plot_meta["delphesVersion"]
energy = plot_meta["energy"]
collider = 'FCC-ee'
formats        = ['png','pdf']


## build plot layout automatically from processList
colors = {
    "ee": None,
    "mumu": None
}

legend = {
    "ee": None,
    "mumu": None
}

grouped_procs = {
    "ee": [],
    "mumu": []
}

for proc, info in cfg.processList.items():

    lep = info["lep"]

    if lep == "Electron":
        grouped_procs["ee"].append(proc)

        # take first entry as representative style
        if colors["ee"] is None:
            colors["ee"] = resolve_color(info["plot"]["color"])
            legend["ee"] = info["plot"]["legend"]

    elif lep == "Muon":
        grouped_procs["mumu"].append(proc)

        if colors["mumu"] is None:
            colors["mumu"] = resolve_color(info["plot"]["color"])
            legend["mumu"] = info["plot"]["legend"]
    


# -----------------------------
# file names (your ROOT outputs)
# -----------------------------

def get_files(sample_list):
    return [
        ROOT.TFile.Open(f"{inputDir}/{name}.root")
        for name in sample_list
    ]

files = {}
files["ee"] = get_files(grouped_procs['ee'])
files["mumu"] = get_files(grouped_procs['mumu'])

def sum_hists(file_list, hist_name):
    h_total = None

    for f in file_list:
        if not f:
            continue

        h = f.Get(hist_name)
        if not h:
            continue

        h = h.Clone()
        h.SetDirectory(0)

        if h_total is None:
            h_total = h
        else:
            h_total.Add(h)

    return h_total

# -----------------------------
# plotting loop
# -----------------------------

from scripts.plot_config import hists

for name, hist_cfg in hists.items():

    c = ROOT.TCanvas(f"c_{name}", "", 800, 750)

    hist_name = hist_cfg["output"]
    h_ee = sum_hists(files["ee"], hist_name)
    h_mu = sum_hists(files["mumu"], hist_name)

    if not h_ee or not h_mu:
        print(f"[WARNING] missing histogram {name}")
        continue

    # clone for safety
    h_ee = h_ee.Clone()
    h_mu = h_mu.Clone()

    # style
    h_ee.SetLineColor(colors["ee"])
    h_mu.SetLineColor(colors["mumu"])

    h_ee.SetLineWidth(2)
    h_mu.SetLineWidth(2)

    h_ee.SetStats(0)
    h_mu.SetStats(0)

    # rebin
    if hist_cfg["rebin"] > 1:
        h_ee.Rebin(hist_cfg["rebin"])
        h_mu.Rebin(hist_cfg["rebin"])

    # axis ranges
    h_ee.GetXaxis().SetRangeUser(hist_cfg["xmin"], hist_cfg["xmax"])
    h_ee.GetYaxis().SetRangeUser(hist_cfg["ymin"], hist_cfg["ymax"])

    h_ee.GetXaxis().SetTitle(hist_cfg["xtitle"])
    h_ee.GetYaxis().SetTitle(hist_cfg["ytitle"])

    # draw
    if hist_cfg["logy"]:
        c.SetLogy()

    h_ee.Draw("hist")
    h_mu.Draw("hist same")

    # legend
    leg = ROOT.TLegend(0.72, 0.75, 0.88, 0.88)
    leg.AddEntry(h_ee, legend["ee"], "l")
    leg.AddEntry(h_mu, legend["mumu"], "l")
    leg.Draw()

    # CMS-like label
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.DrawLatex(0.12, 0.96, "local_prod_ee_mumu")
    latex.DrawLatex(0.12, 0.92, ana_tex)
    latex.DrawLatex(0.68, 0.92, rf"#sqrt{{s}} = {energy} GeV")

    # save
    for fmt in formats:
        c.SaveAs(f"{outdir}/{name}_{sample_label}.{fmt}")

    print(f"[OK] saved {name}")