#!/bin/bash
#!/bin/bash
NEXTFLOW_OUTPUTS="-with-trace Nextflow_output/trace.txt -with-report Nextflow_output/report.html -with-timeline Nextflow_output/timeline.html -with-dag Nextflow_output/flowchart.html"
NEXTFLOW_PIPELINE="msconvert.nf"
CONFIG_LOCATION="../config/nf.config"  # CHANGE TO REAL PATH AFTER WIP
SINGULARITY_IMAGE="../singulqand.simg" # CHANGE TO REAL PATH AFTER WIP
SINGULARITY_ENABLE="-with-singularity"
STDOUT_FILE="Nextflow_output/stdout.txt"

./nextflow $NEXTFLOW_PIPELINE $SINGULARITY_ENABLE $SINGULARITY_IMAGE -c $CONFIG_LOCATION $NEXTFLOW_OUTPUTS | tee $STDOUT_FILE

# Notes: by using "-with-weblog", you could send the output to a url (HTTP POST request)
# This means you could get notified with your webserver when the pipeline is finisheds
