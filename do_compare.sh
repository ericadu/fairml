#!/bin/bash

# for n in 1 2 3 4 5 6 7 8 9; do
#   python3 generate_model.py -f non_sp_complex${n} > ./data/model/non_sp_complex${n}_report.txt
# done

# for n in 1 2 3 4 5 6 7 8 9; do
#   python3 generate_model.py -f random${n} > ./data/model/random${n}_report.txt
# done

for n in 1 2 3 4 5 6 7 8 9; do
  python3 generate_model.py -f married${n} > ./data/model/married${n}_report.txt
done