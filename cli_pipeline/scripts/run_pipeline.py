import argparse
import subprocess
import os
from scripts.config import get_config

from plotmakers.plots_inclusive_fs__pyroot import run_inclusive_plots
from plotmakers.plot_nTuple import run_ntuple_plots

def parse_arg():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type = str,
        required = True,
        help = "Config name, e.g. local_prod_ee_mumu"
    )

    parser.add_argument(
        "--step",
        type = str,
        default = "all",
        choices = ["all", "hist", "tree", "plot"],
        help="Which pipeline step to run, see README"
    )

    parser.add_argument(
        "--mode",
        type = str,
        default = "inclusive",
        choices=["inclusive", "specific", "ntuple"],
        help="Plot mode selection : nTuple(ee+mumu), incluive(2 signals), specific(1 signal)"
    )

    return parser.parse_args()



def main():
    args = parse_arg()

    cfg = get_config(args.config)
    print(f"[INFO] Running pipeline with config: {args.config}")

    env = os.environ.copy()
    env["FCC_PIPELINE_CONFIG"] = args.config

    if args.step in ["all", "hist"]:
        print("[INFO] Running histmaker")

        subprocess.run(
            [
                "fccanalysis",
                "run",
                "histmaker.py"
            ],
            check=True,
            env=env,
        )
    
    if args.step in ["all", "tree"]:
        print("\n[STEP] Running treemaker")

        subprocess.run(
            [
                "python",
                "treemakers/tree.py"
            ],
            check=True,
            env=env,
        )
    
    if args.step in ["all", "plot"]:
        print("\n[STEP] Running plotmaker")

        if args.mode == "specific":
            print("\n[MODE] specific")
            subprocess.run(
                [
                    "fccanalysis",
                    "plots",
                    "plotmakers/plots_specific_fs__FCC_FW.py"
                ],
                check=True,
                env=env,
            )
        if args.mode == "inclusive":
            print("\n[MODE] inclusive")
            run_inclusive_plots(cfg)
        if args.mode == "ntuple":
            print("\n[MODE] ntuple")
            run_ntuple_plots(cfg)
    

    print("\n[DONE] Pipeline finished")

if __name__ == "__main__":
    main()
