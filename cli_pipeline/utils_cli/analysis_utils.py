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

    df_lep = df_lep.Define(
        f"{prefix}lep_all_pt",
        f"FCCAnalyses::ReconstructedParticle::get_pt({prefix}lep_all)"
    )

    df_lep = df_lep.Define(f"{prefix}px__wo__n_lep_cut", f"FCCAnalyses::ReconstructedParticle::get_px({prefix}lep_all)")
    df_lep = df_lep.Define(f"{prefix}py__wo__n_lep_cut", f"FCCAnalyses::ReconstructedParticle::get_py({prefix}lep_all)")
    df_lep = df_lep.Define(f"{prefix}pz__wo__n_lep_cut", f"FCCAnalyses::ReconstructedParticle::get_pz({prefix}lep_all)")

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

    #df = df.Define(f"{prefix}lep_pcut", f"FCCAnalyses::MCParticle::sel_pt({pt_cut})({prefix}lep_all)")
    df = df.Define(f"{prefix}lep_pcut", f"{prefix}lep_all")
    print("pt cut at : ", pt_cut)
    print("n cut at  : ", n_lep_cut)

    #df = df.Define(f"{prefix}n_lep", f"FCCAnalyses::MCParticle::get_n({prefix}lep_pcut)")
    df = df.Define(f"{prefix}n_lep", f"{prefix}lep_pcut.size()") #TODO exchange this back to lep_pcut, but at this moment that cuts one of the 2 peak s(2 from 0 and 2) which is bad

    df = df.Filter(f"{prefix}n_lep >= {n_lep_cut}", f"require at least {n_lep_cut} {lep}s")

    # include this as a xcheck, shoundnt peak at/ close to 0
    df = df.Define(
        f"{prefix}lep_all_pt",
        f"FCCAnalyses::MCParticle::get_pt({prefix}lep_all)"
    )
    #df = df.Define(f"{prefix}debug_px", "Particle.momentum.x")
    #df = df.Define(f"{prefix}debug_py", "Particle.momentum.y")
    #df = df.Define(f"{prefix}debug_pz", "Particle.momentum.z")

    df = df.Define(f"{prefix}px__wo__n_lep_cut", f"FCCAnalyses::MCParticle::get_px({prefix}lep_all)")
    df = df.Define(f"{prefix}py__wo__n_lep_cut", f"FCCAnalyses::MCParticle::get_py({prefix}lep_all)")
    df = df.Define(f"{prefix}pz__wo__n_lep_cut", f"FCCAnalyses::MCParticle::get_pz({prefix}lep_all)")

    return df


def build_dilepton(df_lep, lep, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix

    # build the dilepton system
    df_lep = df_lep.Define(f"{prefix}dilepton_result", f"fcc_pipeline::DYfunction::build_dilepton()({prefix}lep_pcut)")
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
    df_lep = df_lep.Define(f"{prefix}lep0_p", f"{prefix}lep_p[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_p", f"{prefix}lep_p[1]")
    
    return df_lep

def define_lepton_observables(df_lep, lep, particle_collection, prefix=None):
    prefix = f"{lep}_" if prefix is None else prefix

    df_lep = df_lep.Define(f"{prefix}lep0_eta", f"FCCAnalyses::{particle_collection}::get_eta({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_eta", f"FCCAnalyses::{particle_collection}::get_eta({prefix}dilepton_leps)[1]")

    df_lep = df_lep.Define(f"{prefix}lep0_phi", f"FCCAnalyses::{particle_collection}::get_phi({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_phi", f"FCCAnalyses::{particle_collection}::get_phi({prefix}dilepton_leps)[1]")

    df_lep = df_lep.Define(f"{prefix}lep0_pt", f"FCCAnalyses::{particle_collection}::get_pt({prefix}dilepton_leps)[0]")
    df_lep = df_lep.Define(f"{prefix}lep1_pt", f"FCCAnalyses::{particle_collection}::get_pt({prefix}dilepton_leps)[1]")

    return df_lep