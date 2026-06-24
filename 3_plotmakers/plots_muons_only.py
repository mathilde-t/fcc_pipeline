'''
run with : fccanalysis plots 3_plotmakers/plots_muons_only.py 
'''

import ROOT

# global parameters
intLumi        = 1.
intLumiLabel   = "L = 5 ab^{-1}"
ana_tex        = 'e^{+}e^{-} #rightarrow #mu^{+}#mu^{-} + X'
delphesVersion = '3.4.2'
energy         = 91.0
collider       = 'FCC-ee'
formats        = ['png','pdf']

outdir         = './output/plots/' 
inputDir       = './output/histmaker/' 

plotStatUnc    = True

colors = {}
#colors['ee_reco'] = ROOT.kRed
colors['mumu_reco'] = ROOT.kBlue+1
#colors['tautau_reco'] = ROOT.kGreen+2
#colors['ll_reco'] = ROOT.kMagenta+2

procs = {}
procs['signal'] = {
    #'ee_reco':      ['ee_ee_ecm91_delphes'],
    'mumu_reco':    ['ee_mumu_ecm91_delphes'],
    #'tautau_reco':  ['ee_tautau_ecm91_delphes'],
    #'ll_reco':      ['ee_ll_ecm91_delphes'],
}
procs['backgrounds'] = {}
#procs['backgrounds'] =  {'WW':['p8_ee_WW_mumu_ecm240'], 'ZZ':['p8_ee_ZZ_mumubb_ecm240']}
#procs['backgrounds'] =  {'ZZ':['p8_ee_ZZ_mumubb_ecm240']}

legend = {}
#legend['ee_reco'] = 'e^{+}e^{-}'
legend['mumu_reco'] = '#mu^{+}#mu^{-}'
#legend['tautau_reco'] = '#tau^{+}#tau^{-}'
#legend['ll_reco'] = '#ell^{+}#ell^{-}'



hists = {}

hists["dilepton_m"] = {
    "output":   "dilepton_m",
    "logy":     False,
    "stack":    True,
    "rebin":    5,
    "xmin":     0,
    "xmax":     100,
    "ymin":     0,
    "ymax":     1500,
    "xtitle":   "m(#ell^{#plus}#ell^{#minus}) (GeV)",
    "ytitle":   "Events ",
}

hists["dilepton_p"] = {
    "output":   "dilepton_p",
    "logy":     False,
    "stack":    True,
    "rebin":    5,
    "xmin":     0,
    "xmax":     200,
    "ymin":     0,
    "ymax":     1500,
    "xtitle":   "p(#ell^{#plus}#ell^{#minus}) (GeV)",
    "ytitle":   "Events ",
}

hists["muon_p"] = {
    "output":   "muon_p",
    "logy":     False,
    "stack":    True,
    "rebin":    5,
    "xmin":     0,
    "xmax":     200,
    "ymin":     0,
    "ymax":     1000,
    "xtitle":   "p(#mu) (GeV)",
    "ytitle":   "Events",
}

hists["muon_pt"] = {
    "output":   "muon_pt",
    "logy":     False,
    "stack":    True,
    "rebin":    5,
    "xmin":     0,
    "xmax":     200,
    "ymin":     0,
    "ymax":     1000,
    "xtitle":   "p_T(#mu) (GeV)",
    "ytitle":   "Events ",
}

hists["muon_eta"] = {
    "output":   "muon_eta",
    "logy":     False,
    "stack":    True,
    "rebin":    5,
    "xmin":     -3,
    "xmax":     3,
    "ymin":     0,
    "ymax":     1000,
    "xtitle":   "#eta(#mu)",
    "ytitle":   "Events ",
}

hists["muon_phi"] = {
    "output":   "muon_phi",
    "logy":     False,
    "stack":    True,
    "rebin":    5,
    "xmin":     -5,
    "xmax":     5,
    "ymin":     0,
    "ymax":     1000,
    "xtitle":   "#phi(#mu) (rad)",
    "ytitle":   "Events ",
}