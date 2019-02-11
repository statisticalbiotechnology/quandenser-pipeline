#!/bin/bash

config_location="/var/tmp/quandenser_pipeline_$USER"

function PIPE_read() {
  # grep: -o, only get match, cut: -d'=' deliminter and get second column, tr: clear carriage return
  value=$(grep -o "$1=.*" "$config_location/PIPE" | cut -d'=' -f2 | tr -d '\r')
  echo $value
}

function PIPE_write() {
  parameter="$1=.*"
  value="$1=$2"
  # sed: -i overwrite in file, -E = regular expressions
  sed -i -E "s|${parameter}|${value}|g" "$config_location/PIPE"
}

function read_command() {
  exit_code=$(PIPE_read "exit_code")
  # Exit codes:
  # 0 = run button pressed --> run the nextflow pipeline
  # 1 = soft exit, closed window --> Do not run anything
  # 2 = hard exit, python crashed --> Rerun 3 times and stop if not working
  echo $exit_code
}


# Check for help
for var in "$@"
do
  if [ "$var" = "-h" ] || [ "$var" = "--help" ]; then
    printf "\033[1;92mQuandenser-pipeline \033[0m\n"
    printf "Usage:\n"
    printf "\033[0;34m./Open_UI.sh <path_to_mount> \033[0m\n"
    exit 0
  fi
done

# Go to dir where the script lies, this allows for links to work
cd "$(dirname "$0")"

{ # try
  nvidia-smi | grep -q "Driver" && graphics=" --nv"  # Check if nvidia is installed
} || { # catch
  graphics=""
}

# Initialize parameters
declare -i crash_count=0
mount_point=""
for var in "$@"
do
  mount_point+=" --bind $var:$var"
done
if [ -f $config_location/PIPE ]; then
  PIPE_write "custom_mounts" "$mount_point"
else
  echo "PIPE not found. It will be created when running the GUI"
fi
if [ -f $config_location/PIPE ]; then
  PIPE_write "exit_code" "2"  # Write pid to pipe
fi

while true; do
  singularity run --app quandenser_ui --bind $(pwd):$(pwd)$mount_point$graphics SingulQuand.SIF
  wait
  result=$(read_command)
  if [ "$result" = "0" ]; then
    crash_count=0  # Reset
    PIPE_write "exit_code" "2"  # Write pid to pipe
    PIPE_write "started" "true"
    #chmod u+x /var/tmp/quandenser_pipeline_$USER/nextflow  # Fix permission
    #chmod u+x /var/tmp/quandenser_pipeline_$USER/run_quandenser.sh  # Fix permission
    nohup $config_location/run_quandenser.sh & disown
    pid=$!
    PIPE_write "pid" $pid  # Write pid to pipe
  elif [ "$result" = "1" ]; then
    break
  elif [ "$result" = "2" ]; then
    crash_count=$crash_count+1
    echo "Crash count: $crash_count, will continue until 3 crashes"
    if [ $crash_count -gt 3 ]; then
      echo "The GUI crashed 3 times. Aborting"
      break
    fi
  fi
done
cd -  # Go back to prev folder. Will work if you are using link
