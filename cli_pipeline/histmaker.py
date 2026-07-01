import os

from scripts.config import get_config
from scripts.hist_config import BINNING
from utils_cli.path_utils import make_norm_dir_name

cfg_name = os.environ["FCC_PIPELINE_CONFIG"]
cfg = get_config(cfg_name)

inputDir = cfg.inputDir
outputDir = cfg.outputDir
procDict = cfg.procDict
processList = cfg.processList
sample_type = cfg.sample_type
normalisationTag = cfg.lumi_scaling["normalisation"]
intLumi = cfg.lumi_scaling["intLumi"]
n_generated = cfg.lumi_scaling["n_generated"]

outputDir = make_norm_dir_name(outputDir) if normalisationTag else outputDir

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
#if cfg.prodTag is not None:
#    prodTag = cfg.prodTag

# if the datasets have diverse final states (e.g. ee+mumu, not only ee) the build_graph needs to loop over the final states
lep_list = sorted({info["lep"] for info in processList.values()})

# optional: ncpus, default is 4, -1 uses all cores available
nCPUS       = -1

# additional/custom C++ functions, defined in header files (optional)
includePaths = ["functions.h"]


# scale the histograms with the cross-section and integrated luminosity
# for centrally produced samples, normalise here because the FCC framework expects so,
# for locally produced samples, normalise while the histogram creation, as they are selfmade

doScale = (sample_type == "central" and normalisationTag)
if doScale:
    intLumi = intLumi

# Create an empty stats file at the beginning of the run
os.makedirs(outputDir, exist_ok=True)
with open(os.path.join(outputDir, "histogram_stats.txt"), "w") as f:
    f.write(f"outputDir: {outputDir}\n\n")

# build_graph function that contains the analysis logic, cuts and histograms (mandatory)
def build_graph(df, dataset):

    results = []
    event_weight = 1.0

    if sample_type == "local" and normalisationTag:
        xs = processList[dataset]["crossSection"]
        event_weight = xs * intLumi / n_generated
        weight = xs * intLumi / n_generated
        df = df.Define("weight", f"{weight}")
    else: df = df.Define("weight", "1.0")

    weightsum = df.Sum("weight")

    for lep in lep_list:

        df_lep = df

        # collection aliases, different to local and central plots
        if sample_type == "central":
            df_lep = df_lep.Alias(f"{lep}_Idx", f"{lep}#0.index") #here1 central
        elif sample_type == "local":
            df_lep = df_lep.Alias(f"{lep}_Idx", f"{lep}_objIdx.index") #here1 local
        else:
            raise ValueError(f"Unknown sample type: {sample_type}, indexing step")

        
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


        results.append(df_lep.Histo1D((f"{lep}_dilepton_m", "", *BINNING["m"]), f"{lep}_dilepton_m", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_dilepton_p", "", *BINNING["p"]), f"{lep}_dilepton_p", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_p", "", *BINNING["p"]), f"{lep}_lep0_p", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_p", "", *BINNING["p"]), f"{lep}_lep1_p", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_eta", "", *BINNING["eta"]), f"{lep}_lep0_eta", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_eta", "", *BINNING["eta"]), f"{lep}_lep1_eta", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_phi", "", *BINNING["phi"]), f"{lep}_lep0_phi", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_phi", "", *BINNING["phi"]), f"{lep}_lep1_phi", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_pt", "", *BINNING["p"]), f"{lep}_lep0_pt", "weight"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_pt", "", *BINNING["p"]), f"{lep}_lep1_pt", "weight"))

        ### stats info printout
        h_unweighted_dilepton_m = df_lep.Histo1D( 
                                    (f"{lep}_dilepton_m_unw", "", *BINNING["m"]), 
                                     f"{lep}_dilepton_m" ) 
            
        h_weighted_dilepton_m = df_lep.Histo1D( 
                                     (f"{lep}_dilepton_m_w", "", *BINNING["m"]), 
                                      f"{lep}_dilepton_m", "weight" )
              
        if lep in lep_list[-1]: # Only write stats for the last lepton in the list to avoid duplicate and unfinished entries
            with open(os.path.join(outputDir, "histogram_stats.txt"), "a") as f:
                f.write(f"=== Dataset: {dataset}, Lepton: {lep} ===\n\n")
        
                f.write("|" + "=" * 60 + "|\n")
                f.write("|" + f" Histogram (dilepton_m) {'Entries':>15}{'Integral':>15}" + f"{'|\n':>8}")
                f.write("|" + "-" * 60 + "|\n")
                #unweighted
                f.write(
                    "|" +
                    f"{' Unweighted':<20}"
                    f"{h_unweighted_dilepton_m.GetEntries():>15.0f}"
                    f"{h_unweighted_dilepton_m.Integral():>15.1f}" +
                    f"{'|\n':>12}"
                )
                #weighted
                f.write(
                    "|" +
                    f"{' Weighted':<20}"
                    f"{h_weighted_dilepton_m.GetEntries():>15.0f}"
                    f"{h_weighted_dilepton_m.Integral():>15.1f}" +
                    f"{'|\n':>12}"
                )
                f.write("|" + "=" * 60 + "|\n")
                f.write(
                        f"{'Note: unweighted: weight not applied, weighted: weight applied':<60}" + "\n"
                        f"{'      (n=1 for no normalisation, n≠1 for normalisation)':<60}"
                    )
        
                f.write("\n\n")
        
                f.write(f"--- Check integration for all histograms ---\n")
        
                f.write("|" + "=" * 75 + "|\n")
                f.write("|" + f"{' Histogram':<20}" f"{'Entries':>15}" f"{'Integral':>15}{'Average Weight':>19}" + f"{'|\n':>8}")
                f.write("|" + "-" * 75 + "|\n")
                for h in results:
                    entries = h.GetEntries()
                    integral = h.Integral()
                    average_weight = integral / entries if entries > 0 else 0.0
                    f.write(
                        "|" +
                        f"{ h.GetName():<20}"
                        f"{entries:>15.0f}"
                        f"{integral:>15.1f}"
                        f"{average_weight:>19.1f}" +
                        f"{'|\n':>8}"
                    )
                f.write("|" + "=" * 75 + "|\n")
        
                f.write("\n\n")

    return results, weightsum