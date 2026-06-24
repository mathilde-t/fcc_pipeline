'''
run with : fccanalysis plots 3_plotmakers/plots_ee_mumu.py 
'''

import ROOT

# global parameters
intLumi        = 1.
#intLumiLabel   = "L = 5 ab^{-1}"
ana_tex        = 'e^{+}e^{-} #rightarrow Z/#gamma^{*} #rightarrow e^{+}e^{-}, #mu^{+}#mu^{-}'
delphesVersion = 'spring21'
energy         = 91.2
collider       = 'FCC-ee'
formats        = ['png','pdf']

sample_label = "real_samples"

outdir         = f"./output/plots/{sample_label}" 
inputDir       = f"./output/histmaker/{sample_label}"

plotStatUnc    = True

procs = {}
procs['signal'] = {
    'ee': ['events_003635753', 'events_007405803', 'events_009996087'],
    'mumu': ['events_003635753', 'events_007405803', 'events_009996087'],
}

procs['backgrounds'] = {}

colors = {
    'ee': ROOT.kRed,
    'mumu': ROOT.kBlue+1
}

legend = {
    'ee': 'e^{+}e^{-}',
    'mumu': '#mu^{+}#mu^{-}'
}



hists = {}

for lep in ['Electron', 'Muon']:
    hists[f"{lep}_p"] = {
        "output":   f"{lep}_p",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     0,
        "xmax":     100,
        "ymin":     0,
        "ymax":     2000,
        "xtitle":   f"p({lep}) (GeV)",
        "ytitle":   "Events",
    }

    hists[f"{lep}_dilepton_m"] = {
        "output":   f"{lep}_dilepton_m",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     0,
        "xmax":     100,
        "ymin":     0,
        "ymax":     2000,
        "xtitle":   f"m(dilepton {lep}) (GeV)",
        "ytitle":   "Events ",
    }

    hists[f"{lep}_dilepton_p"] = {
        "output":   f"{lep}_dilepton_p",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     0,
        "xmax":     60,
        "ymin":     0,
        "ymax":     2000,
        "xtitle":   f"p(dilepton {lep}) (GeV)",
        "ytitle":   "Events ",
    }

    hists[f"{lep}_lep0_p"] = {
        "output":   f"{lep}_lep0_p",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     0,
        "xmax":     100,
        "ymin":     0,
        "ymax":     2000,
        "xtitle":   f"p(leading lepton {lep}) (GeV)",
        "ytitle":   "Events",
    }

    hists[f"{lep}_lep1_p"] = {
        "output":   f"{lep}_lep1_p",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     0,
        "xmax":     100,
        "ymin":     0,
        "ymax":     2000,
        "xtitle":   f"p(subleading lepton {lep}) (GeV)",
        "ytitle":   "Events",
    }

    hists[f"{lep}_lep0_pt"] = {
        "output":   f"{lep}_lep0_pt",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     0,
        "xmax":     70,
        "ymin":     0,
        "ymax":     300,
        "xtitle":   f"p_{{T}}(leading lepton {lep}) (GeV)",
        "ytitle":   "Events",
    }

    hists[f"{lep}_lep1_pt"] = {
        "output":   f"{lep}_lep1_pt",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     0,
        "xmax":     70,
        "ymin":     0,
        "ymax":     300,
        "xtitle":   f"p_{{T}}(subleading lepton {lep}) (GeV)",
        "ytitle":   "Events",
    }

    hists[f"{lep}_lep0_eta"] = {
        "output":   f"{lep}_lep0_eta",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     -3,
        "xmax":     3,
        "ymin":     0,
        "ymax":     60,
        "xtitle":   f"#eta(leading lepton {lep})",
        "ytitle":   "Events",
    }

    hists[f"{lep}_lep1_eta"] = {
        "output":   f"{lep}_lep1_eta",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     -3,
        "xmax":     3,
        "ymin":     0,
        "ymax":     60,
        "xtitle":   f"#eta(subleading lepton {lep})",
        "ytitle":   "Events",
    }

    hists[f"{lep}_lep0_phi"] = {
        "output":   f"{lep}_lep0_phi",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     -5,
        "xmax":     5,
        "ymin":     0,
        "ymax":     60,
        "xtitle":   f"#phi(leading lepton {lep}) (rad)",
        "ytitle":   "Events",
    }

    hists[f"{lep}_lep1_phi"] = {
        "output":   f"{lep}_lep1_phi",
        "logy":     False,
        "stack":    True,
        "rebin":    5,
        "xmin":     -5,
        "xmax":     5,
        "ymin":     0,
        "ymax":     60,
        "xtitle":   f"#phi(subleading lepton {lep}) (rad)",
        "ytitle":   "Events",
    }