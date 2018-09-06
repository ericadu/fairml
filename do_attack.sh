#!/bin/bash

python3 attack/generate_data.py "$@"
head data/attack_data.csv
python3 attack/attack_synthetic.py
open output/fairml_attack.png
