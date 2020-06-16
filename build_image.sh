#!/bin/bash
# Note, You can change the tmpdir to another location
#sudo SINGULARITY_TMPDIR=/tmp singularity build SingulQuand.SIF Singularity

docker build -t matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses:latest .
