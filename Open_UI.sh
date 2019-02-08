#!/bin/bash
echo "Starting quandenser-pipeline GUI"

function read_command() {
  str_old="IMAGE_LOCATION=.*"
  str_replace="IMAGE_LOCATION=$(pwd)/SingulQuand.SIF"
  sed -ri "s|${str_old}|${str_replace}|g" "/var/tmp/quandenser_pipeline_$USER/PIPE"
  echo "Hello"
}

while true; do
  #singularity run --app quandenser_ui --bind $(pwd):$(pwd) --nv SingulQuand.SIF
  #wait
  echo "DONE"
  read_command
  break
done
