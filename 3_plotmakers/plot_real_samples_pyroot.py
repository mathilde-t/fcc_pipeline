'''
    Plotting script for the dilepton analysis with real samples using root, not the fcc plotter,
    because we want to overlay the two channels in the same plot.
    
    run with python plot_real_samples_pyroot.py
'''

import ROOT
import os

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

# -----------------------------
# global parameters (same as FCC script)
# -----------------------------
intLumi = 1.
ana_tex = 'e^{+}e^{-} #rightarrow Z/#gamma^{*} #rightarrow e^{+}e^{-}, #mu^{+}#mu^{-}'
collider = 'FCC-ee'

procs = {}

energy = 240
sample_label = "real_samples"
procs['signal'] = {
    'ee': ['events_003635753', 'events_007405803', 'events_009996087'],
    'mumu': ['events_003635753', 'events_007405803', 'events_009996087'],
}

energy = 91.2
sample_label = "wi23_idea_si"
procs['signal'] = {
    'ee': ['events_003136187', 'events_006869229'],
    'mumu': ['events_003136187', 'events_006869229'],
}

energy = 91.188
sample_label = "wi23_idea_wzp6"
procs['signal'] = {
    'ee': ['ee_events_193158988', 'ee_events_194455359'],
    'mumu': ['mumu_events_196687800', 'mumu_events_197347757'],
}

inputDir = f"./output/histmaker/{sample_label}"
outdir = f"./output/plots/{sample_label}"

os.makedirs(outdir, exist_ok=True)

formats = ["png", "pdf"]

# -----------------------------
# colors + labels
# -----------------------------

procs['backgrounds'] = {}

colors = {
    "ee": ROOT.kRed,
    "mumu": ROOT.kBlue + 1
}

legend = {
    "ee": "e^{+}e^{-}",
    "mumu": "#mu^{+}#mu^{-}"
}

# -----------------------------
# hist definitions (your config, slightly adapted)
# -----------------------------
from 3_plotmakers/plot_config import hists
#hists = {
#
#    "dilepton_m": {
#        "output": "dilepton_m",
#        "rebin": 5,
#        "xmin": 0, "xmax": 100,
#        "ymin": 0, "ymax": 2000,
#        "xtitle": "m(dilepton) (GeV)",
#        "ytitle": "Events",
#        "logy": False,
#    },}
#
#    "dilepton_p": {
#        "file": "dilepton_p",
#        "rebin": 5,
#        "xmin": 0, "xmax": 60,
#        "ymin": 0, "ymax": 2000,
#        "xtitle": "p(dilepton) (GeV)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep0_p": {
#        "file": "lep0_p",
#        "rebin": 5,
#        "xmin": 0, "xmax": 100,
#        "ymin": 0, "ymax": 2000,
#        "xtitle": "p(leading lepton) (GeV)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep1_p": {
#        "file": "lep1_p",
#        "rebin": 5,
#        "xmin": 0, "xmax": 100,
#        "ymin": 0, "ymax": 2000,
#        "xtitle": "p(subleading lepton) (GeV)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep0_pt": {
#        "file": "lep0_pt",
#        "rebin": 5,
#        "xmin": 0, "xmax": 70,
#        "ymin": 0, "ymax": 300,
#        "xtitle": "p_{T}(leading lepton) (GeV)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep1_pt": {
#        "file": "lep1_pt",
#        "rebin": 5,
#        "xmin": 0, "xmax": 70,
#        "ymin": 0, "ymax": 300,
#        "xtitle": "p_{T}(subleading lepton) (GeV)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep0_eta": {
#        "file": "lep0_eta",
#        "rebin": 5,
#        "xmin": -3, "xmax": 3,
#        "ymin": 0, "ymax": 60,
#        "xtitle": "#eta(leading lepton)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep1_eta": {
#        "file": "lep1_eta",
#        "rebin": 5,
#        "xmin": -3, "xmax": 3,
#        "ymin": 0, "ymax": 60,
#        "xtitle": "#eta(subleading lepton)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep0_phi": {
#        "file": "lep0_phi",
#        "rebin": 5,
#        "xmin": -5, "xmax": 5,
#        "ymin": 0, "ymax": 60,
#        "xtitle": "#phi(leading lepton) (rad)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#
#    "lep1_phi": {
#        "file": "lep1_phi",
#        "rebin": 5,
#        "xmin": -5, "xmax": 5,
#        "ymin": 0, "ymax": 60,
#        "xtitle": "#phi(subleading lepton) (rad)",
#        "ytitle": "Events",
#        "logy": False,
#    },
#}

# -----------------------------
# file names (your ROOT outputs)
# -----------------------------

def get_files(sample_list):
    return [
        ROOT.TFile.Open(f"{inputDir}/{name}.root")
        for name in sample_list
    ]

files = {}
files["ee"] = get_files(procs['signal']['ee'])
files["mumu"] = get_files(procs['signal']['mumu'])

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

def scale_to_ymax_for_vis_comp_with_fcc_plots(h, ymax):
    if not h:
        return h

    max_bin = h.GetMaximum()

    if max_bin > 0:
        h.Scale(ymax / max_bin)

    return h

for name, cfg in hists.items():

    c = ROOT.TCanvas(f"c_{name}", "", 800, 750)

    h_ee = sum_hists(files["ee"], f"Electron_{cfg['output']}")
    h_mu = sum_hists(files["mumu"], f"Muon_{cfg['output']}")

    if not h_ee or not h_mu:
        print(f"[WARNING] missing histogram {name}")
        continue

    # style
    h_ee.SetLineColor(colors["ee"])
    h_mu.SetLineColor(colors["mumu"])

    h_ee.SetLineWidth(2)
    h_mu.SetLineWidth(2)

    h_ee.SetStats(0)
    h_mu.SetStats(0)

    # rebin
    if cfg["rebin"] > 1:
        h_ee.Rebin(cfg["rebin"])
        h_mu.Rebin(cfg["rebin"])

    # 🔥 visual scaling to FCC y-axis range
    scale_to_ymax_for_vis_comp_with_fcc_plots(h_ee, cfg["ymax"])
    scale_to_ymax_for_vis_comp_with_fcc_plots(h_mu, cfg["ymax"])

    # axis ranges
    h_ee.GetXaxis().SetRangeUser(cfg["xmin"], cfg["xmax"])
    h_ee.GetYaxis().SetRangeUser(cfg["ymin"], cfg["ymax"])

    h_ee.GetXaxis().SetTitle(cfg["xtitle"])
    h_ee.GetYaxis().SetTitle(cfg["ytitle"])

    # draw
    if cfg["logy"]:
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
    latex.DrawLatex(0.12, 0.96, "Centrally produced samples")
    latex.DrawLatex(0.12, 0.92, ana_tex)
    latex.DrawLatex(0.68, 0.92, rf"#sqrt{{s}} = {energy} GeV")

    # save
    for fmt in formats:
        c.SaveAs(f"{outdir}/{name}_{sample_label}.{fmt}")

    print(f"[OK] saved {name}")