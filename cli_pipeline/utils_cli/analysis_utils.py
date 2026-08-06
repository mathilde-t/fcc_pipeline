''' Helper functions to build the lepton collection, apply the p-cut and build the dilepton system'''

def prepare_reco_collection(df_lep, lep, sample_type, pt_cut=0, n_lep_cut=0, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix
    
    # collection aliases, different to local and central plots
    if sample_type == "central":
        df_lep = df_lep.Alias(f"{lep}_Idx", f"{lep}#0.index")
    elif sample_type == "local":
        df_lep = df_lep.Alias(f"{lep}_Idx", f"{lep}_objIdx.index")
    else:
        raise ValueError(f"Unknown sample type: {sample_type}, indexing step")

    df_lep = df_lep.Define(f"{prefix}lep_all", f"FCCAnalyses::ReconstructedParticle::get({lep}_Idx, ReconstructedParticles)")
    df_lep = df_lep.Define(f"{prefix}lep_pcut", f"FCCAnalyses::ReconstructedParticle::sel_pt({pt_cut})({prefix}lep_all)")
    df_lep = df_lep.Filter(f"{prefix}lep_pcut.size() >= {n_lep_cut}")
    df_lep = df_lep.Define(f"{prefix}n_lep", f"{prefix}lep_pcut.size()")

    return df_lep

PDG_IDS = {
    "Electron": 11,
    "Muon": 13,
    "Tau": 15,
}

def prepare_gen_collection(df, lep, sample_type, pt_cut=0, n_lep_cut=0, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix
    pdgid = PDG_IDS[lep]

    if sample_type == "local":
        df = df.Define(f"{prefix}lep_all", f"FCCAnalyses::MCParticle::sel_pdgID({pdgid}, true)(MCParticlesStable)")

    elif sample_type == "central":
        df = df.Define(f"{prefix}stable", "FCCAnalyses::MCParticle::sel_genStatus(1)(Particle)")
        df = df.Define(f"{prefix}lep_all", f"FCCAnalyses::MCParticle::sel_pdgID({pdgid}, true)({prefix}stable)")
    
    else:
        raise ValueError(f"sample type unknown : {sample_type}")

    df = df.Define(f"{prefix}lep_pcut", f"FCCAnalyses::MCParticle::sel_pt({pt_cut})({prefix}lep_all)")
    df = df.Define(f"{prefix}n_lep", f"{prefix}lep_pcut.size()")
    df = df.Filter(f"{prefix}n_lep >= {n_lep_cut}", f"require at least {n_lep_cut} {lep}s")

    return df


def define_lepton_observables(df_lep, lep, particle_collection, GENORRECO, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix

    if GENORRECO == "gen":
        df_lep = df_lep.Define(f"{prefix}lep0_pdgs", f"FCCAnalyses::{particle_collection}::get_pdg({prefix}lep_pcut)[0]")
        df_lep = df_lep.Define(f"{prefix}lep1_pdgs", f"FCCAnalyses::{particle_collection}::get_pdg({prefix}lep_pcut)[1]")
    else:
        df_lep = df_lep.Define(f"{prefix}lep0_pdgs", "-1")
        df_lep = df_lep.Define(f"{prefix}lep1_pdgs", "-1")
    
    df_lep = df_lep.Define(f"{prefix}lep0_eta", f"FCCAnalyses::{particle_collection}::get_eta({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_eta", f"FCCAnalyses::{particle_collection}::get_eta({prefix}lep_pcut)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_phi", f"FCCAnalyses::{particle_collection}::get_phi({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_phi", f"FCCAnalyses::{particle_collection}::get_phi({prefix}lep_pcut)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_p", f"FCCAnalyses::{particle_collection}::get_p({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_p", f"FCCAnalyses::{particle_collection}::get_p({prefix}lep_pcut)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_pt", f"FCCAnalyses::{particle_collection}::get_pt({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_pt", f"FCCAnalyses::{particle_collection}::get_pt({prefix}lep_pcut)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_px", f"FCCAnalyses::{particle_collection}::get_px({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_px", f"FCCAnalyses::{particle_collection}::get_px({prefix}lep_pcut)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_py", f"FCCAnalyses::{particle_collection}::get_py({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_py", f"FCCAnalyses::{particle_collection}::get_py({prefix}lep_pcut)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_pz", f"FCCAnalyses::{particle_collection}::get_pz({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_pz", f"FCCAnalyses::{particle_collection}::get_pz({prefix}lep_pcut)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_charge", f"FCCAnalyses::{particle_collection}::get_charge({prefix}lep_pcut)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_charge", f"FCCAnalyses::{particle_collection}::get_charge({prefix}lep_pcut)[1]")
    return df_lep


def build_dilepton(df_lep, lep, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix
    # build the dilepton system
    df_lep = df_lep.Define(f"{prefix}dilepton_result", f"fcc_pipeline::DYfunction::build_dilepton()({prefix}lep_pcut)")

    return df_lep


def select_dilepton_events(df_lep, lep, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix

    df_lep = df_lep.Define(
            f"{prefix}pass_selection",
            f"""
            {prefix}dilepton_result.size() == 3 &&
            {prefix}dilepton_result[1].charge * {prefix}dilepton_result[2].charge < 0 &&
            abs({prefix}dilepton_result[0].mass - 91.1876) < 15.
            """
    )

    return df_lep


def define_dilepton_observables(df_lep, lep, particle_collection, Vec_rp, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix

    # define dilepton properties
    df_lep = df_lep.Define(f"{prefix}dilepton", f"{Vec_rp}{{{prefix}dilepton_result[0]}}")
    df_lep = df_lep.Define(f"{prefix}dilepton_m", f"FCCAnalyses::{particle_collection}::get_mass({prefix}dilepton)[0]")
    df_lep = df_lep.Define(f"{prefix}dilepton_p", f"FCCAnalyses::{particle_collection}::get_p({prefix}dilepton)[0]")

    # define the two leptons that form the dilepton system
    df_lep = df_lep.Define(f"{prefix}dilepton_leps", f"{Vec_rp}{{{prefix}dilepton_result[1], {prefix}dilepton_result[2]}}")
    df_lep = df_lep.Define(f"{prefix}lep_p", f"{particle_collection}::get_p({prefix}dilepton_leps)")
    df_lep = df_lep.Define(f"{prefix}lep0_p_after_dilep", f"{prefix}lep_p[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_p_after_dilep", f"{prefix}lep_p[1]")

    df_lep = df_lep.Define(f"{prefix}lep0_charge_after_dilep", f"FCCAnalyses::{particle_collection}::get_charge({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_charge_after_dilep", f"FCCAnalyses::{particle_collection}::get_charge({prefix}dilepton_leps)[1]")
    
    return df_lep


def categorisation_separate_inclusive_sets(df_lep, lep, costheta_cut=0.8, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix

    df_lep = df_lep.Define(f"{prefix}lep0_costheta", f"{prefix}lep0_pz / {prefix}lep0_p")
    df_lep = df_lep.Define(f"{prefix}lep1_costheta", f"{prefix}lep1_pz / {prefix}lep1_p")

    if lep == "Electron":
        df_lep = df_lep.Define(
            f"{prefix}event_category",
            f"(abs({prefix}lep0_costheta)<{costheta_cut} && "
            f"abs({prefix}lep1_costheta)<{costheta_cut}) ? 1 : 0"
        )

    elif lep == "Muon":
        # all muons are s-channel-like
        df_lep = df_lep.Define(
            f"{prefix}event_category",
            "1"
        )

    return df_lep



def define_lepton_observables_from_dilepton_object(df_lep, lep, particle_collection, prefix=None):
    # this function serves as a cross check to the define_lepton_observables function, but uses the selected leptons from the dilepton object instead of the original lepton collection
    prefix = f"{lep}_" if prefix is None else prefix

    df_lep = df_lep.Define(f"{prefix}lep0_eta", f"FCCAnalyses::{particle_collection}::get_eta({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_eta", f"FCCAnalyses::{particle_collection}::get_eta({prefix}dilepton_leps)[1]")

    df_lep = df_lep.Define(f"{prefix}lep0_phi", f"FCCAnalyses::{particle_collection}::get_phi({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_phi", f"FCCAnalyses::{particle_collection}::get_phi({prefix}dilepton_leps)[1]")

    df_lep = df_lep.Define(f"{prefix}lep0_pt", f"FCCAnalyses::{particle_collection}::get_pt({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_pt", f"FCCAnalyses::{particle_collection}::get_pt({prefix}dilepton_leps)[1]")

    df_lep = df_lep.Define(f"{prefix}lep0_px", f"FCCAnalyses::{particle_collection}::get_px({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_px", f"FCCAnalyses::{particle_collection}::get_px({prefix}dilepton_leps)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_py", f"FCCAnalyses::{particle_collection}::get_py({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_py", f"FCCAnalyses::{particle_collection}::get_py({prefix}dilepton_leps)[1]")
    df_lep = df_lep.Define(f"{prefix}lep0_pz", f"FCCAnalyses::{particle_collection}::get_pz({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_pz", f"FCCAnalyses::{particle_collection}::get_pz({prefix}dilepton_leps)[1]")

    df_lep = df_lep.Define(f"{prefix}lep0_charge", f"FCCAnalyses::{particle_collection}::get_charge({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_charge", f"FCCAnalyses::{particle_collection}::get_charge({prefix}dilepton_leps)[1]")

    return df_lep