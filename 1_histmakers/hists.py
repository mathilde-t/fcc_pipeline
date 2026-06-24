'''
run with : fccanalysis run 1_histmakers/hists.py
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

inputDir = "./localSamples/diy"
outputDir = "./output/histmaker"

# optional: ncpus, default is 4, -1 uses all cores available
nCPUS       = -1

# Link to the dictonary that contains all the cross section informations etc... (mandatory)
procDict = "jsons/dummy.json"

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

pt_cut = 0

def build_electrons(df):
    df = df.Alias('Ele_Idx', 'Electron_objIdx.index')
    df = df.Define("ele_all",
        "FCCAnalyses::ReconstructedParticle::get(Ele_Idx, ReconstructedParticles)")
    df = df.Define("ele_pcut",
        "FCCAnalyses::ReconstructedParticle::sel_p(0)(ele_all)")
    return df

def build_muons(df):
    df = df.Alias('Muon_Idx', 'Muon_objIdx.index')
    df = df.Define("mu_all",
        "FCCAnalyses::ReconstructedParticle::get(Muon_Idx, ReconstructedParticles)")
    df = df.Define("mu_pcut",
        "FCCAnalyses::ReconstructedParticle::sel_p(0)(mu_all)")
    return df

# build_graph function that contains the analysis logic, cuts and histograms (mandatory)
    

def run_channel(df, lep_col):

    df = df.Define(
        "dilepton_result",
        f"fcc_pipeline::DYfunction::build_dilepton()({lep_col})"
    )

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
    
    return df


def build_graph(df, dataset):

    df = build_electrons(df)
    df = build_muons(df)

    if dataset == "ee_ee_ecm91_delphes":
        return run_channel(df, "ele_pcut")

    elif dataset == "ee_mumu_ecm91_delphes":
        return run_channel(df, "mu_pcut")

    elif dataset == "ee_ll_ecm91_delphes":
        df_e = run_channel(df, "ele_pcut")
        df_m = run_channel(df, "mu_pcut")
        return df_e + df_m

    
    results = []
    
    results.append(df.Histo1D(("dilepton_m","",*bins_m), "dilepton_m"))
    results.append(df.Histo1D(("dilepton_p","",*bins_p), "dilepton_p"))
    results.append(df.Histo1D(("lep0_p","",*bins_p), "lep0_p"))
    results.append(df.Histo1D(("lep1_p","",*bins_p), "lep1_p"))
    results.append(df.Histo1D(("lep0_eta","",*bins_eta), "lep0_eta"))
    results.append(df.Histo1D(("lep1_eta","",*bins_eta), "lep1_eta"))
    results.append(df.Histo1D(("lep0_phi","",*bins_phi), "lep0_phi"))
    results.append(df.Histo1D(("lep1_phi","",*bins_phi), "lep1_phi"))
    results.append(df.Histo1D(("lep0_pt","",*bins_p), "lep0_pt"))
    results.append(df.Histo1D(("lep1_pt","",*bins_p), "lep1_pt"))
    

    weightsum = df.Count()

    return results, weightsum