#!/bin/bash

N=$1
DIRPATH=$2
SETTINGS=$3
THREADS=$4

python3 audit.py -r $N -d $DIRPATH -s $SETTINGS -t $THREADS