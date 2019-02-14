#!/bin/bash

config_location="/var/tmp/quandenser_pipeline_$USER"
GREEN="\033[0;92m"
RED="\033[0;31m"
BLUE="\033[0;34m"
YELLOW="\033[0;93m"
RESET="\033[0m\n"

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
    echo ""  # Empty row
    printf "${GREEN}Quandenser-pipeline HELP$RESET"
    printf "Usage:\n"
    printf "${BLUE}./Open_UI.sh <path_to_mount>$RESET"
    exit 0
  fi
done

# Go to dir where the script lies, this allows for links to work
cd "$(dirname "$0")"

# Check if nvidia is installed
{
  nvidia-smi | grep -q "Driver" && graphics=" --nv"
} || { # catch
  printf "${YELLOW}No nvidia drivers detected. Will use prebuilt drivers instead ${RESET}"
  graphics=""
}

# Check if singularity is installed
{
  singularity --version | grep -q "version" && :
} || { # catch
  while true; do
    printf "${GREEN}Singularity is not installed. Y/y to install (requires sudo privileges) or N/n to cancel ${RESET}"
    read accept
    if [ "$accept" = "y" ] || [ "$accept" = "Y" ]; then
      # NOTE: it should be possible to install for just user (aka without sudo)
      # Perhaps in the future, it could be set so singularity is only installed for user --> no sudo required
      # However, all dependencies, such as squashfs-tools still need to be installed
      printf "${GREEN}Installing Singularity${RESET}"
      {  # try
        sudo apt-get update && \
        sudo apt-get install -y build-essential \
        libssl-dev uuid-dev libgpgme11-dev libseccomp-dev pkg-config squashfs-tools git && \
        export VERSION=1.11.4 OS=linux ARCH=amd64 && \ # change this as you need
        wget -O /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz https://dl.google.com/go/go${VERSION}.${OS}-${ARCH}.tar.gz && \
        sudo tar -C /usr/local -xzf /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz && \
        echo 'export GOPATH=${HOME}/go' >> ~/.bashrc && \
        echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc && \
        export GOPATH=${HOME}/go && \
        export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin && \
        source ~/.bashrc && \
        mkdir -p ${GOPATH}/src/github.com/sylabs && \
        cd ${GOPATH}/src/github.com/sylabs && \
        git clone https://github.com/sylabs/singularity.git && \
        cd singularity && \
        cd ${GOPATH}/src/github.com/sylabs/singularity && \
        ./mconfig && \
        cd ./builddir && \
        make && \
        sudo make install && \
        printf "${GREEN}Singularity successfully installed${RESET}"
      } || { # catch
        printf "${RED}Singularity failed to install. Do you have root access? ${RESET}"
        exit 1
      }
      break
    elif [ "$accept" = "n" ] || [ "$accept" = "N" ]; then
      printf "${RED}Singularity will not installed. Exiting... ${RESET}"
      exit 0
    else
      printf "${RED}Not a valid command${RESET}"
    fi
  done
}

if [ ! -f SingulQuand.SIF ]; then
  while true; do
    printf "${YELLOW}Singularity container not found. Install stable from Singularity Hub? Y/y or N/n${RESET}"
    read accept
    if [ "$accept" = "y" ] || [ "$accept" = "Y" ]; then
      printf "${GREEN}Installing Singularity container${RESET}"
      {  # try
        singularity pull SingulQuand.SIF shub://statisticalbiotechnology/quandenser-pipeline && \
        printf "${GREEN}Singularity container successfully installed${RESET}"
      } || {
        printf "${RED}Downloading the container failed${RESET}"
        exit 1
      }
      break
    elif [ "$accept" = "n" ] || [ "$accept" = "N" ]; then
      printf "${RED}The Singularity container will not installed. Exiting... ${RESET}"
      exit 0
    else
      printf "${RED}Not a valid command${RESET}"
    fi
  done
fi

if (( $EUID == 0 )); then
    printf "${YELLOW}You are running as root. Please run the script again as user${RESET}"
    exit 0
fi

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
  printf "${YELLOW}PIPE not found. It will be created when running the GUI${RESET}"
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
    nohup $config_location/run_quandenser.sh & disown
    pid=$!
    PIPE_write "pid" $pid  # Write pid to pipe
  elif [ "$result" = "1" ]; then
    break
  elif [ "$result" = "2" ]; then
    crash_count=$crash_count+1
    printf "${RED}Crash count: $crash_count, will continue until 3 crashes${RESET}"
    if [ $crash_count -gt 3 ]; then
      printf "${RED}The GUI crashed 3 times. Aborting${RESET}"
      printf "${RED}If you are on a cluster, be aware that you need to enable the X11 server ${RESET}"
      printf "${RED}by using the command ssh -X ...${RESET}"
      printf "${RED}Look at the crash log in the console for additonal information${RESET}"
      break
    fi
  fi
done
cd -  # Go back to prev folder. Will work if you are using link
