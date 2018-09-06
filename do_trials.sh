#!/bin/bash

N=$1
DIRPATH=$2
P1=$3

for P in 0.1 0.2 0.3; do
  COUNTER=0
  while [ $COUNTER -lt $N ]; do
    python3 false_negatives_generator.py -d $DIRPATH -p $P --prob0 1.0 --prob1 $P1
    let COUNTER=COUNTER+1 
  done
done

# for P0 in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9; do
#   for C in 3 5 7 10 15; do
#     python3 combine_fairml_output.py -r $ROWTYPE -d $DIRPATH -f $P0-$C
#   done
# done
# python3 parse_fairml_output.py -r $ROWTYPE -d $DIRPATH -f $P


# for P1 in 0.4 0.5 0.6 0.7 0.8 0.9; do
#   COUNTER=0
#   while [ $COUNTER -lt $N ]; do
#     python3 statistical_parity_generator.py -r $ROWTYPE -d $DIRPATH --prob0 $P0 --prob1 $P1
#     let COUNTER=COUNTER+1 
#   done

#   python3 parse_fairml_output.py -r $ROWTYPE -d $DIRPATH -f $P0-$P1
# done


# for P in 0.5; do
#   for c in 2 3 4; do
#     mkdir $DIRPATH/$P-$c
#     COUNTER=0
#     while [ $COUNTER -lt $N ]; do
#       python3 statistical_parity_generator.py -r $ROWTYPE -d $DIRPATH/$P-$c -p $P -c $c
#       python3 audit.py -r $ROWTYPE -d $DIRPATH/$P-$c -c $c
#       let COUNTER=COUNTER+1 
#     done
#     python3 parse_fairml_complex_output.py -r $ROWTYPE -d $DIRPATH/$P-$c
#   done
# done
# for P0 in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9; do
#   for C in 0.5; do
#     COUNTER=0
#     while [ $COUNTER -lt $N ]; do
#       python3 statistical_parity_generator.py -r $ROWTYPE -d $DIRPATH --prob0 $P0 --prob1 $P1 -c $C
#       let COUNTER=COUNTER+1 
#     done
#   done
# done

# for P in 0.3 0.2 0.1; do
#   for eps in 0.1 0.2 0.3 0.4; do
#     mkdir $DIRPATH/$P-$eps
#     COUNTER=0
#     while [ $COUNTER -lt $N ]; do
#       python3 predictive_parity_generator.py -r $ROWTYPE -d $DIRPATH/$P-$eps -p $P -e $eps -t fpr
#       python3 audit.py -r $ROWTYPE -d $DIRPATH/$P-$eps
#       let COUNTER=COUNTER+1 
#     done

#     python3 parse_fairml_output.py -r $ROWTYPE -d $DIRPATH/$P-$eps
#   done
# done

# for P1 in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9; do
#   for eps in 0.1 0.2 0.3 0.4; do
#     if [ $P0 = $P1 ]; then
#        continue
#     fi
#     mkdir $DIRPATH/$P0-$P1-$eps
#     COUNTER=0
#     while [ $COUNTER -lt $N ]; do
#       python3 predictive_parity_generator.py -r $ROWTYPE -d $DIRPATH/$P0-$P1-$eps --prob0 $P0 --prob1 $P1 -e $eps -t fpr
#       python3 audit.py -r $ROWTYPE -d $DIRPATH/$P0-$P1-$eps
#       let COUNTER=COUNTER+1 
#     done

#     python3 parse_fairml_output.py -r $ROWTYPE -d $DIRPATH/$P0-$P1-$eps
#   done
# done
