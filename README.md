### Steps to run the analysis pipeline

`source /cvmfs/sw.hsf.org/key4hep/setup.sh`

0. generate data locally with the fcc_generation directory scripts/ or use centrally produced ones
1. `functions.h` : define necessary functions if not already in the FCC FW
2. `histmaker` files : load certain samples, create all the wanted histograms from that 
        fccanalysis run 1_histmakers/hists_SPECIFIC_NAME.py
3. `treemaker` : convert the EDM4hep format into a flat tree for all hists 
        fccanalysis run 2_treemakers/convertEDMtoNanoAODlike.py
4. `plotmaker` files : configure the desired plots
        fccanalysis plots 3_plotmakers/plots_SPECIFIC_NAME.py