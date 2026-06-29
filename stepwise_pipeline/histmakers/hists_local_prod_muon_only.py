'''
run with : fccanalysis run histmakers/hists_local_prod_muon_only.py
'''

from scripts.config import get_config
from scripts.hist_config import BINNING

cfg = get_config("local_prod_muon_only")

inputDir = cfg.inputDir
outputDir = cfg.outputDir
procDict = cfg.procDict
processList = cfg.processList


# optional: ncpus, default is 4, -1 uses all cores available
nCPUS       = -1

# additional/custom C++ functions, defined in header files (optional)
includePaths = ["functions.h"]

# scale the histograms with the cross-section and integrated luminosity
doScale = False
intLumi = 5000000 # 5 /ab


# build_graph function that contains the analysis logic, cuts and histograms (mandatory)
def build_graph(df, dataset):

    results = []
    df = df.Define("weight", "1.0")
    weightsum = df.Sum("weight")
    
    # --- get all muons from the collection ---

    # define some aliases to be used later on
    df = df.Alias('Muon_Idx', 'Muon_objIdx.index')
    
    # get all the leptons from the collection
    df = df.Define("muon_all","FCCAnalyses::ReconstructedParticle::get(Muon_Idx, ReconstructedParticles)")
    
    # select leptons with momentum > 20 GeV
    df = df.Define("muon_pcut", "FCCAnalyses::ReconstructedParticle::sel_p(20)(muon_all)")
    
    # get muon properties
    df = df.Define("muon_p","FCCAnalyses::ReconstructedParticle::get_p(muon_pcut)")
    df = df.Define("muon_pt","FCCAnalyses::ReconstructedParticle::get_pt(muon_pcut)")
    df = df.Define("muon_eta","FCCAnalyses::ReconstructedParticle::get_eta(muon_pcut)")
    df = df.Define("muon_phi","FCCAnalyses::ReconstructedParticle::get_phi(muon_pcut)")
    
    df = df.Filter("muon_pcut.size() >= 2")
    
    # baseline histograms, before any selection cuts (store with _cut0)
    results.append(df.Histo1D(("muon_p", "", *BINNING["p"]), "muon_p"))
    results.append(df.Histo1D(("muon_pt", "", *BINNING["p"]), "muon_pt"))
    results.append(df.Histo1D(("muon_eta", "", *BINNING["eta"]), "muon_eta"))
    results.append(df.Histo1D(("muon_phi", "", *BINNING["phi"]), "muon_phi"))


    weightsum = df.Count()

    return results, weightsum