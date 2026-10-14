"""
Run with:
    fccanalysis run treemakers/tree.py

This script runs the conversion script
"treemakers/convertEDMtoNanoAODlike.py" for each dataset.

For each dataset, a temporary analysis script is created, configured
with the appropriate dataset information and normalisation, executed
with FCCAnalysis, and then removed.
"""

import os
import ROOT

from scripts.config import get_config
from utils_cli.path_utils import make_norm_dir_name


# Configuration
cfg_name = os.environ["FCC_PIPELINE_CONFIG"]
cfg = get_config(cfg_name)

TEMPLATE = "treemakers/convertEDMtoNanoAODlike.py"


# Helper functions
def get_input_dir(cfg):
    """Return the input directory for the selected sample type."""
    if cfg.sample_type == "local":
        return cfg.inputDir
    if cfg.sample_type == "central":
        return os.path.join("./localSamples", cfg.inputDir)
    raise RuntimeError(f"Unknown sample type: {cfg.sample_type}")

def count_n_generated(input_dir, dataset):
    """Count the number of generated events in a dataset."""
    filename = os.path.join(input_dir, f"{dataset}.root")
    if not os.path.exists(filename):
        raise RuntimeError(f"File not found: {filename}")
    print(f"[INFO] Counting events in: {filename}")
    df = ROOT.RDataFrame("events", filename)
    return df.Count().GetValue()

def group_datasets_by_final_state(process_list):
    """Group datasets according to their physical final state."""
    final_state_groups = {}
    for dataset, info in process_list.items():
        fs = info["fs"]
        final_state_groups.setdefault(fs, []).append(dataset)
    return final_state_groups

def count_generated_events(input_dir, final_state_groups):
    """Count the total number of generated events for each final state."""
    n_generated_groups = {}
    for fs, datasets in final_state_groups.items():
        n_generated_groups[fs] = sum(
            count_n_generated(input_dir, dataset)
            for dataset in datasets
        )
        print(
            f"[INFO] Final state {fs}: "
            f"N_generated_total = {n_generated_groups[fs]}"
        )
    return n_generated_groups


def get_output_dir(cfg, cfg_name):
    """Construct and create the tree output directory."""
    output_dir = os.path.join(
        "./output/treemaker",
        (   cfg.outputDir
            if not cfg.lumi_scaling["normalisation"]
            else make_norm_dir_name(cfg.outputDir)), cfg_name,
    )
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def create_conversion_script(
    dataset,
    info,
    cfg,
    cfg_name,
    input_dir,
    output_dir,
    n_generated_total,
):
    """Create a temporary conversion script for one dataset."""
    with open(TEMPLATE, "r") as f:
        content = f.read()

    xsec = info["crossSection"]
    genorreco = cfg.plotting["gen_or_reco"]

    replacements = {
        "__DATASET__": dataset,
        "__XSEC__": str(xsec),
        "__INPUTDIR__": input_dir,
        "__OUTPUTDIR__": output_dir,
        "__SAMPLETYPE__": cfg.sample_type,
        "__NORMALISATIONTAG__": str(cfg.lumi_scaling["normalisation"]),
        "__INTLUMI__": str(cfg.lumi_scaling["intLumi"]),
        "__GENORRECO__": str(genorreco),
        "__NGENERATED__": str(n_generated_total),
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    output_script = f"tmp_{dataset}.py"

    with open(output_script, "w") as f:
        f.write(content)

    return output_script


def run_conversion_script(output_script):
    """Run FCCAnalysis on the temporary conversion script."""

    cmd = f"fccanalysis run {output_script}"
    print(f"[INFO] Running: {cmd}")

    return os.system(cmd)


## Main workflow
input_dir = get_input_dir(cfg)
print(f"[INFO] Sample type: {cfg.sample_type}")
print(f"[INFO] Input directory: {input_dir}")

output_dir = get_output_dir(cfg, cfg_name)
print(f"[INFO] Output directory: {output_dir}")


# 1. Group datasets by final state
final_state_groups = group_datasets_by_final_state(cfg.processList)

# 2. Count total generated events per final state
n_generated_groups = count_generated_events(input_dir, final_state_groups)

# 3. Process each dataset
for dataset, info in cfg.processList.items():
    if "lep" not in info:
        raise ValueError(
            f"No lepton defined for dataset {dataset}"
        )

    lep = info["lep"]
    fs = info["fs"]
    xsec = info["crossSection"]

    n_generated_total = n_generated_groups[fs]

    weight = (xsec * cfg.lumi_scaling["intLumi"] / n_generated_total )

    print()
    print(f"[INFO] Processing dataset: {dataset}")
    print(f"[INFO]   lepton:    {lep}")
    print(f"[INFO]   final state: {fs}")
    print(f"[INFO]   xsec:      {xsec}")
    print(f"[INFO]   N_generated_total: {n_generated_total}")
    print(f"[INFO]   event weight: {weight}")

    output_script = create_conversion_script(
        dataset=dataset,
        info=info,
        cfg=cfg,
        cfg_name=cfg_name,
        input_dir=input_dir,
        output_dir=output_dir,
        n_generated_total=n_generated_total,
    )

    try:
        run_conversion_script(output_script)

    finally:
        # Always remove the temporary script, even if FCCAnalysis fails.
        if os.path.exists(output_script):
            os.remove(output_script)