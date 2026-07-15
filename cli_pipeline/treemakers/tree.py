'''
run with : fccanalysis run treemakers/tree.py

This script runs the conversion script "treemakers/convertEDMtoNanoAODlike.py" for each dataset, 
by creating temporary config files on the fly and executing them with FCCAnalysis. 
'''

import os
from scripts.config import get_config
from utils_cli.path_utils import make_norm_dir_name

cfg_name = os.environ["FCC_PIPELINE_CONFIG"]
cfg = get_config(cfg_name)

template = "treemakers/convertEDMtoNanoAODlike.py"

### debug
#print("TREE MODULE LOADED")
#print("has build_graph:", "build_graph" in globals())
#print("globals:", list(globals().keys()))


for dataset, info in cfg.processList.items():

    if "lep" not in info:
        raise ValueError(f"No lepton defined for dataset {dataset}")

    lep = info["lep"]
    xsec = info["crossSection"]
    print(f"Processing dataset: {dataset} with lepton: {lep}")

    # create temporary analysis config
    output_script = f"tmp_{dataset}.py"

    with open(template, "r") as f:
        content = f.read()

    content = content.replace("__LEPTON__", lep)
    content = content.replace("__DATASET__", dataset)
    content = content.replace("__XSEC__", str(xsec))
    inputDir = os.path.join(
        "./localSamples/",
        cfg.inputDir
    )
    print(f"[INFO] tree inputDir: {inputDir}")
    content = content.replace("__INPUTDIR__", inputDir)

    outputDir = os.path.join(
        "./output/treemaker/",
        cfg.outputDir if not cfg.lumi_scaling["normalisation"] else make_norm_dir_name(cfg.outputDir),
        cfg_name
    )
    os.makedirs(outputDir, exist_ok=True)
    print(f"[INFO] save tree to outputDir: {outputDir}")
    content = content.replace("__OUTPUTDIR__", outputDir)
    content = content.replace(
        "__PRODTAG__",
        f'prodTag = "{cfg.prodTag}"' if cfg.prodTag else ""
    )
    content = content.replace("__SAMPLETYPE__", cfg.sample_type)
    content = content.replace("__NORMALISATIONTAG__", str(cfg.lumi_scaling["normalisation"]))
    content = content.replace("__INTLUMI__", str(cfg.lumi_scaling["intLumi"]))
    content = content.replace("__NGENERATED__", str(cfg.lumi_scaling["n_generated"]))
    content = content.replace("__GENORRECO__", str(cfg.plotting["gen_or_reco"]))

    with open(output_script, "w") as f:
        f.write(content)

    # run FCCAnalysis
    cmd = f"fccanalysis run {output_script}"

    print(f"Running: {cmd}")

    os.system(cmd)
    
    # cleanup
    os.remove(output_script)