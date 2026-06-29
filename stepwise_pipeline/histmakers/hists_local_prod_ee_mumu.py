'''
run with : fccanalysis run histmakers/hists_local_prod_ee_mumu.py
'''

from scripts.config import get_config
from scripts.hist_config import BINNING

cfg = get_config("local_prod_ee_mumu")

inputDir = cfg.inputDir
outputDir = cfg.outputDir
procDict = cfg.procDict
processList = cfg.processList

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
if cfg.prodTag is not None:
    prodTag = cfg.prodTag

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
    
    lep = cfg.processList[dataset]["lep"]

    df = df.Alias(f"{lep}_Idx", f"{lep}_objIdx.index")
    
    df = df.Define("lep_all", f"FCCAnalyses::ReconstructedParticle::get({lep}_Idx, ReconstructedParticles)")
    df = df.Define("lep_pcut", "FCCAnalyses::ReconstructedParticle::sel_p(0)(lep_all)")


    # --- make code general for all leptons (electrons, muons, taus) ---

    # build in functions    
    df = df.Define("dilepton_result", "fcc_pipeline::DYfunction::build_dilepton()(lep_pcut)")
    
    # define dilepton properties
    df = df.Define("dilepton", "Vec_rp{dilepton_result[0]}")
    df = df.Define("dilepton_m", "FCCAnalyses::ReconstructedParticle::get_mass(dilepton)[0]")
    df = df.Define("dilepton_p", "FCCAnalyses::ReconstructedParticle::get_p(dilepton)[0]")

    # define the two leptons that form the dilepton system
    df = df.Define("dilepton_leps", "Vec_rp{dilepton_result[1], dilepton_result[2]}")
    df = df.Define("lep_p", "FCCAnalyses::ReconstructedParticle::get_p(dilepton_leps)")
    df = df.Define("lep0_p", "lep_p[0]")
    df = df.Define("lep1_p", "lep_p[1]")

    df = df.Define("lep0_eta", "FCCAnalyses::ReconstructedParticle::get_eta(dilepton_leps)[0]")
    df = df.Define("lep1_eta", "FCCAnalyses::ReconstructedParticle::get_eta(dilepton_leps)[1]")

    df = df.Define("lep0_phi", "FCCAnalyses::ReconstructedParticle::get_phi(dilepton_leps)[0]")
    df = df.Define("lep1_phi", "FCCAnalyses::ReconstructedParticle::get_phi(dilepton_leps)[1]")

    df = df.Define("lep0_pt", "FCCAnalyses::ReconstructedParticle::get_pt(dilepton_leps)[0]")
    df = df.Define("lep1_pt", "FCCAnalyses::ReconstructedParticle::get_pt(dilepton_leps)[1]")
    
    df = df.Filter("lep_pcut.size() >= 2")

    results.append(df.Histo1D(("dilepton_m", "", *BINNING["m"]), "dilepton_m"))
    results.append(df.Histo1D(("dilepton_p", "", *BINNING["p"]), "dilepton_p"))
    results.append(df.Histo1D(("lep0_p", "", *BINNING["p"]), "lep0_p"))
    results.append(df.Histo1D(("lep1_p", "", *BINNING["p"]), "lep1_p"))
    results.append(df.Histo1D(("lep0_eta", "", *BINNING["eta"]), "lep0_eta"))
    results.append(df.Histo1D(("lep1_eta", "", *BINNING["eta"]), "lep1_eta"))
    results.append(df.Histo1D(("lep0_phi", "", *BINNING["phi"]), "lep0_phi"))
    results.append(df.Histo1D(("lep1_phi", "", *BINNING["phi"]), "lep1_phi"))
    results.append(df.Histo1D(("lep0_pt", "", *BINNING["p"]), "lep0_pt"))
    results.append(df.Histo1D(("lep1_pt", "", *BINNING["p"]), "lep1_pt"))

    weightsum = df.Count()

    return results, weightsum