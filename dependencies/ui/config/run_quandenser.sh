#!/bin/bash
PROFILE="local"
CONFIG_LOCATION="/var/tmp/quandenser_pipeline_$USER"
OUTPUT_PATH="/media/storage/timothy/quandenser-pipeline/output"

NEXTFLOW_OUTPUTS="-with-trace $OUTPUT_PATH/Nextflow_output/trace.txt -with-report $OUTPUT_PATH/Nextflow_output/report.html -with-timeline $OUTPUT_PATH/Nextflow_output/timeline.html -with-dag $OUTPUT_PATH/Nextflow_output/flowchart.html"
WORK_DIRECTORY="$OUTPUT_PATH/work"
STDOUT_FILE="$OUTPUT_PATH/stdout.txt"
NF_CONFIG_LOCATION="$CONFIG_LOCATION/nf.config"
NEXTFLOW_PIPELINE="$CONFIG_LOCATION/run_quandenser.nf"
SINGULARITY_IMAGE="SingulQuand.SIF"  # Note: This means that the pipe reader needs to be in same directory as image!!
SINGULARITY_ENABLE="-with-singularity"

mkdir -p "$OUTPUT_PATH/Nextflow_output"  # Will also create output folder if it does not exist

/var/tmp/quandenser_pipeline_$USER/nextflow $NEXTFLOW_PIPELINE $SINGULARITY_ENABLE $SINGULARITY_IMAGE \
-c $NF_CONFIG_LOCATION $NEXTFLOW_OUTPUTS -w $WORK_DIRECTORY -profile $PROFILE | tee $STDOUT_FILE

# Notes: by using "-with-weblog", you could send the output to a url (HTTP POST request)
# This means you could get notified with your webserver when the pipeline is finisheds
