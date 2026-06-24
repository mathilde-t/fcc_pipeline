'''
run with : fccanalysis run 2_treemakers/tree.py

This script runs the conversion script "2_treemakers/convertEDMtoNanoAODlike.py" for each dataset, 
by creating temporary config files on the fly and executing them with FCCAnalysis. 
'''

import os
import shutil

datasets = {
    "ee_ee_ecm91_delphes": {"lep": "Electron", "xsec": 2020.4,},
    "ee_mumu_ecm91_delphes": {"lep": "Muon", "xsec": 2024.7,},
}

datasets = {
    "events_003635753": {"lep": "Electron", "xsec": 2020.4,},
    "events_007405803": {"lep": "Muon", "xsec": 2024.7,},
    "events_009996087": {"lep": "Electron", "xsec": 2020.4,},
}
template = "2_treemakers/convertEDMtoNanoAODlike.py"

for dataset, info in datasets.items():

    lep = info["lep"]
    xsec = info["xsec"]
    print(f"Processing dataset: {dataset} with lepton: {lep}")

    # create temporary analysis config
    output_script = f"tmp_{dataset}.py"

    with open(template, "r") as f:
        content = f.read()

    content = content.replace("__LEPTON__", lep)
    content = content.replace("__DATASET__", dataset)
    content = content.replace("__XSEC__", str(xsec))

    with open(output_script, "w") as f:
        f.write(content)

    # run FCCAnalysis
    cmd = f"fccanalysis run {output_script}"

    print(f"Running: {cmd}")

    os.system(cmd)

    # cleanup
    os.remove(output_script)