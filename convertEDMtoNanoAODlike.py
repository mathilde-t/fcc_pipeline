'''
run with : fccanalysis run convertEDMtoNanoAODlike.py (called tree.py in docs)
'''

processList = {
    "__DATASET__": {"fraction": 1.0, "crossSection": __XSEC__,},
}

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
#prodTag     = "FCCee/winter2023/IDEA/"

#Optional: output directory, default is local running directory
outputDir = "./output/convertEDMtoNanoAODlike"
inputDir = "./localSamples/IDEA_FullSilicon/p8_ee_Zll_ecm240"
# inputDir = "./localSamples/diy"

includePaths = ["functions.h"]

nCPUS = 4
compGroup = "group_u_FCC.local_gen"
outputDirEos = "/eos/user/m/mwitt/"
eosType = "eospublic"


class RDFanalysis:

    def analysers(df):
        LEPTON = "__LEPTON__"
        print("LEPTON LEPTON LEPTON:", LEPTON)
        
        df = df.Alias(f"{LEPTON}_Idx", f"{LEPTON}_objIdx.index")

        # print(sorted([str(c) for c in df.GetColumnNames() if "objIdx" in str(c)]))

        df = df.Define("lep_all", f"FCCAnalyses::ReconstructedParticle::get({LEPTON}_Idx, ReconstructedParticles)")
        df = df.Define("lep_pcut", "FCCAnalyses::ReconstructedParticle::sel_p(0)(lep_all)")


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

        return df  


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
        ]

        return branchList