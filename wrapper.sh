#!/bin/bash
set -e

# input params:
# 1 - input file name
# 2 - output file name
# 3 - profile name

IN_FILE_NAME=$1
OUT_FILE_NAME=$2
ENC_PROFILE=$3

echo "Copying file into container FS"
cp "/input/${IN_FILE_NAME}" "/encode_in/${IN_FILE_NAME}"

HandBrakeCLI -i "/encode_in/${IN_FILE_NAME}" -o "/encode_out/${OUT_FILE_NAME}" --preset "${ENC_PROFILE}"

echo "Moving output file from container FS to mounted output dir"
mv "/encode_out/${OUT_FILE_NAME}" "/output/${OUT_FILE_NAME}"

echo "Removing input file"
rm -f "/input/${IN_FILE_NAME}"
