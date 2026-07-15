#ifndef DYFUNCTIONS_H
#define DYFUNCTIONS_H 

#include <algorithm>
#include <cmath>
#include <math.h>
#include <vector>
#include <type_traits>

#include "TLorentzVector.h"
#include "ROOT/RVec.hxx"
#include "edm4hep/ReconstructedParticleData.h"
#include "edm4hep/MCParticleData.h"
#include "edm4hep/ParticleIDData.h"
#include "edm4hep/Vector3f.h"
#include "ReconstructedParticle2MC.h"

namespace fcc_pipeline {
namespace DYfunction {

struct build_dilepton {

    build_dilepton() {}

    // Idea : leptons → sorted leptons → build dilepton
    // output : dilepton object + p sorted leading leptons
    // compatible with both ReconstructedParticleData (reco-level) and MCParticleData (gen-level)

    template <typename Particle>
    ROOT::VecOps::RVec<Particle>
    operator()(ROOT::VecOps::RVec<Particle> leptons) const {

        ROOT::VecOps::RVec<Particle> out;

        // require at least two leptons to build a dilepton system
        // otherwise no valid dilepton candidate exists
        if (leptons.size() < 2)
            return out;


        // 1. Sort leptons by momentum magnitude
        // The two highest momentum leptons are used to build the dilepton system
        auto p = [](const auto& v) {
            return std::sqrt(
                v.momentum.x * v.momentum.x +
                v.momentum.y * v.momentum.y +
                v.momentum.z * v.momentum.z
            );
        };


        std::sort(
            leptons.begin(),
            leptons.end(),
            [&](const auto& a, const auto& b) {
                return p(a) > p(b);
            }
        );


        // 2. Build dilepton four-vector from the two leading leptons
        TLorentzVector sum;

        for (int i = 0; i < 2; i++) {

            TLorentzVector v;

            v.SetXYZM(
                leptons[i].momentum.x,
                leptons[i].momentum.y,
                leptons[i].momentum.z,
                leptons[i].mass
            );

            sum += v;
        }


        // 3. Create output particle for the dilepton system
        Particle dilep{};

        dilep.momentum.x = sum.Px();
        dilep.momentum.y = sum.Py();
        dilep.momentum.z = sum.Pz();

        dilep.mass = sum.M();

        // ReconstructedParticleData contains an energy member
        // MCParticleData does not need to store the energy here
        if constexpr (std::is_same_v<Particle, edm4hep::ReconstructedParticleData>) {
            dilep.energy = sum.E();
        }


        // 4. Store dilepton first
        // output convention:
        // [0] = dilepton system
        // [1] = leading lepton
        // [2] = subleading lepton
        out.push_back(dilep);


        // 5. Store the two leptons used for the dilepton afterwards
        out.push_back(leptons[0]);
        out.push_back(leptons[1]);


        return out;
    }
};

} // namespace DYfunction
} // namespace fcc_pipeline

#endif