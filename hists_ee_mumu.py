'''
run with : fccanalysis run hists.py
'''

# list of processes
processList = {
    # gen level
    # "ee_ee_ecm91": {"fraction": 1.0, "crossSection": 4487.6,},
    # "ee_mumu_ecm91": {"fraction": 1.0, "crossSection": 2024.7,},
    # "ee_tautau_ecm91": {"fraction": 1.0,"crossSection": 2020.4,},
    # "ee_ll_ecm91": {"fraction": 1.0, "crossSection": 8533.7,},

    # reco level
    "ee_ee_ecm91_delphes": {"fraction": 1.0, "crossSection": 2020.4,},
    "ee_mumu_ecm91_delphes": {"fraction": 1.0, "crossSection": 2024.7,},
    #"ee_tautau_ecm91_delphes": {"fraction": 1.0,"crossSection": 2024.7,},
    #"ee_ll_ecm91_delphes": {"fraction": 1.0, "crossSection": 8533.7,},
}

inputDir = "./localSamples"
outputDir = "./output/histmaker"

# optional: ncpus, default is 4, -1 uses all cores available
nCPUS       = -1

# Link to the dictonary that contains all the cross section informations etc... (mandatory)
procDict = "dummy.json"

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
    
    lepton_map = {
        "ee_ee_ecm91_delphes": "Electron",
        "ee_mumu_ecm91_delphes": "Muon",
        #"ee_tautau_ecm91_delphes": "Tau",
        #"ee_ll_ecm91_delphes": "Lepton"
    }
    lep = lepton_map[dataset]

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

    results.append(df.Histo1D(("dilepton_m", "", *bins_m), "dilepton_m"))
    results.append(df.Histo1D(("dilepton_p", "", *bins_p), "dilepton_p"))
    results.append(df.Histo1D(("lep0_p", "", *bins_p), "lep0_p"))
    results.append(df.Histo1D(("lep1_p", "", *bins_p), "lep1_p"))
    results.append(df.Histo1D(("lep0_eta", "", *bins_eta), "lep0_eta"))
    results.append(df.Histo1D(("lep1_eta", "", *bins_eta), "lep1_eta"))
    results.append(df.Histo1D(("lep0_phi", "", *bins_phi), "lep0_phi"))
    results.append(df.Histo1D(("lep1_phi", "", *bins_phi), "lep1_phi"))
    results.append(df.Histo1D(("lep0_pt", "", *bins_p), "lep0_pt"))
    results.append(df.Histo1D(("lep1_pt", "", *bins_p), "lep1_pt"))

    weightsum = df.Count()

    return results, weightsum