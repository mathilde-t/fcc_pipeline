# FCC Drell–Yan Analysis Pipeline

This repository contains an FCCAnalysis framework for the analysis of Drell–Yan events decaying into di-electron and/ or di-muon final states, supporting locally and centrally produced data. The pipeline can be executed in two different ways:

* **Command-line interface (`cli_pipeline/`)** – recommended for routine analyses and complete workflow execution.
* **Stepwise interface (`stepwise_pipeline/`)** – intended for understanding, developing and debugging the analysis. Its structure closely follows the official FCCAnalysis [tutorial](https://hep-fcc.github.io/fcc-tutorials/main/index.html).

---

## Environment setup

Before running the analysis, source the appropriate Key4hep environment.
For locally produced samples:
```bash
source /cvmfs/sw.hsf.org/key4hep/setup.sh
```

For centrally produced samples, source the corresponding central production environment.

---

## Pipeline explication and usage of the stepwise execution

All commands below should be executed from `fcc_pipeline/stepwise_pipeline/`. 
The command-line interface described later is launched from `fcc_pipeline/cli_pipeline/`.

The pipeline consists of the following stages:

**0. Prepare the input samples**
The analysis can be performed either on
* locally generated samples produced with the scripts in `fcc_generation/`, or
* centrally produced FCC datasets.

**1. Shared analysis functions** `functions.h`
This header contains custom C++ helper functions used throughout the analysis whenever equivalent implementations are not already provided by FCCAnalysis.

**2. Configure the analysis**
All dataset-dependent settings are centralised in a set of configuration files:

* `scripts/data_configs.json` – dataset definitions, input/output directories, process lists, and cross sections
* `scripts/hist_config.py` – histogram definitions and binning
* `scripts/plot_config.py` – plotting configuration
* `scripts/config.py` – configuration interface providing `get_config()` (should normally not be modified)

The analysis is configured simply by selecting

```python
cfg = get_config("<config_name>")
```

No changes to the analysis code are required when switching between datasets.
Note : all barn values given, should be given in femto units.

**3. Histogram production**
The histogram maker contains the physics analysis logic, while all dataset-specific information is provided through the configuration system.

Run:
```bash
fccanalysis run histmakers/histmaker.py
```

**4. Tree production**
The tree maker converts EDM4Hep files into flat NanoAOD-like analysis trees. The conversion script `treemakers/convertEDMtoNanoAODlike.py` automatically creates temporary FCCAnalysis configuration files for each dataset and executes them sequentially.

Run:
```bash
fccanalysis run treemakers/tree.py
```

**5. Plot production**
Several plotting scripts are available depending on the desired output:

* `plots_specific_fs__FCC_FW.py` uses the built-in FCCAnalysis plotting utilities to produce plots for a single final state
* `plots_inclusive_fs__pyroot.py` combines several final states using PyROOT
* `plot_nTuple.py` is a lightweight Python plotting script intended for quick studies and cross-checks

Run:
```bash
fccanalysis plots plotmakers/plots_<config_name>.py
```

The output is written to the directory specified in `scripts/data_configs.json`.


## Command-line execution

The complete workflow can also be executed from the command line.
First ensure that the appropriate Key4hep environment has been sourced as mentioned above and that the working directory path is `fcc_pipeline/cli_pipeline/`.

The full analysis pipeline is launched with

```bash
python scripts/run_pipeline.py --config <config_name>
```

By default, this executes the workflow in the order:

1. histogram production,
2. tree production,
3. inclusive plot production.

Individual stages can be executed when adding `--step` and specifying the stage to execute: `all`, `hist`, `tree`, or `plot`. `all` is the default setting.

To choose a differnt plotting script, the `--mode` parameter can be added. It takes `inclusive`, `specific`, and `ntuple` corresponding to the tree plotting scripts. `inclusive` is the default.