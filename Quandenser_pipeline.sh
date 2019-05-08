#!/bin/bash
config_location="/home/$USER/.quandenser_pipeline"  # Change depending on mac or linux
GREEN="\033[0;92m"
RED="\033[0;91m"
BLUE="\033[0;94m"
YELLOW="\033[0;93m"
RESET="\033[0m\n"

# Go to dir where the script lies, this allows for links to work
cd "$(dirname "$(realpath "$0")")"

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

# Check for help before doing anything
for var in "$@"
do
  if [ "$var" = "-h" ] || [ "$var" = "--help" ]; then
    echo ""  # Empty row
    printf "${GREEN}Quandenser-pipeline HELP$RESET"
    printf "Usage:\n"
    printf "${BLUE}  ./Quandenser_pipeline.sh <path_to_mount> <options>$RESET"
    printf "Description:\n"
    printf "${BLUE}  Quandenser-pipeline is a tool that combines Quandenser,
  which condenses label-free MS data and Triqler, which finds differentially expressed proteins using both MS1 and MS2 data.
  Quandenser-pipeline streamlines the process, by accepting almost any vendor format alongside a fasta database containing
  proteins, which are then run through a Singularity image containing all the necessary parts to do the analysis.$RESET"
    printf "Custom mounting points:\n"
    printf "${BLUE}  <path_to_mount>
  Full path to custom mounting point. Useful if the directory is not mounted by Singularity by default.
  Example: ./Quandenser_pipeline.sh /media
  This will mount the directory /media to the container. Note that mounting directories such as /usr or /var can have unforseen consequenses$RESET"
    printf "Optional options:\n"
    printf "${BLUE}  -D or --disable-opengl\t This will disable opengl. Can be useful if the program crashes when switching to Edit Workflow or About tab (will persist through runs)$RESET"
    printf "${BLUE}  -E or --enable-opengl\t\t This will enable opengl, if you have disabled it before (will persist through runs)$RESET"
    printf "${BLUE}  -U or --disable-update\t This will disable checking for updates$RESET"
    printf "${BLUE}  -N or --disable-nvidia\t Disable using nvidia drivers (useful if you are running on a cluster with NVIDIA cards from a computer without NVIDIA drivers)$RESET"
    exit 0
  fi
done

# Check if nvidia is installed
{
  nvidia-smi | grep -q "Driver" && graphics=" --nv"
} || { # catch
  printf "${YELLOW}No nvidia drivers detected. Will use prebuilt drivers instead ${RESET}"
  graphics=""
}

# Check if singularity is installed
{
  singularity --version && :
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

# Check if the image is installed
if [ ! -f SingulQuand.SIF ]; then
  while true; do
    printf "${YELLOW}By downloading and using the pipeline, you are agreeing to the license of Quandenser pipeline and the proteowizard licenses found at this url: ${BLUE}http://proteowizard.sourceforge.net/licenses.html${RESET}"
    printf "${YELLOW}Singularity container not found. Install stable from Singularity Hub? ${GREEN}Y/y ${YELLOW}or ${RED}N/n${RESET}"
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

# Check mount points made by the user
mount_point=" --bind /mnt:/mnt"  # Always start with mounting "mnt" directory
directories=" /mnt"
for var in "$@"; do
  if [[ -d $var ]]; then  # If it is a path, add it to mount list
    mount_point+=" --bind $var:$var"
    directories+=" $var"  # This is only used when the pipeline is restarted
  fi
done

# Check if user has disabled updates or not
disable_update="false"
for var in "$@"; do
  if [ "$var" = "-U" ] || [ "$var" = "--disable-update" ]; then
    disable_update="true"
  fi
done

# Check for updates
if [ "$disable_update" == "false" ]; then
  # Check image version on singularity hub
  VERSION_SINGHUB=$(GET http://singularity-hub.org/api/container/details/statisticalbiotechnology/quandenser-pipeline/ | jq -r '.metrics.inspect' | grep -m 1 -oP 'VERSION=\\"\K([^"\\]*)')
  # Check version in container. Superimportant: pipe stdin from singularity to dev/null. Otherwise, suspended tty input and it runs in background
  VERSION_SIF=$(</dev/null singularity run SingulQuand.SIF / | grep -oP ' \K(v[0-9]+[.][0-9]+)')
  if [[ "$VERSION_SINGHUB" != *"."* ]]; then
    printf "${YELLOW}Unable connect to SingularityHub. Either a new version is being published or SingularityHub is not reachable at the moment${RESET}"
  elif [ "$VERSION_SINGHUB" != "$VERSION_SIF" ]; then
    while true; do
      printf "${YELLOW}A new update has been found ($VERSION_SIF -> $VERSION_SINGHUB). Do you want to install it? ${GREEN}Y/y ${YELLOW}or ${RED}N/n. ${BLUE}R/r${YELLOW} to read the changelog${RESET}"
      read accept
      if [ "$accept" = "y" ] || [ "$accept" = "Y" ]; then
        singularity pull -F SingulQuand.SIF shub://statisticalbiotechnology/quandenser-pipeline
        curl -s https://api.github.com/repos/statisticalbiotechnology/quandenser-pipeline/releases/latest \
        | jq --raw-output '.assets[0] | .browser_download_url' \
        | xargs wget -O $(basename $0) \
        && chmod 744 $(basename $0) \
        && printf "${GREEN}Installation successfully. Restarting Quandenser_pipeline${RESET}" \
        && $0 $directories && exit
      elif [ "$accept" = "n" ] || [ "$accept" = "N" ]; then
        printf "${YELLOW}Skipping update${RESET}"
        break
      elif [ "$accept" = "R" ] || [ "$accept" = "r" ]; then
        curl -s https://api.github.com/repos/statisticalbiotechnology/quandenser-pipeline/releases/latest curl -s https://api.github.com/repos/statisticalbiotechnology/quandenser-pipeline/releases/latest | jq --raw-output '.body'
      else
        printf "${RED}Not a valid command${RESET}"
      fi
    done
  else
    printf "${GREEN}Quandenser-pipeline is up to date ($VERSION_SIF)${RESET}"
  fi
fi

if (( $EUID == 0 )); then
    printf "${YELLOW}You are running as root. Please run the script again as user${RESET}"
    exit 0
fi

# Initialize pipe before trying to write, this will be automacially done with the GUI as well
# However, doing it here will allow users to add parameters without having to run and close the GUI
# The GUI will work without this
singularity exec --app quandenser_ui SingulQuand.SIF  python -c "from utils import check_corrupt; check_corrupt('${config_location}')"

# Check for more user commands and write to PIPE that has now been created
for var in "$@"; do
  if [ "$var" = "--disable-opengl" ] || [ "$var" = "-D" ]; then  # Check if user wants to disable opengl, will remember it for next time
    PIPE_write "disable-opengl" "true"
  elif [ "$var" = "--enable-opengl" ] || [ "$var" = "-E" ]; then  # Check if user wants to enable opengl
    PIPE_write "disable-opengl" "false"
  elif [ "$var" = "--disable-nvidia" ] || [ "$var" = "-N" ]; then  # Check if user wants to disable nvidia drivers
    graphics=""
  fi
done

# Mandatory PIPE writes
if [ -f $config_location/PIPE ]; then
  PIPE_write "custom_mounts" "$mount_point"
  PIPE_write "exit_code" "2"
  PIPE_write "pwd" "$(pwd)"  # Add the current location of the SIF file, which will be used to browse files
else
  printf "${YELLOW}PIPE not found. It will be created when running the GUI${RESET}"  # You should never get here
fi

# Initialize parameters as integer
declare -i crash_count=0

# Main loop
while true; do
  singularity run --app quandenser_ui --bind $(pwd):$(pwd)$mount_point$graphics SingulQuand.SIF  # All parameters have to be close
  wait
  result=$(read_command)
  if [ "$result" = "0" ]; then
    crash_count=0  # Reset
    PIPE_write "exit_code" "2"  # Write pid to pipe
    PIPE_write "started" "true"
    nohup $config_location/run_quandenser.sh </dev/null >/dev/null 2>&1 & disown
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
      printf "${RED}Look at the crash log in the console for additional information${RESET}"
      break
    fi
  fi
done
cd -  # Go back to prev folder. Will work if you are using link
