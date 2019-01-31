#!/bin/bash
OUTPUT_PATH="/media/storage/timothy/quandenser-pipeline/output"
NEXTFLOW_OUTPUTS="-with-trace $OUTPUT_PATH/Nextflow_output/trace.txt -with-report $OUTPUT_PATH/Nextflow_output/report.html -with-timeline $OUTPUT_PATH/Nextflow_output/timeline.html -with-dag $OUTPUT_PATH/Nextflow_output/flowchart.html"
NEXTFLOW_PIPELINE="run_quandenser.nf"
WORK_DIRECTORY="$OUTPUT_PATH/work"
STDOUT_FILE="$OUTPUT_PATH/stdout.txt"
CONFIG_LOCATION="config/nf.config"  # CHANGE TO REAL PATH AFTER WIP
SINGULARITY_IMAGE="singulqand.simg" # CHANGE TO REAL PATH AFTER WIP
SINGULARITY_ENABLE="-with-singularity"

mkdir -p "$OUTPUT_PATH/Nextflow_output"

./nextflow $NEXTFLOW_PIPELINE $SINGULARITY_ENABLE $SINGULARITY_IMAGE \
-c $CONFIG_LOCATION $NEXTFLOW_OUTPUTS -w $WORK_DIRECTORY | tee $STDOUT_FILE

# Notes: by using "-with-weblog", you could send the output to a url (HTTP POST request)
# This means you could get notified with your webserver when the pipeline is finisheds
