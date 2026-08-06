import argparse
import subprocess
import os
from scripts.config import get_config

from plotmakers.plots_inclusive_fs__pyroot import run_inclusive_plots
from plotmakers.plot_nTuple import run_ntuple_plots
from plotmakers.plots_pyroot import run_allpr_plots
from plotmakers.plots_categorisation import run_category_plots
from plotmakers.plot_ak_var_per_level_plus_ratio import run_ak_plots

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
        choices=["inclusive", "specific", "ntuple", "allpr", "cat", "ratio", "closure", "ak"],
        help="Plot mode selection : incluive(2 signals), specific(1 signal), nTuple(ee+mumu), allpr(with pyroot), cat(category plots for central samples), ratio(ratio plots per hists), closure(closure test for local line), ak(merged plot with ak, per hist, local vs central)"
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
            run_inclusive_plots(cfg, args.config)

        if args.mode == "allpr":
            print("\n[MODE] all pyroot")
            run_allpr_plots(cfg, args.config)

        if args.mode == "cat":
            print("\n[MODE] category plots")
            run_category_plots(cfg, args.config)

        if args.mode == "ntuple":
            print("\n[MODE] ntuple")
            run_ntuple_plots(cfg)

        if args.mode == "ratio":
            print("\n[MODE] ratio plots")
            subprocess.run(
                [
                    "python",
                    "plotmakers/plots_ratio_local_to_central.py"
                ],
                check=True,
                env=env,
            )

        if args.mode == "closure":
            print("\n[MODE] closure test")
            subprocess.run(
                [
                    "python",
                    "plotmakers/plots_closure_local.py"
                ],
                check=True,
                env=env,
            )

        if args.mode == "ak":
            print("\n[MODE] merged plot with ak")
            run_ak_plots(cfg, args.config)
    

    print("\n[DONE] Pipeline finished")

if __name__ == "__main__":
    main()
