#!/bin/bash

DIRPATH=$1
ROWTYPE=$2

# for P0 in 0.1 0.2 0.3 0.4 0.5; do
#   for P1 in 0.6 0.7 0.8 0.9; do
#     if [ $P0 = $P1 ]; then
#        continue
#     fi
#     for eps in 0.1 0.2 0.3 0.4; do
#       python3 parse_fairml_output.py -r $ROWTYPE -d $DIRPATH/$P0-$P1-$eps
#     done
#   done
# done
# for P in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9; do
#   for eps in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9; do
#     python3 parse_fairml_output.py -r $ROWTYPE -d $DIRPATH/$P-$eps
#   done
# done

for P in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9; do
  python3 parse_fairml_output.py -r $ROWTYPE -d $DIRPATH/$P
done