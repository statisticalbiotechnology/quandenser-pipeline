# Quandenser-pipeline <img align='right' src="/images/logo.png" height="50">

## A Nextflow/Singularity pipeline for Quandenser

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/2356)

## How to install
Go to releases and download *Quandenser_pipeline.sh* and run the shell script. The shell script will handle the rest!

## Usage
Go to the directory where *Quandenser_pipeline.sh* is installed and run the command

    ./Quandenser_pipeline.sh

This will install Singularity if it does not exist (this requires sudo privileges). The script will also download the latest stable version of the Singularity image.

If you want to mount another directory that is not detected by Singularity, you can add any amount of directories to mount by these commands:

    ./Quandenser_pipeline.sh /path/to/directory1 /path/to/directory2


The pipeline can be run on a SLURM cluster if Singularity is installed. Just don't forget to enable "slurm_cluster" in the
settings!

**If you have trouble running the GUI, look further down below in the section "Known Issues"**

## Description
*Quandenser-pipeline* is a tool that combines *Quandenser*, a tool which condenses label-free MS data and *Triqler*, a tool which finds differentially expressed proteins using both MS1 and MS2 data. *Quandenser-pipeline* streamlines the process, by accepting almost any vendor format alongside a fasta database containing proteins, which are then run through a Singularity image containing all the necessary parts to do the analysis.

<img src="/images/gui.png" width="1000" height="800">


[Singularity](https://github.com/sylabs/singularity): Singularity is an open source container platform used to embed the software used in the pipeline


[Nextflow](https://github.com/nextflow-io/nextflow): Nextflow is a workflow manager, which was used to create the pipeline


[Quandenser](https://github.com/statisticalbiotechnology/quandenser): A recent software which condenses quantification data from label-free mass spectrometry experiments, written by Lukas Käll and Matthew The at ScilifeLab


[Crux toolkit](https://github.com/crux-toolkit/crux-toolkit): An open-source mass spectrometry analysis toolkit used to analyse MS2 spectra from Quandeser


[Triqler](https://github.com/statisticalbiotechnology/triqler): A combined identification and quantification error model of label-free protein quantification, written by Lukas Käll and Matthew The at ScilifeLab. It is used as the final analysis software, utilizing the output from Crux and Quandenser

The GUI is built with the open source GUI [PySide2](https://pypi.org/project/PySide2/)
with [ColinDuqesnoy's dark theme](https://github.com/ColinDuquesnoy/QDarkStyleSheet)


## Known issues

>*** stack smashing detected***: python terminated

Sometimes when running on a computer with nvidia drivers locally, this error message will be shown. It will not harm your computer, so just keep trying to start the program. Usually, it stabilizes after a couple of runs.
I've been trying to find the cause of this bug, but it seems to be correlated to the creation of the GUI window through Singularity. If you have any ideas about the bug, please let me know!


>WebEngineContext used before QtWebEngine::initialize() or OpenGL context creation failed.

This usually happens when you are running on a cluster. Sometimes, the nvidia drivers on your computer is not compatible
with the drivers on the cluster. Please add the following command when running the start script.
Note: disabling opengl will not hinder the performance of the software. The workflow display and the about tab will
not be shown.

    ./Quandenser_pipeline.sh /path/to/directory1 ... --disable-opengl


>Glx related crashes (ex qt.glx: qglx_findConfig: Failed to finding matching FBConfig (8 8 8 0))

If you are running on a cluster with nvidia cards and you do not have an nvidia card on your local machine (ex if you are running the software in virtualbox on a cluster). Add the following command to disable nvidia drivers

    ./Quandenser_pipeline.sh /path/to/directory1 ... --disable-nvidia

**If everything fails and you can't get it to work, there is one last thing you can try, which is explained below ...**

## Running the pipeline WITHOUT the GUI

If everything fails or you can't run the GUI for some reason, there is a last resort which you can use: run the pipeline without the GUI. This is not as intuitive as using the GUI, but it is possible to do, since the GUI in itself is not required to run the pipeline but it only makes things easier. Do the following to run the pipeline without GUI:

1. Remove the directory *.quandenser_pipeline* from your home directory. Run the command `rm -r /home/$USER/.quandenser_pipeline`. This will clear previous settings that might interfere.

2. Run `./Quandenser_pipeline.sh` as usual. You should see *Missing file <file>. Installing file* in yellow text on the terminal. This will add the configuration files. At this point, it doesn't matter if the GUI crashes or not.

3. Go to the config directory with `cd /home/$USER/.quandenser_pipeline`

4. The files **nf.config** and **run_quandenser** are the only files which you will need to edit to make this work.
 - **run_quandenser.sh**: Here, the only parameters you need to edit are:
    - *PROFILE* = Can be either *local* or *cluster*
    - *OUTPUT_PATH* = The full path to the directory where the output will be placed.
  - **nf.config**: Here, pretty much any variable can be changed. However, I would suggest to focus on:
    - *params.db* = Path to the fasta file used as the protein database. Note that only the "Full" workflow requires this.
    - *params.output_path* = Output path, which needs to be the same as the output path in the .sh file
    - *params.batch_file* = Path to the batch file. The syntax of the batch file is:
    `/full/path/to/ms/file label` where "label" could be any combination of ascii characters. Note that the delimiter between the file path and the label needs to be a tab character. For each file, add another row. Replicates should have the same label assigned.
    - *params.custom_mounts* = Custom mounts used for Nextflow. the syntax should be:
    ` --bind /path/to/mount:/path/to/mount`. Note the blank space before " --bind"
    - *params.workflow* = Can be "Full", "MSconvert" or "Quandenser"
    - *params.resume_directory* = Path to another directory containing previously calculated quandenser files
    - *time parameters* = If you are running on a cluster and are using the "cluster" profile, adjust the time values to your liking.


5. Go back to the directory containing *SingulQuand.SIF* and run this command:
`nohup /home/$USER/run_quandenser.sh </dev/null >/dev/null 2>&1 & disown`
This should run the sh file, deattach it from the terminal and run it in the background. This will allow you to close the terminal/ssh session without stopping the pipeline.

## Building from scratch

If you have come all the way down here in the README, you might be interested in building the image from scratch.

Simply clone the repository with git or download it [here](https://github.com/statisticalbiotechnology/quandenser-pipeline/archive/master.zip). Unzip the directory and cd inside, then run "./build_image.sh" and it will build everything for you! (However, this requires both Singularity and sudo privileges, so run the release first to install Singularity)

## Questions?

Feel free to mail me at "timothy.bergstrom@gmail.com" if you have any questions about quandenser-pipeline.



<img src="/images/logo.png" height="128">
 <small>&copy; Copyright 2019, Timothy Bergström</small>
