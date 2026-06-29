import os

from scripts.config import get_config
from scripts.hist_config import BINNING

cfg_name = os.environ["FCC_PIPELINE_CONFIG"]
cfg = get_config(cfg_name)

### debug
# print("CONFIG name : ", cfg_name)
# print("CONFIG name : ", cfg)
#print("[DEBUG] cwd:", os.getcwd())
#print("[DEBUG] FCC_PIPELINE_CONFIG:", os.environ.get("FCC_PIPELINE_CONFIG"))
#print("[DEBUG] outputDir:", cfg.outputDir)
#print("[DEBUG] inputDir:", cfg.inputDir)

inputDir = cfg.inputDir
outputDir = cfg.outputDir
procDict = cfg.procDict
processList = cfg.processList
sample_type = cfg.sample_type

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
#if cfg.prodTag is not None: #here1
#    prodTag = cfg.prodTag

# if the datasets have diverse final states (e.g. ee+mumu, not only ee) the build_graph needs to loop over the final states
lep_list = sorted({info["lep"] for info in processList.values()})


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
    df = df.Define("weight", "1.0") #here1 put something else when scaling MC later.
    weightsum = df.Sum("weight")
    
    for lep in lep_list:

        df_lep = df

        # collection aliases, differen to local and central plots
        if sample_type == "central":
            df_lep = df_lep.Alias(f"{lep}_Idx", f"{lep}#0.index") #here1 central
        elif sample_type == "local":
            df_lep = df_lep.Alias(f"{lep}_Idx", f"{lep}_objIdx.index") #here1 local
        else:
            raise ValueError(f"Unknown sample type: {sample_type}")

        
        df_lep = df_lep.Define(f"{lep}_lep_all", f"FCCAnalyses::ReconstructedParticle::get({lep}_Idx, ReconstructedParticles)")
        df_lep = df_lep.Define(f"{lep}_lep_pcut", f"FCCAnalyses::ReconstructedParticle::sel_p(0)({lep}_lep_all)")


        # --- make code general for all leptons (electrons, muons, taus) ---

        # build in functions    
        df_lep = df_lep.Define(f"{lep}_dilepton_result", f"fcc_pipeline::DYfunction::build_dilepton()({lep}_lep_pcut)")
        
        # define dilepton properties
        df_lep = df_lep.Define(f"{lep}_dilepton", f"Vec_rp{{{lep}_dilepton_result[0]}}")
        df_lep = df_lep.Define(f"{lep}_dilepton_m", f"FCCAnalyses::ReconstructedParticle::get_mass({lep}_dilepton)[0]")
        df_lep = df_lep.Define(f"{lep}_dilepton_p", f"FCCAnalyses::ReconstructedParticle::get_p({lep}_dilepton)[0]")

        # define the two leptons that form the dilepton system
        df_lep = df_lep.Define(f"{lep}_dilepton_leps", f"Vec_rp{{{lep}_dilepton_result[1], {lep}_dilepton_result[2]}}")
        df_lep = df_lep.Define(f"{lep}_lep_p", f"FCCAnalyses::ReconstructedParticle::get_p({lep}_dilepton_leps)")
        df_lep = df_lep.Define(f"{lep}_lep0_p", f"{lep}_lep_p[0]")
        df_lep = df_lep.Define(f"{lep}_lep1_p", f"{lep}_lep_p[1]")

        df_lep = df_lep.Define(f"{lep}_lep0_eta", f"FCCAnalyses::ReconstructedParticle::get_eta({lep}_dilepton_leps)[0]")
        df_lep = df_lep.Define(f"{lep}_lep1_eta", f"FCCAnalyses::ReconstructedParticle::get_eta({lep}_dilepton_leps)[1]")

        df_lep = df_lep.Define(f"{lep}_lep0_phi", f"FCCAnalyses::ReconstructedParticle::get_phi({lep}_dilepton_leps)[0]")
        df_lep = df_lep.Define(f"{lep}_lep1_phi", f"FCCAnalyses::ReconstructedParticle::get_phi({lep}_dilepton_leps)[1]")

        df_lep = df_lep.Define(f"{lep}_lep0_pt", f"FCCAnalyses::ReconstructedParticle::get_pt({lep}_dilepton_leps)[0]")
        df_lep = df_lep.Define(f"{lep}_lep1_pt", f"FCCAnalyses::ReconstructedParticle::get_pt({lep}_dilepton_leps)[1]")
        
        df_lep = df_lep.Filter(f"{lep}_lep_pcut.size() >= 2")

        results.append(df_lep.Histo1D((f"{lep}_dilepton_m", "", *BINNING["m"]), f"{lep}_dilepton_m"))
        results.append(df_lep.Histo1D((f"{lep}_dilepton_p", "", *BINNING["p"]), f"{lep}_dilepton_p"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_p", "", *BINNING["p"]), f"{lep}_lep0_p"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_p", "", *BINNING["p"]), f"{lep}_lep1_p"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_eta", "", *BINNING["eta"]), f"{lep}_lep0_eta"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_eta", "", *BINNING["eta"]), f"{lep}_lep1_eta"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_phi", "", *BINNING["phi"]), f"{lep}_lep0_phi"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_phi", "", *BINNING["phi"]), f"{lep}_lep1_phi"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_pt", "", *BINNING["p"]), f"{lep}_lep0_pt"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_pt", "", *BINNING["p"]), f"{lep}_lep1_pt"))

    return results, weightsum