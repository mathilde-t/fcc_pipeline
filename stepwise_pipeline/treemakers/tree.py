'''
run with : fccanalysis run treemakers/tree.py

This script runs the conversion script "treemakers/convertEDMtoNanoAODlike.py" for each dataset, 
by creating temporary config files on the fly and executing them with FCCAnalysis. 
'''

import os
from scripts.config import get_config

cfg = get_config("local_prod_ee_mumu")

template = "treemakers/convertEDMtoNanoAODlike.py"

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

    content = content.replace("__INPUTDIR__", cfg.inputDir)
    content = content.replace("__OUTPUTDIR__", cfg.outputDir)
    content = content.replace(
        "__PRODTAG__",
        f'prodTag = "{cfg.prodTag}"' if cfg.prodTag else ""
    )

    with open(output_script, "w") as f:
        f.write(content)

    # run FCCAnalysis
    cmd = f"fccanalysis run {output_script}"

    print(f"Running: {cmd}")

    os.system(cmd)

    # cleanup
    os.remove(output_script)