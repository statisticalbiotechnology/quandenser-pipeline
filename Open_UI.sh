#!/bin/bash
cd "$(dirname "$0")"  # Go to dir where the script lies, this allows for links to work

function PIPE_read() {
  # grep: -o, only get match, cut: -d'=' deliminter and get second column
  value=$(grep -o "$1=.*" "/var/tmp/quandenser_pipeline_$USER/PIPE" | cut -d'=' -f2)
  echo $value
}

function PIPE_write() {
  parameter="$1=.*"
  value="$1=$2"
  # sed: -i overwrite in file, -E = regular expressions
  sed -i -E "s|${parameter}|${value}|g" "/var/tmp/quandenser_pipeline_$USER/PIPE"
}

function read_command() {
  exit_code=$(PIPE_read "exit_code")
  echo $exit_code
  # Exit codes:
  # 0 = run button pressed --> run the nextflow pipeline
  # 1 = soft exit, closed window --> Do not run anything
  # 2 = hard exit, python crashed --> Rerun 3 times and stop if not working
  if [ $exit_code == 0 ]; then
    echo "Run"
  elif [ $exit_code == 1 ]; then
    echo "Soft exit"
  elif [ $exit_code == 2 ]; then
    echo "Hard exit"
  fi
}

while true; do
  #singularity run --app quandenser_ui --bind $(pwd):$(pwd) --nv SingulQuand.SIF
  #wait
  read_command
  break
done
