# Quandenser-pipeline
## A Nextflow/Singularity pipeline for Quandenser
[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/2356)

## How to install
Go to releases and download "Quandenser_pipeline.sh" and run the shell script. The shell script will handle the rest!

## Usages
Quandenser-pipeline is a tool to analyze label-free MS data, from (almost) any vendor format alongside a fasta
database with proteins to .tsv files containing which proteins are in the sample + a lot of other parameters.
The aim of the pipeline is to streamline the process from using proteome MS files to actual results.

<img src="/images/gui.png" width="1000" height="800">


The pipeline can be run on a cluster with both SLURM and Singularity installed. Just don't forget to enable it in the
settings!


## Description
[Singularity](https://github.com/sylabs/singularity)


[Nextflow](https://github.com/nextflow-io/nextflow)


[Quandenser](https://github.com/statisticalbiotechnology/quandenser)


[Crux toolkit](https://github.com/crux-toolkit/crux-toolkit)


[Triqler](https://github.com/statisticalbiotechnology/triqler)

The GUI is built with the open source GUI [PySide2](https://pypi.org/project/PySide2/)
with [ColinDuqesnoy's dark theme](https://github.com/ColinDuquesnoy/QDarkStyleSheet)

<img src="/images/logo.png"  width="128" height="128">
