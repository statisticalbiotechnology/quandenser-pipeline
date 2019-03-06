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


>Glx related crashes

If you are running on a cluster with nvidia cards and you do not have an nvidia card on your local machine (ex if you are running the software in virtualbox on a cluster). Add the following command to disable nvidia drivers

    ./Quandenser_pipeline.sh /path/to/directory1 ... --disable-nvidia


## Description
*Quandenser-pipeline* is a tool that combines *Quandenser*, a tool which condenses label-free MS data and *Triqler*, a tool which finds differentially expressed proteins using both MS1 and MS2 data. *Quandenser-pipeline* streamlines the process, by accepting almost any vendor format alongside a fasta database containing proteins, which are then run through a Singularity image containing all the necessary parts to do the analysis.



<img src="/images/gui.png" width="1000" height="800">


[Singularity](https://github.com/sylabs/singularity)


[Nextflow](https://github.com/nextflow-io/nextflow)


[Quandenser](https://github.com/statisticalbiotechnology/quandenser)


[Crux toolkit](https://github.com/crux-toolkit/crux-toolkit)


[Triqler](https://github.com/statisticalbiotechnology/triqler)

The GUI is built with the open source GUI [PySide2](https://pypi.org/project/PySide2/)
with [ColinDuqesnoy's dark theme](https://github.com/ColinDuquesnoy/QDarkStyleSheet)


## Building from scratch

If you have come all the way down here in the README, you might be interested in building the image from scratch.

Simply clone the repository with git or download it [here](https://github.com/statisticalbiotechnology/quandenser-pipeline/archive/master.zip). Unzip the directory and cd inside, then run "./build_image.sh" and it will build everything for you! (However, this requires both Singularity and sudo privileges, so run the release first to install Singularity)


<img src="/images/logo.png" height="128">
 <small>&copy; Copyright 2019, Timothy Bergström</small>
