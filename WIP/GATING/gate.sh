#!/bin/bash
NEXTFLOW_OUTPUTS="-with-trace Nextflow_output/trace.txt -with-report Nextflow_output/report.html -with-timeline Nextflow_output/timeline.html -with-dag Nextflow_output/flowchart.html"
NEXTFLOW_PIPELINE="gate.nf"
NETXTFLOW_CONFIG="gate.config"

mkdir -p "Nextflow_output"

./nextflow $NEXTFLOW_PIPELINE -c $NETXTFLOW_CONFIG $NEXTFLOW_OUTPUTS | tee Nextflow_output/stdout.txt
echo "SUBMITTED"