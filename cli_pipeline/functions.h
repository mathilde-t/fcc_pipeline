#ifndef DYFUNCTIONS_H
#define DYFUNCTIONS_H

#include <algorithm>
#include <cmath>
#include <math.h>
#include <vector>
#include <type_traits>
#include <random>

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

    // Build dilepton candidate from the two highest momentum leptons
    //
    // Output convention:
    //
    // out[0] : dilepton system
    // out[1] : leading lepton
    // out[2] : subleading lepton
    //
    // If fewer than two leptons exist:
    // return empty vector
    //
    // Validity can later be checked with:
    // collection.size() == 3

    template <typename Particle>
    ROOT::VecOps::RVec<Particle>
    operator()(ROOT::VecOps::RVec<Particle> leptons) const {

        ROOT::VecOps::RVec<Particle> out;

        // no valid dilepton candidate
        if (leptons.size() < 2) {
            return out;
        }

        // momentum magnitude used for sorting
        auto p = [](const auto& v) {
            return std::sqrt(
                v.momentum.x * v.momentum.x +
                v.momentum.y * v.momentum.y +
                v.momentum.z * v.momentum.z
            );
        };

        // sort descending in momentum
        std::sort(
            leptons.begin(),
            leptons.end(),
            [&](const auto& a, const auto& b) {
                return p(a) > p(b);
            }
        );

        // take leading 2 os leptons
        if (leptons[0].charge == leptons[1].charge) {
            return out;
        }

        // build four-vector sum
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

        // create dilepton object
        Particle dilep{};

        dilep.momentum.x = sum.Px();
        dilep.momentum.y = sum.Py();
        dilep.momentum.z = sum.Pz();

        dilep.mass = sum.M();


        // ReconstructedParticleData has energy
        // MCParticleData does not
        if constexpr (
            std::is_same_v<
                Particle,
                edm4hep::ReconstructedParticleData
            >
        ) {
            dilep.energy = sum.E();
        }

        // store:
        // [0] dilepton
        // [1] leading lepton
        // [2] subleading lepton

        out.push_back(dilep);
        out.push_back(leptons[0]);
        out.push_back(leptons[1]);

        return out;
    }
};

template <typename Particle>
ROOT::VecOps::RVec<Particle>
sort_pt(ROOT::VecOps::RVec<Particle> particles) {

    // Randomise the initial ordering
    static thread_local std::mt19937 rng(std::random_device{}());

    std::shuffle(
        particles.begin(),
        particles.end(),
        rng
    );

    // Sort by descending pT.
    // For equal pT, stable_sort keeps the random order.
    std::stable_sort(
        particles.begin(),
        particles.end(),
        [](const auto& a, const auto& b) {

            const float pt_a = std::sqrt(
                a.momentum.x * a.momentum.x +
                a.momentum.y * a.momentum.y
            );

            const float pt_b = std::sqrt(
                b.momentum.x * b.momentum.x +
                b.momentum.y * b.momentum.y
            );

            return pt_a > pt_b;
        }
    );

    return particles;
}

} // namespace DYfunction
} // namespace fcc_pipeline

#endif