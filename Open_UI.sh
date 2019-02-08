#!/bin/bash
echo "Starting quandenser-pipeline GUI"

function read_command() {
      return 1
}

while true; do
  singularity run --app quandenser_ui --bind $(pwd):$(pwd) --nv singulqand.simg
  break
done
