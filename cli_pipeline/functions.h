#ifndef DYFUNCTIONS_H
#define DYFUNCTIONS_H

#include <cmath>
#include <vector>
#include <math.h>
#include <algorithm>

#include "TLorentzVector.h"
#include "ROOT/RVec.hxx"
#include "edm4hep/ReconstructedParticleData.h"
#include "edm4hep/MCParticleData.h"
#include "edm4hep/ParticleIDData.h"
#include "ReconstructedParticle2MC.h"

namespace fcc_pipeline { namespace DYfunction {

using Vec_rp = ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>;

struct build_dilepton {

    build_dilepton() {}
    // Idea : leptons → sorted leptons → build dilepton
    // output : dilepton object + p sorted leptons

    ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>
    operator()(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> leptons) {

        ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> out;

        // 1. sort leptons by p
        auto p = [](auto const& v) {
            return std::sqrt(v.momentum.x*v.momentum.x +
                             v.momentum.y*v.momentum.y +
                             v.momentum.z*v.momentum.z);
        };

        std::sort(leptons.begin(), leptons.end(),
            [&](auto const& a, auto const& b) {
                return p(a) > p(b);
            });

        // 2. build dilepton system
        TLorentzVector sum;

        for (auto &l : leptons) {
            TLorentzVector v;
            v.SetXYZM(l.momentum.x, l.momentum.y, l.momentum.z, l.mass);
            sum += v;
        }

        edm4hep::ReconstructedParticleData dilep;

        dilep.momentum.x = sum.Px();
        dilep.momentum.y = sum.Py();
        dilep.momentum.z = sum.Pz();
        dilep.mass       = sum.M();
        dilep.energy     = sum.E();

        // 3. store as first element
        out.push_back(dilep);

        // 4. also keep leptons
        for (auto &l : leptons) {
            out.push_back(l);
        }

        return out;
    }
};

}}

#endif