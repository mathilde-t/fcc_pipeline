'''
run with : fccanalysis run treemakers/convertEDMtoNanoAODlike.py (called treemakers/tree.py in docs)
'''

from utils_cli.analysis_utils import *

processList = {
    "__DATASET__": {"fraction": 1.0, "crossSection": __XSEC__,},
}

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
__PRODTAG__

#Optional: output directory, default is local running directory
inputDir = "__INPUTDIR__"
outputDir = "__OUTPUTDIR__"


includePaths = ["functions.h", "namespace_particle.h"]

nCPUS = 4
compGroup = "group_u_FCC.local_gen"
outputDirEos = "/eos/user/m/mwitt/"
eosType = "eospublic"


class RDFanalysis:

    def analysers(df):
        LEPTON = "__LEPTON__"
        print("LEPTON LEPTON LEPTON:", LEPTON)

        SAMPLETYPE = "__SAMPLETYPE__"
        NORMALISATIONTAG = __NORMALISATIONTAG__
        GENORRECO = "__GENORRECO__"

        if NORMALISATIONTAG:
            df = df.Define(
                "weight",
                "(double)__XSEC__ * (double)__INTLUMI__ / (double)__NGENERATED__"
            )
        else:
            df = df.Define("weight", "1.0")

        # Define aliases and collections for gen and reco-levels specifically
        if GENORRECO == "reco":
            df = prepare_reco_collection(df, LEPTON, SAMPLETYPE, pt_cut=0, n_lep_cut=2, prefix="")
        elif GENORRECO == "gen":
            df = prepare_gen_collection(df, LEPTON, SAMPLETYPE, pt_cut=0, n_lep_cut=2, prefix="")
        else:
            raise ValueError(f"Unknown GENORRECO value: {GENORRECO}")
        
        particle_collection = "ReconstructedParticle" if GENORRECO == "reco" else "MCParticle"
        cpp_type = "ReconstructedParticleData" if GENORRECO == "reco" else "MCParticleData"
        Vec_rp = f"ROOT::VecOps::RVec<edm4hep::{cpp_type}>"

        df = build_dilepton(df, LEPTON, prefix="")
        df = define_dilepton_observables(df, LEPTON, particle_collection, Vec_rp, prefix="")
        df = define_lepton_observables(df, LEPTON, particle_collection, prefix="")
        
        return df  

# save output as flat nTuple
    def output():

        branchList = [
            "dilepton_m",
            "dilepton_p",
            "lep0_p",
            "lep1_p",
            "lep0_eta", 
            "lep1_eta", 
            "lep0_phi", 
            "lep1_phi", 
            "lep0_pt",
            "lep1_pt",
            "weight",
            "n_lep",
            "lep_all_pt",
            "px__wo__n_lep_cut",
            "py__wo__n_lep_cut",
            "pz__wo__n_lep_cut"
        ]

        branchList = ["weight"]
        return branchList