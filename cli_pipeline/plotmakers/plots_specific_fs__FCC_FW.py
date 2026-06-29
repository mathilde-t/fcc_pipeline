'''
run with : fccanalysis plots plotmakers/plots_specific_fs__FCC_FW.py 
plot edm files with the framework
this plotter can only plot one final state particle. So if data contains ee and mumu,
in that order, it will plot the plots for mumu.
'''
import ROOT
import os
from scripts.config import get_config

cfg_name = os.environ["FCC_PIPELINE_CONFIG"]
cfg = get_config(cfg_name)
#cfg = get_config("local_prod_muon_only")

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
plotStatUnc = plot_meta["plotStatUnc"]
collider = 'FCC-ee'
formats = ['png','pdf']


## build plot layout automatically from processList
colors = {}
legend = {}
procs = {"signal": {}, "backgrounds": {}}

for proc, info in cfg.processList.items():
    
    c = resolve_color(info["plot"]["color"])
    colors[proc] = c
    legend[proc] = info["plot"]["legend"]

    ptype = info["plot"].get("type", "background")
    if ptype == "signal":
        procs["signal"][proc] = [proc]
    else:
        procs["backgrounds"][proc] = [proc]


## build the plots with the FCC framework
from scripts.plot_config import hists