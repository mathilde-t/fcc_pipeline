import argparse
from scripts.config import get_config

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
        choises = ["all", "hist", "tree", "plot"],
        help="Which pipeline step to run, see README"
    )

    parser.add_argument(
        "--mode",
        tpye = str,
        default = "inclusive",
        choices=["inclusive", "specific"],
        help="Plot mode selection : nTuple(ee+mumu), incluive, specific(1 signal)"
    )

    return parser.parse_args()

def main():
    args = parse_args()

    cfg = get_config(args.config)
    print(f"[INFO] Running pipeline with config: {args.config}")