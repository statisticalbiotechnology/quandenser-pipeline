#!/bin/bash
config_location="/home/$USER/.quandenser_pipeline"  # Change depending on mac or linux
GREEN="\033[0;92m"
RED="\033[0;91m"
BLUE="\033[0;94m"
YELLOW="\033[0;93m"
RESET="\033[0m\n"

# Go to dir where the script lies, this allows for links to work
export SCRIPTDIR="$(dirname "$(realpath "$0")")"
#cd "$SCRIPTDIR"

disable_update="false"
gui_free_installation="false"
use_docker="false"
read_config_location="false"
directories=()

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
  proteins, which are then run through a Docker/Singularity image containing all the necessary parts to do the analysis.$RESET"
    printf "Custom mounting points:\n"
    printf "${BLUE}  <path_to_mount>
  Full path to custom mounting point. Useful if the directory is not mounted by Singularity by default.
  Example: ./Quandenser_pipeline.sh /media
  This will mount the directory /media to the container. Note that mounting directories such as /usr or /var can have unforeseen consequenses$RESET"
    printf "Optional options:\n"
    printf "${BLUE}  -L or --gui-free-installation\tInstall scripts in current directory to run quandenser w/o gui, and exit.$RESET"
    printf "${BLUE}  -d or --with-docker\tUse Docker instead of Singularity.$RESET"
    printf "${BLUE}  -C or --config-dir\tDirectory where configuration files will be stored (default: /home/$USER/.quandenser_pipeline).$RESET"
    printf "${BLUE}  -D or --disable-opengl\t This will disable opengl. Can be useful if the program crashes when switching to Edit Workflow or About tab (will persist through runs)$RESET"
    printf "${BLUE}  -E or --enable-opengl\t\t This will enable opengl, if you have disabled it before (will persist through runs)$RESET"
    printf "${BLUE}  -U or --disable-update\t This will disable checking for updates$RESET"
    printf "${BLUE}  -N or --disable-nvidia\t Disable using nvidia drivers (useful if you are running on a cluster with NVIDIA cards from a computer without NVIDIA drivers)$RESET"
    exit 0
  elif [ "$var" = "--with-docker" ] || [ "$var" = "-d" ]; then  
    # Check if user wants to install local scripts
    use_docker="true"
  elif [ "$var" = "--config-dir" ] || [ "$var" = "-C" ]; then  
    # Check if user wants to install local scripts
    read_config_location="true"
  elif [ "$read_config_location" = "true" ]; then
    read_config_location="changed"
    if [[ -d $var ]]; then  # If it is an existing path, set it
      config_location=$(realpath "$var")
    else
      printf "$var is not a directory, do you want to create it? [y/n]"
      read accept
      if [ "$accept" = "y" ] || [ "$accept" = "Y" ]; then
        mkdir -p $var 
        config_location=$(realpath "$var")
      else
        printf "${RED}No valid config directory set. Exiting... ${RESET}"
        exit 1
      fi
    fi
  elif [ "$var" = "--gui-free-installation" ] || [ "$var" = "-L" ]; then  
    # Check if user wants to install local scripts
    gui_free_installation="true"
  elif [ "$var" = "--disable-update" ] || [ "$var" = "-U" ]; then 
    # Check if user has disabled updates or not
    disable_update="true"
  elif [[ -d $var ]]; then  # If it is a path, add it to mount list
    directories+=($var)
  fi
done

mount_point=""  # Always start with mounting "mnt" directory
for directory in directories; do
  # Check mount points made by the user
  if [ "$use_docker" == "true" ]; then
    mount_point+=" -v $var:$var"
  else
    mount_point+=" --bind $var:$var"
  fi
done

if [[ -d $config_location ]]; then  # If it is an existing path, set it
  printf "${GREEN}Using $config_location as config dir ${RESET}"  
else
  printf "${GREEN}$config_location is not a directory, do you want to create it? [y/n] ${RESET}"
  read accept
  if [ "$accept" = "y" ] || [ "$accept" = "Y" ]; then
    mkdir -p $config_location 
  else
    printf "${RED}No valid config directory set. Exiting... ${RESET}"
    exit 1
  fi
fi


# Check if nvidia is installed
{
  nvidia-smi | grep -q "Driver" && graphics=" --nv"
} || { # catch
  printf "${YELLOW}No nvidia drivers detected. Will use prebuilt drivers instead ${RESET}"
  graphics=""
}

# Check if docker/singularity is installed
if [ "$use_docker" == "true" ]; then
  if [[ "$(systemctl is-active docker)" != "active" ]]; then
    printf "${GREEN}Docker daemon is not running. Exiting...${RESET}"
    exit 1
  else
    mount_point+=" -u $(id -u):$(id -g)"
  fi
else
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
          libssl-dev uuid-dev libgpgme11-dev libseccomp-dev pkg-config squashfs-tools git cryptsetup && \
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
          export SINGULARITYVERSION=3.4.1 && \
          wget https://github.com/sylabs/singularity/releases/download/v${SINGULARITYVERSION}/singularity-${SINGULARITYVERSION}.tar.gz && \
          tar -xzf singularity-${SINGULARITYVERSION}.tar.gz && \
          # git clone https://github.com/sylabs/singularity.git && \
          cd singularity && \
          cd ${GOPATH}/src/github.com/sylabs/singularity && \
          ./mconfig && \
          cd ./builddir && \
          make && \
          sudo make install && \
          cd "$SCRIPTDIR" && \
          printf "${GREEN}Singularity successfully installed${RESET}"
        } || { # catch
          printf "${RED}Singularity failed to install. Do you have root access? ${RESET}"
          exit 1
        }
        break
      elif [ "$accept" = "n" ] || [ "$accept" = "N" ]; then
        printf "${RED}Singularity will not be installed. Exiting... ${RESET}"
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
  
  # Check for updates
  if [ "$disable_update" == "false" ]; then
    # Check image version on singularity hub
    #VERSION_SINGHUB=$(GET http://singularity-hub.org/api/container/details/statisticalbiotechnology/quandenser-pipeline/ | jq -r '.metrics.inspect' | grep -m 1 -oP 'VERSION=\\"\K([^"\\]*)')
    VERSION_SINGHUB=$(curl -s https://api.github.com/repos/statisticalbiotechnology/quandenser-pipeline/releases/latest \
    | jq --raw-output '.tag_name')
    # Check version in container. Superimportant: pipe stdin from singularity to /dev/null. Otherwise, suspended tty input and it runs in background
    VERSION_SIF=$(</dev/null singularity run $mount_point SingulQuand.SIF / | grep -oP ' \K(v[0-9]+[.][0-9]+)')
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
          && $0 "$@" && exit
        elif [ "$accept" = "n" ] || [ "$accept" = "N" ]; then
          printf "${YELLOW}Skipping update${RESET}"
          break
        elif [ "$accept" = "R" ] || [ "$accept" = "r" ]; then
          curl -s https://api.github.com/repos/statisticalbiotechnology/quandenser-pipeline/releases/latest | jq --raw-output '.body'
        else
          printf "${RED}Not a valid command${RESET}"
        fi
      done
    else
      printf "${GREEN}Quandenser-pipeline is up to date ($VERSION_SIF)${RESET}"
    fi
  fi
fi

if [ "$gui_free_installation" == "true" ]; then # Check if user wants to install local scripts and exit
  mkdir -p ./out
  
  #base_url="/home/matthewt/storage/quandenser-pipeline/dependencies/ui/config/"
  #cp $base_url/run_quandenser.sh ./
  #cp $base_url/run_quandenser.nf ./
  #cp $base_url/nextflow ./
  #cp $base_url/nf.config ./out/
  
  base_url="https://raw.githubusercontent.com/statisticalbiotechnology/quandenser-pipeline/master/dependencies/ui/config/"
  wget -q $base_url/run_quandenser.sh
  wget -q $base_url/run_quandenser.nf
  wget -q $base_url/nextflow
  wget -qO ./out/nf.config $base_url/nf.config
  
  chmod a+x run_quandenser.sh
  chmod a+x nextflow
  if [ ! -f file_list.txt ]; then
    echo -e "file1.mzML\tcase\nfile2.mzML\tcase\nfile3.mzML\tcontrol\nfile4.mzML\tcontrol" > file_list.txt
  fi
  
  if [ "$read_config_location" == "changed" ]; then
    sed -i "s|CONFIG_LOCATION=\"\"|CONFIG_LOCATION=\"${config_location}\"|g" run_quandenser.sh
  else
    sed -i 's|CONFIG_LOCATION=""|CONFIG_LOCATION=`pwd`|g' run_quandenser.sh
  fi
  sed -i 's|OUTPUT_PATH=""|export OUTPUT_PATH=`pwd`/out|g' run_quandenser.sh
  if [ "$use_docker" == "true" ]; then
    sed -i 's|USE_DOCKER="false"|USE_DOCKER="true"|g' run_quandenser.sh
  fi
  sed -i 's|NF_CONFIG_LOCATION="$CONFIG_LOCATION/nf.config"|NF_CONFIG_LOCATION="$OUTPUT_PATH/nf.config"|g' run_quandenser.sh
  
  sed -i "s|params.custom_mounts=\"\"|params.custom_mounts=\"$mount_point\"|g" ./out/nf.config
  sed -i 's|params.output_path=""|params.output_path="$OUTPUT_PATH"|g' ./out/nf.config
  sed -i 's|params.batch_file=""|params.batch_file="file_list.txt"|g' ./out/nf.config
  
  printf "${YELLOW}Installed scripts in current working directory.${RESET}"
  printf "${YELLOW}Please configure scripts by editing out/nf.config and run_quandenser.sh.${RESET}"
  printf "${YELLOW}You will also need to edit the tab-delimited file, file_list.txt, specifying "
  printf "the files you want to process and their sample group.${RESET}"
  printf "${YELLOW}You will then be able to run the pipleline with run_quandenser.sh${RESET}"
  exit 0
fi

if (( $EUID == 0 )); then
  printf "${YELLOW}You are running as root. Please run the script again as a regular user${RESET}"
  exit 0
fi

export QUANDENSER_CONFIG_PATH=$config_location

# Initialize pipe before trying to write, this will be automatically done with the GUI as well
# However, doing it here will allow users to add parameters without having to run and close the GUI
# The GUI will work without this
if [ "$use_docker" == "true" ]; then
  docker run $mount_point -v $HOME:$HOME -e QUANDENSER_CONFIG_PATH=$config_location matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses -c "from utils import check_corrupt; check_corrupt('${config_location}')"
else
  singularity exec --app quandenser_ui $mount_point SingulQuand.SIF python -c "from utils import check_corrupt; check_corrupt('${config_location}')"
fi

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

# Check for more user commands and write to PIPE that has now been created
for var in "$@"; do
  if [ "$var" = "--disable-opengl" ] || [ "$var" = "-D" ]; then  # Check if user wants to disable opengl, will remember it for next time
    PIPE_write "disable-opengl" "true"
    printf "${YELLOW}OpenGL disabled${RESET}"
  elif [ "$var" = "--enable-opengl" ] || [ "$var" = "-E" ]; then  # Check if user wants to enable opengl
    PIPE_write "disable-opengl" "false"
    printf "${YELLOW}OpenGL enabled${RESET}"
  elif [ "$var" = "--disable-nvidia" ] || [ "$var" = "-N" ]; then  # Check if user wants to disable nvidia drivers
    graphics=""
    printf "${YELLOW}Nvidia drivers disabled${RESET}"
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
  # launch GUI
  if [ "$use_docker" == "true" ]; then
    docker run -e DISPLAY=${DISPLAY} -e QUANDENSER_CONFIG_PATH=$config_location $mount_point -v $HOME:$HOME -v /tmp/.X11-unix/:/tmp/.X11-unix matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses
  else
    singularity run --app quandenser_ui --bind $(pwd):$(pwd)$mount_point$graphics SingulQuand.SIF  # All parameters have to be close
  fi
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
