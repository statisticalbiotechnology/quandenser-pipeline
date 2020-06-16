#!/bin/bash

# Changeable
PROFILE="local"
OUTPUT_PATH=""
OUTPUT_PATH_LABEL=""
USE_DOCKER="false"
EMAIL_NOTIFICATION=""
CONFIG_LOCATION=""

# Static
WORK_DIRECTORY="$OUTPUT_PATH/work"  # Work should always be merged, multiple runs should use same
NF_CONFIG_LOCATION="$CONFIG_LOCATION/nf.config"
NEXTFLOW_PIPELINE="$CONFIG_LOCATION/run_quandenser.nf"
if [ "$USE_DOCKER" == "true" ]; then
  IMAGE="-with-docker matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses"
else
  IMAGE="-with-singularity SingulQuand.SIF"  # Note: This means that the pipe reader needs to be in same directory as image!!
fi
OUTPUT_PATH="$OUTPUT_PATH$OUTPUT_PATH_LABEL"  # Modify output path after workpath has been set
STDOUT_FILE="$OUTPUT_PATH/stdout.txt"
NEXTFLOW_OUTPUTS="-with-trace $OUTPUT_PATH/Nextflow_output/trace.txt -with-report $OUTPUT_PATH/Nextflow_output/report.html -with-timeline $OUTPUT_PATH/Nextflow_output/timeline.html -with-dag $OUTPUT_PATH/Nextflow_output/flowchart.html"

mkdir -p "$OUTPUT_PATH/Nextflow_output"  # Will also create output folder if it does not exist

$CONFIG_LOCATION/nextflow run $NEXTFLOW_PIPELINE $IMAGE \
-c $NF_CONFIG_LOCATION $NEXTFLOW_OUTPUTS -w $WORK_DIRECTORY -profile $PROFILE $EMAIL_NOTIFICATION \
| tee -a $STDOUT_FILE

# Notes: by using "-with-weblog", you could send the output to a url (HTTP POST request)
# This means you could get notified with your webserver when the pipeline is finished
