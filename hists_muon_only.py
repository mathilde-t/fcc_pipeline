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
    #"ee_ee_ecm91_delphes": {"fraction": 1.0, "crossSection": 2020.4,},
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
    results.append(df.Histo1D(("muon_p", "", *bins_p), "muon_p"))
    results.append(df.Histo1D(("muon_pt", "", *bins_p), "muon_pt"))
    results.append(df.Histo1D(("muon_eta", "", *bins_eta), "muon_eta"))
    results.append(df.Histo1D(("muon_phi", "", *bins_phi), "muon_phi"))


    weightsum = df.Count()

    return results, weightsum