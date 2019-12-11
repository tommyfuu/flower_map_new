#!/bin/bash

# An example bash script demonstrating how to run the entire snakemake pipeline
# This script creates two separate log files:
# 	1) log - the basic snakemake log of completed rules
# 	2) qlog - a more detailed log of the progress of each rule and any errors

# you can specify a directory for all output here:
out_path="$PWD/out"
mkdir -p "$out_path"

# clear leftover log files
if [ -f "${out_path}/log" ]; then
	echo ""> "${out_path}/log";
fi
if [ -f "${out_path}/qlog" ]; then
	echo ""> "${out_path}/qlog";
fi

# make sure that this script is executed from the directory that it lives in!

# Before running this snakemake pipeline, remember to complete the config file
# with the required input info. In particular, make sure that you have created
# a samples.tsv file specifying paths to your drone imagery.

snakemake \
-j 12 \
--config out="${out_path}" \
--latency-wait 60 \
--use-conda \
-k \
"$@" >>"${out_path}/log" 2>&1