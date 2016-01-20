#!/usr/bin/env bash

if [ ! -d ${QC4SD_DIR} ]; then
    mkdir -p $QC4SD_DIR
fi

cd $QC4SD_DIR

# check if the project QC4SD exist with VCS
if [ ! -d ${QC4SD_DIR}/.hg ]; then
    cd ..
    rm -rf QC4SD
    hg clone https://bitbucket.org/SMBYC/qc4sd QC4SD
    cd $QC4SD_DIR
fi

# synchronize changes with repository, update and clean
hg pull
hg update -C
hg status -un|xargs rm 2> /dev/null

# print status
echo -e "\nThe last commit:\n"
hg tip
echo -e "Update finished\n"
