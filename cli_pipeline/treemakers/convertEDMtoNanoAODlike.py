'''
run with : fccanalysis run treemakers/convertEDMtoNanoAODlike.py (called treemakers/tree.py in docs)
'''

from scripts.lep_list import LEP_LIST
from utils_cli.analysis_utils import *

processList = {
    "__DATASET__": {"fraction": 1.0, "crossSection": __XSEC__,},
}

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
#__PRODTAG__

#Optional: output directory, default is local running directory
inputDir = "__INPUTDIR__"
outputDir = "__OUTPUTDIR__"

includePaths = ["functions.h"]

nCPUS = -1
compGroup = "group_u_FCC.local_gen"
outputDirEos = "/eos/user/m/mwitt/"
eosType = "eospublic"


class RDFanalysis:

    def analysers(df):
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

        for lep in LEP_LIST:

            # Define aliases and collections for gen and reco-levels specifically
            if GENORRECO == "reco":
                df = prepare_reco_collection(df, lep, SAMPLETYPE, pt_cut=0, n_lep_cut=0)
            elif GENORRECO == "gen":
                df = prepare_gen_collection(df, lep, SAMPLETYPE, pt_cut=0, n_lep_cut=0)
            else:
                raise ValueError(f"Unknown GENORRECO value: {GENORRECO}")
            
            particle_collection = "ReconstructedParticle" if GENORRECO == "reco" else "MCParticle"
            cpp_type = "ReconstructedParticleData" if GENORRECO == "reco" else "MCParticleData"
            Vec_rp = f"ROOT::VecOps::RVec<edm4hep::{cpp_type}>"

            df = define_lepton_observables(df, lep, particle_collection, GENORRECO)
                
            df = build_dilepton(df, lep)
            df = select_dilepton_events(df, lep)

            if lep == LEP_LIST[-1]:
                df = df.Define(f"valid_obj", "Muon_dilepton_result.size() == 3 || Electron_dilepton_result.size() == 3")
        
        df = df.Filter(
            "Electron_pass_selection || Muon_pass_selection",
            "Pass dilepton selection"
        )

        for lep in LEP_LIST:
            df = define_dilepton_observables(df, lep, particle_collection, Vec_rp)
            df = categorisation_separate_inclusive_sets(df, lep)
        
        return df  

# save output as flat nTuple
    def output():

        variables = [
            "n_lep",

            "lep0_pdgs",
            "lep1_pdgs",
            "lep0_eta",
            "lep1_eta",
            "lep0_phi",
            "lep1_phi",
            "lep0_p",
            "lep1_p",
            "lep0_pt",
            "lep1_pt",
            "lep0_px",
            "lep1_px",
            "lep0_py",
            "lep1_py",
            "lep0_pz",
            "lep1_pz",
            "lep0_charge",
            "lep1_charge",
            "lep0_theta",
            "lep1_theta",

            "pass_selection",

            "dilepton_m",
            "dilepton_p",
            "lep0_p_after_dilep",
            "lep1_p_after_dilep",
            "lep0_charge_after_dilep",
            "lep1_charge_after_dilep",
            
            "lep0_costheta",
            "lep1_costheta",
            "event_category",
        ]

        branchList = ["weight", "valid_obj",]
 
        for lep in LEP_LIST:
            branchList.extend(
                f"{lep}_{var}" for var in variables
            )

        return branchList