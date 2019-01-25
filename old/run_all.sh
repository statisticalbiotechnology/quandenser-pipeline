#!/bin/bash
sudo singularity build singulqand.simg Singularity
# curl -s https://get.nextflow.io | bash
# ./nextflow main.nf -with-singularity singulqand.simg
nextflow main.nf -with-singularity singulqand.simg
