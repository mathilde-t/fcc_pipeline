import os

from scripts.config import get_config
from scripts.hist_config import BINNING
from utils_cli.path_utils import make_norm_dir_name
from utils_cli.analysis_utils import *

cfg_name = os.environ["FCC_PIPELINE_CONFIG"]
cfg = get_config(cfg_name)

normalisationTag = cfg.lumi_scaling["normalisation"]
inputDir = os.path.join(
        "./localSamples/",
        cfg.inputDir
    )
print(f"[INFO] histmaker inputDir: {inputDir}")

outputDir = os.path.join(
        "./output/histmaker/",
        cfg.outputDir if not normalisationTag else make_norm_dir_name(cfg.outputDir),
        cfg_name
    )
print(f"[INFO] histmaker outputDir: {outputDir}")

procDict = cfg.procDict
processList = cfg.processList
sample_type = cfg.sample_type
intLumi = cfg.lumi_scaling["intLumi"]
n_generated = cfg.lumi_scaling["n_generated"]
gen_or_reco = cfg.plotting["gen_or_reco"]

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


### Helper functions ###
# Helper function to choose if the weight application is done on the fly (local samples) or performed by the FCC FW (central samples)
def weight_application(df, dataset):
    if sample_type == "local" and normalisationTag:
        xs = processList[dataset]["crossSection"]
        weight = xs * intLumi / n_generated
        return df.Define("weight", f"{weight}")
    return df.Define("weight", "1.0")

# Helper functions to build the lepton collection, apply the p-cut and build the dilepton system
# now in utils

# Helper function to build the histograms and write to file
OBSERVABLES = [
    ("dilepton_m", "m"),
    ("dilepton_p", "p"),
    ("lep0_p", "p"),
    ("lep1_p", "p"),
    ("lep0_eta", "eta"),
    ("lep1_eta", "eta"),
    ("lep0_phi", "phi"),
    ("lep1_phi", "phi"),
    ("lep0_pt", "p"),
    ("lep1_pt", "p"),
    ("n_lep", "n"),
    ("lep_all_pt", "p"),
    ("px__wo__n_lep_cut", "p_sym"),
    ("py__wo__n_lep_cut", "p_sym"),
    ("pz__wo__n_lep_cut", "p_sym"),
]

def build_histograms(df_lep, lep, results):
    for variable, binning in OBSERVABLES:
        results.append(df_lep.Histo1D((f"{lep}_{variable}", "", *BINNING[binning]), f"{lep}_{variable}", "weight"))
    return results

# Helper function to write the histogram statistics to a text file
def write_histogram_stats(df_lep, lep, dataset, results, outputDir, lep_list):
    ### stats info printout
    h_unweighted_dilepton_m = df_lep.Histo1D( 
                                (f"{lep}_dilepton_m_unw", "", *BINNING["m"]), 
                                    f"{lep}_dilepton_m" ) 
        
    h_weighted_dilepton_m = df_lep.Histo1D( 
                                    (f"{lep}_dilepton_m_w", "", *BINNING["m"]), 
                                    f"{lep}_dilepton_m", "weight" )
            
    if lep == lep_list[-1]: # Only write stats for the last lepton in the list to avoid duplicate and unfinished entries
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



### Main code execution ###

# Create an empty stats file at the beginning of the run
os.makedirs(outputDir, exist_ok=True)
with open(os.path.join(outputDir, "histogram_stats.txt"), "w") as f:
    f.write(f"outputDir: {outputDir}\n\n")

# build_graph function that contains the analysis logic, cuts and histograms (mandatory)
def build_graph(df, dataset):

    results = []

    df = weight_application(df, dataset)
    weightsum = df.Sum("weight")

    for lep in lep_list:

        df_lep = df
        
        if gen_or_reco == "reco":
            df_lep = prepare_reco_collection(df_lep, lep, sample_type, pt_cut=0, n_lep_cut=2)
        elif gen_or_reco == "gen":
            df_lep = prepare_gen_collection(df_lep, lep, sample_type, pt_cut=0, n_lep_cut=2)
        else:
            raise ValueError(f"Unknown gen_or_reco value: {gen_or_reco}")
        
        particle_collection = "ReconstructedParticle" if gen_or_reco == "reco" else "MCParticle"
        cpp_type = "ReconstructedParticleData" if gen_or_reco == "reco" else "MCParticleData"
        Vec_rp = f"ROOT::VecOps::RVec<edm4hep::{cpp_type}>"

        df_lep = build_dilepton(df_lep, lep)
        df_lep = define_dilepton_observables(df_lep, lep, particle_collection, Vec_rp)
        df_lep = define_lepton_observables(df_lep, lep, particle_collection)

        results = build_histograms(df_lep, lep, results)
        write_histogram_stats(df_lep, lep, dataset, results, outputDir, lep_list)

    return results, weightsum