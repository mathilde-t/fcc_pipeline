#!/bin/bash

## CAVE : run on fccenv26
local_configs=(
    "local_prod_ee_z_mumu_reco"
    "local_prod_ee_z_mumu_gen"
    "local_prod_ee_z_mumu_minus_z_res_reco"
    "local_prod_ee_z_mumu_minus_z_res_gen"
    "local_prod_ee_mumu_reco"
    "local_prod_ee_mumu_gen"
)

local_configs=(
    "local_prod_ee_mumu_reco"
    "local_prod_ee_mumu_gen"
)

## CAVE : run on fccenv24
central_configs=(
    "central_prod_ee_mumu_reco"
    "central_prod_ee_mumu_gen"
)

# Select which set of configs to run
# for full pipeline, run on central cfg fist, then on local cfgs to make the ak plot possible
# configs=("${central_configs[@]}")
configs=("${local_configs[@]}")


## Tree step
for config in "${configs[@]}"; do

    echo "========================================"
    echo "Running tree for config: $config"
    echo "========================================"

    python scripts/run_pipeline.py --config "$config" --step tree

    if [ $? -ne 0 ]; then
        echo "Error while running $config"
        exit 1
    fi
done


## Plot step
for config in "${configs[@]}"; do

    echo "========================================"
    echo "Running plot for config: $config"
    echo "========================================"

    if [[ "$config" == local* ]]; then
        python scripts/run_pipeline.py --config "$config" --step plot --mode allpr
    elif [[ "$config" == central* ]]; then
        python scripts/run_pipeline.py --config "$config" --step plot --mode cat
        python scripts/run_pipeline.py --config "$config" --step plot --mode allpr
    else
        echo "Unknown config style: $config"
        exit 1
    fi

    if [ $? -ne 0 ]; then
        echo "Error while running $config"
        exit 1
    fi
done

for config in "${configs[@]}"; do

    echo "========================================"
    echo "Running category closure tests for config: $config"
    echo "========================================"

    if [[ "$config" == local* && "$config" == *"_z_"* ]]; then
        python scripts/run_pipeline.py --config "$config" --step plot --mode closure
        continue
    else
        echo "Non-z config: $config"
        continue
    fi

    if [ $? -ne 0 ]; then
        echo "Error while running $config"
        exit 1
    fi
done

echo "========================================"
echo "Running ratio plots : local vs central lines"
echo "========================================"

python plotmakers/plots_ratio_local_to_central.py

for config in "${local_configs[@]}"; do

    # Only run for inclusive configs
    if [[ "$config" != "local_prod_ee_mumu_reco" && \
          "$config" != "local_prod_ee_mumu_gen" ]]; then
        continue
    fi

    echo "========================================"
    echo "Running ak local vs central + ratio plots for config : $config"
    echo "========================================"

    if [[ "$config" == local* ]]; then
        python scripts/run_pipeline.py --config "$config" --step plot --mode ak
    else
        echo "Non-local or unknown config style: $config", must be local config
        exit 1
    fi

    if [ $? -ne 0 ]; then
        echo "Error while running $config"
        exit 1
    fi
done

echo "All done :)"