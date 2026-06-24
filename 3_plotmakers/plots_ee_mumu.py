'''
run with : fccanalysis plots 3_plotmakers/plots_ee_mumu.py 
'''

import ROOT

# global parameters
intLumi        = 1.
#intLumiLabel   = "L = 5 ab^{-1}"
ana_tex        = 'e^{+}e^{-} #rightarrow Z/#gamma^{*} #rightarrow e^{+}e^{-}, #mu^{+}#mu^{-}'
delphesVersion = '3.4.2'
energy         = 91.2
collider       = 'FCC-ee'
formats        = ['png','pdf']

sample_label = "diy_samples_delphes"

outdir         = f"./output/plots/{sample_label}" 
inputDir       = f"./output/histmaker/{sample_label}"

plotStatUnc    = True

colors = {}
colors['ee_reco'] = ROOT.kRed
colors['mumu_reco'] = ROOT.kBlue+1
#colors['tautau_reco'] = ROOT.kGreen+2
#colors['ll_reco'] = ROOT.kMagenta+2

procs = {}
procs['signal'] = {
    'ee_reco':      ['ee_ee_ecm91_delphes'],
    'mumu_reco':    ['ee_mumu_ecm91_delphes'],
    #'tautau_reco':  ['ee_tautau_ecm91_delphes'],
    #'ll_reco':      ['ee_ll_ecm91_delphes'],
}
procs['backgrounds'] = {}
#procs['backgrounds'] =  {'WW':['p8_ee_WW_mumu_ecm240'], 'ZZ':['p8_ee_ZZ_mumubb_ecm240']}
#procs['backgrounds'] =  {'ZZ':['p8_ee_ZZ_mumubb_ecm240']}

legend = {}
legend['ee_reco'] = 'e^{+}e^{-}'
legend['mumu_reco'] = '#mu^{+}#mu^{-}'
#legend['tautau_reco'] = '#tau^{+}#tau^{-}'
#legend['ll_reco'] = '#ell^{+}#ell^{-}'

from 3_plotmakers/plot_config import hists

#hists = {}
#
#hists["dilepton_m"] = {
#    "output":   "dilepton_m",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     0,
#    "xmax":     100,
#    "ymin":     0,
#    "ymax":     2000,
#    "xtitle":   "m(dilepton) (GeV)",
#    "ytitle":   "Events ",
#}
#
#hists["dilepton_p"] = {
#    "output":   "dilepton_p",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     0,
#    "xmax":     60,
#    "ymin":     0,
#    "ymax":     2000,
#    "xtitle":   "p(dilepton) (GeV)",
#    "ytitle":   "Events ",
#}
#
#hists["lep0_p"] = {
#    "output":   "lep0_p",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     0,
#    "xmax":     100,
#    "ymin":     0,
#    "ymax":     2000,
#    "xtitle":   "p(leading lepton) (GeV)",
#    "ytitle":   "Events",
#}
#
#hists["lep1_p"] = {
#    "output":   "lep1_p",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     0,
#    "xmax":     100,
#    "ymin":     0,
#    "ymax":     2000,
#    "xtitle":   "p(subleading lepton) (GeV)",
#    "ytitle":   "Events",
#}
#
#hists["lep0_pt"] = {
#    "output":   "lep0_pt",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     0,
#    "xmax":     70,
#    "ymin":     0,
#    "ymax":     300,
#    "xtitle":   "p_{T}(leading lepton) (GeV)",
#    "ytitle":   "Events",
#}
#
#hists["lep1_pt"] = {
#    "output":   "lep1_pt",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     0,
#    "xmax":     70,
#    "ymin":     0,
#    "ymax":     300,
#    "xtitle":   "p_{T}(subleading lepton) (GeV)",
#    "ytitle":   "Events",
#}
#
#hists["lep0_eta"] = {
#    "output":   "lep0_eta",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     -3,
#    "xmax":     3,
#    "ymin":     0,
#    "ymax":     60,
#    "xtitle":   "#eta(leading lepton)",
#    "ytitle":   "Events",
#}
#
#hists["lep1_eta"] = {
#    "output":   "lep1_eta",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     -3,
#    "xmax":     3,
#    "ymin":     0,
#    "ymax":     60,
#    "xtitle":   "#eta(subleading lepton)",
#    "ytitle":   "Events",
#}
#
#hists["lep0_phi"] = {
#    "output":   "lep0_phi",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     -5,
#    "xmax":     5,
#    "ymin":     0,
#    "ymax":     60,
#    "xtitle":   "#phi(leading lepton) (rad)",
#    "ytitle":   "Events",
#}
#
#hists["lep1_phi"] = {
#    "output":   "lep1_phi",
#    "logy":     False,
#    "stack":    True,
#    "rebin":    5,
#    "xmin":     -5,
#    "xmax":     5,
#    "ymin":     0,
#    "ymax":     60,
#    "xtitle":   "#phi(subleading lepton) (rad)",
#    "ytitle":   "Events",
#}
#