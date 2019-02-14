# Quandenser-pipeline <img align='right' src="/images/logo.png"  width="50" height="50">

## A Nextflow/Singularity pipeline for Quandenser

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/2356)

## How to install
Go to releases and download ''Quandenser_pipeline.sh'' and run the shell script. The shell script will handle the rest!

## Usage
Go to the directory where ''Quandenser_pipeline.sh'' is installed and run the command

    ./Quandenser_pipeline.sh

This will install Singularity if it does not exist (this requires sudo privileges). The script will also download the latest stable version of the Singularity image.

If you want to mount another directory that is not detected by Singularity, you can add any amount of directories to mount by these commands:

    ./Quandenser_pipeline.sh /path/to/directory1 /path/to/directory2


The pipeline can be run on a SLURM cluster if Singularity is installed. Just don't forget to enable "slurm_cluster" in the
settings!


## Description
Quandenser-pipeline is a tool to analyze label-free MS data, from (almost) any vendor format alongside a fasta
database with proteins to .tsv files containing which proteins are in the sample + a lot of other parameters.
The aim of the pipeline is to streamline the process from using proteome MS files to actual results.

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


<img src="/images/logo.png"  width="128" height="128">
 <small>&copy; Copyright 2019, Timothy Bergström</small>
