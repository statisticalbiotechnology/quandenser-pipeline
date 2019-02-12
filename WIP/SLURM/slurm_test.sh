#!/bin/bash
PROFILE="standard_restricted"
NEXTFLOW_OUTPUTS="-with-trace Nextflow_output/trace.txt -with-report Nextflow_output/report.html -with-timeline Nextflow_output/timeline.html -with-dag Nextflow_output/flowchart.html"
NEXTFLOW_PIPELINE="slurm_test.nf"
NETXTFLOW_CONFIG="slurm_test.config"

mkdir -p "Nextflow_output"

./nextflow run $NEXTFLOW_PIPELINE -c $NETXTFLOW_CONFIG $NEXTFLOW_OUTPUTS -profile $PROFILE | tee Nextflow_output/stdout.txt
echo "SUBMITTED"
