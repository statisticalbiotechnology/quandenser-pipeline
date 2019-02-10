#!/bin/bash
cd "$(dirname "$0")"  # Go to dir where the script lies, this allows for links to work

function PIPE_read() {
  # grep: -o, only get match, cut: -d'=' deliminter and get second column, tr: clear carriage return
  value=$(grep -o "$1=.*" "/var/tmp/quandenser_pipeline_$USER/PIPE" | cut -d'=' -f2 | tr -d '\r')
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
  # Exit codes:
  # 0 = run button pressed --> run the nextflow pipeline
  # 1 = soft exit, closed window --> Do not run anything
  # 2 = hard exit, python crashed --> Rerun 3 times and stop if not working
  echo $exit_code
}

declare -i crash_count=0
mount_point=""
for var in "$@"
do
  mount_point+=" --bind $var:$var"
done
if [ -f /var/tmp/quandenser_pipeline_$USER/PIPE ]; then
  PIPE_write "custom_mounts" "$mount_point"
else
  echo "PIPE not found. It will be created when running the GUI"
fi

while true; do
  singularity run --app quandenser_ui --bind $(pwd):$(pwd)$mount_point SingulQuand.SIF
  wait
  result=$(read_command)
  if [ "$result" = "0" ]; then
    crash_count=0  # Reset
    chmod u+x /var/tmp/quandenser_pipeline_$USER/nextflow.sh  # Fix permission
    chmod u+x /var/tmp/quandenser_pipeline_$USER/run_quandenser.sh  # Fix permission
    nohup /var/tmp/quandenser_pipeline_$USER/run_quandenser.sh & pid=$!
    PIPE_write "pid" $pid  # Write pid to pipe
  elif [ "$result" = "1" ]; then
    break
  elif [ "$result" = "2" ]; then
    crash_count=$crash_count+1
    echo $crash_count
    if [ $crash_count -gt 3 ]; then
      echo "The GUI crashed 3 times. Aborting"
      break
    fi
  fi
done
cd -  # Go back to prev folder. Will work if you are using link
