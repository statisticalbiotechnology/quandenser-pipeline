#!/bin/bash
config_location="/home/$USER/.quandenser_pipeline"  # Change depending on mac or linux
GREEN="\033[0;92m"
RED="\033[0;31m"
BLUE="\033[0;34m"
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
    printf "${BLUE}  ./Open_UI.sh <path_to_mount>$RESET"
    echo ""  # Empty row
    printf "Description:\n"
    printf "${BLUE}  PLACEHOLDER$RESET"
    printf "Options:\n"
    printf "${BLUE}  --disable-opengl\t This will disable opengl. Can be useful if the program crashes when switching to Edit Workflow or About tab$RESET"
    printf "${BLUE}  --enable-opengl\t This will enable opengl. Can be used when the user has disabled opengl and wants to reset$RESET"
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

# Initialize pipe before trying to write, this will be automacially done with the GUI as well
# However, doing it here will allow users to add parameters without having to run and close the GUI
# The GUI will work without this
singularity exec --app quandenser_ui SingulQuand.SIF  python -c "from utils import check_corrupt; check_corrupt('${config_location}')"

# Check arguments
mount_point=""
for var in "$@"
do
  if [[ -d $var ]]; then  # If it is a path, add it to mount list
    mount_point+=" --bind $var:$var"
  elif [[ "$var" = "--disable-opengl" ]]; then  # Check if user wants to disable opengl, will remember it for next time
    PIPE_write "disable-opengl" "true"
  elif [[ "$var" = "--enable-opengl" ]]; then  # Check if user wants to enable opengl
    PIPE_write "disable-opengl" "false"
  elif [[ "$var" = "--disable-nvidia" ]]; then  # Check if user wants to disable nvidia drivers
    graphics=""
  fi
done

if [ -f $config_location/PIPE ]; then
  PIPE_write "custom_mounts" "$mount_point"
  PIPE_write "exit_code" "2"
  PIPE_write "pwd" "$(pwd)"  # Add the current location of the SIF file, which will be used to browse files
else
  printf "${YELLOW}PIPE not found. It will be created when running the GUI${RESET}"  # You should never get here
fi

# Initialize parameters as integer
declare -i crash_count=0

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
