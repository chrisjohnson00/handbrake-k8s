#!/bin/bash
set -e
#
# input params:
# 1 - input file name
# 2 - output file name
# 3 - profile name

IN_FILE_NAME=$1
OUT_FILE_NAME=$2
ENC_PROFILE=$3

python3 /wrapper.py "${IN_FILE_NAME}" "${OUT_FILE_NAME}" "${ENC_PROFILE}"
