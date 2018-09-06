#!/bin/bash

for eps in .01 .02 .03 .04; do
    for cor in 2 4 8 12 16; do
        python3 attack/generate_data.py -e $eps -c $cor
        python3 attack/attack_synthetic.py
    done
done | tee ./output/benchmark_results.txt
