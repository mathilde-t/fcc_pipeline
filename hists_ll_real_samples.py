'''
run with : fccanalysis run hists_ll_real_samples.py
'''

# list of processes
processList = {
     # reco level
    "events_003635753": {"fraction": 1.0, "crossSection": 1,},
    "events_007405803": {"fraction": 1.0, "crossSection": 1,},
    "events_009996087": {"fraction": 1.0, "crossSection": 1,},
}

processList = {
     # reco level
    "events_003136187": {"fraction": 1.0, "crossSection": 1,},
    "events_006869229": {"fraction": 1.0, "crossSection": 1,},
}

processList = {
    "ee_events_193158988": {"fraction": 1.0, "crossSection": 1,},
    "ee_events_194455359": {"fraction": 1.0, "crossSection": 1,},
    "mumu_events_196687800": {"fraction": 1.0, "crossSection": 1,},
    "mumu_events_197347757": {"fraction": 1.0, "crossSection": 1,},
}

inputDir = "./localSamples/IDEA_FullSilicon/p8_ee_Zll_ecm240"
outputDir = "./output/histmaker/real_samples"

inputDir = "./localSamples/wi23_idea_si"
outputDir = "./output/histmaker/wi23_idea_si"

inputDir = "./localSamples/wi23_idea_wzp6"
outputDir = "./output/histmaker/wi23_idea_wzp6"

# optional: ncpus, default is 4, -1 uses all cores available
nCPUS       = -1

# Link to the dictonary that contains all the cross section informations etc... (mandatory)
procDict = "dummy_real_samples.json"
procDict = "dummy_wi23.json"
procDict = "dummy_wi23_idea_wzp6.json"

# additional/custom C++ functions, defined in header files (optional)
includePaths = ["functions.h"]

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
#prodTag     = "FCCee/winter2023/IDEA/"


# scale the histograms with the cross-section and integrated luminosity
doScale = False
intLumi = 5000000 # 5 /ab

# define some binning for various histograms

bins_p = (200, 0, 100)
bins_m = (150, 0, 100)
bins_eta = (600, -3, 3)
bins_phi = (500, -5, 5)

bins_count = (50, 0, 50)
bins_charge = (10, -5, 5)
bins_iso = (500, 0, 5)

# build_graph function that contains the analysis logic, cuts and histograms (mandatory)
def build_graph(df, dataset):

    results = []
    df = df.Define("weight", "1.0")
    weightsum = df.Sum("weight")
    
    # lepton_map = {
    #     "ee_ee_ecm91_delphes": "Electron",
    #     "ee_mumu_ecm91_delphes": "Muon",
    #     #"ee_tautau_ecm91_delphes": "Tau",
    #     #"ee_ll_ecm91_delphes": "Lepton"
    # }
    # lep = lepton_map[dataset]

    for lep in ["Electron", "Muon"]:

        df_lep = df

        # collection aliases
        df_lep = df_lep.Alias(f"{lep}_Idx", f"{lep}#0.index")
        
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

        results.append(df_lep.Histo1D((f"{lep}_dilepton_m", "", *bins_m), f"{lep}_dilepton_m"))
        results.append(df_lep.Histo1D((f"{lep}_dilepton_p", "", *bins_p), f"{lep}_dilepton_p"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_p", "", *bins_p), f"{lep}_lep0_p"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_p", "", *bins_p), f"{lep}_lep1_p"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_eta", "", *bins_eta), f"{lep}_lep0_eta"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_eta", "", *bins_eta), f"{lep}_lep1_eta"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_phi", "", *bins_phi), f"{lep}_lep0_phi"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_phi", "", *bins_phi), f"{lep}_lep1_phi"))
        results.append(df_lep.Histo1D((f"{lep}_lep0_pt", "", *bins_p), f"{lep}_lep0_pt"))
        results.append(df_lep.Histo1D((f"{lep}_lep1_pt", "", *bins_p), f"{lep}_lep1_pt"))

        weightsum = df.Count()

    return results, weightsum